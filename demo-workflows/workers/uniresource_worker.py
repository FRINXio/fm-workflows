import logging
import json
from jinja2 import Template
from python_graphql_client import GraphqlClient
from frinx_conductor_workers.frinx_rest import conductor_headers
from logging_helpers import logging_handler
from util import completed_response, failed_response

log = logging.getLogger(__name__)

uniresource_url = "http://uniresource:8884/query"

client = GraphqlClient(endpoint=uniresource_url, headers=conductor_headers)

claim_resource_template = Template(
    """
    mutation ClaimResource($pool_id: ID!, $description: String!, $user_input: Map!{{ alternative_id_variable }}) {
    {{ claim_resource }}(
        poolId: $pool_id,
        description: $description,
        userInput: $user_input{{ alternative_id }})
    {
        id
        Properties
    }
    }"""
)

create_pool_template = Template(
    """
    mutation CreatePool($pool_name: String!, $resource_type_id: ID!, $resource_type_strat_id: ID!,{{ pool_properties_variables }}) {
    {{ create_pool }}(
        input: {
            resourceTypeId: $resource_type_id,
            poolName: $pool_name,
            allocationStrategyId: $resource_type_strat_id,
            poolDealocationSafetyPeriod: 0,
            {{ pool_properties_types }},
            {{ pool_properties }},
            {{ parent_resource_id }},
            tags: [$pool_name],
        }
    ) {
        pool { id }
    }
    }"""
)

query_pool_template = Template(
    """
    query QueryPool($resource_type_id: ID!) {
    QueryResourcePools(
        tags: { matchesAny: [
            { matchesAll: [{{ pool_names }}] }
            ]
        },
        resourceTypeId: $resource_type_id)
    {
        id
    }
    }"""
)

query_resource_template = Template(
    """
    query QueryId($resource: String) {
    QueryResourceTypes(byName: $resource) {
        id   
    }
    QueryAllocationStrategies(byName: $resource) {
        id
    }
    }"""
)

query_pool_by_tag_template = Template(
    """
    query SearchPools($poolTag: String!) {
    SearchPoolsByTags(tags: { matchesAny: [{matchesAll: [$poolTag]}]}) {
        id
        Name
    }
    } """
)

query_claimed_resource_template = Template(
    """
    query QueryClaimedResource($pool_id: ID!,{{ input_variable }}) {
    {{ query_resource }}(
        poolId: $pool_id,
        {{ input }})
    {
        edges {
            node {
                id
                Properties
                }
            }
        }
    }"""
)

update_alternative_id_for_resource_template = Template(
    """
    mutation UpdateResourceAltId($pool_id: ID!, $input: Map!, $alternative_id: Map!) {
        {{ update_alt_id }}(
        poolId: $pool_id, input: $input, alternativeId: $alternative_id) {
            AlternativeId
        }
    }
    """
)


def execute(body, variables):
    return client.execute(query=body, variables=variables)


@logging_handler(log)
def claim_resource(task, logs):
    """
    Claim resource from Uniresource
    Claim resource can use two types of claims: ClaimResource, ClaimResourceWithAltId.
    For using ClaimResourceWithAltId you have to fill alternativeId in input data

         Args:

             task (dict): dictionary with input data ["poolId", "userInput", "description", "alternativeId"]

             logs: stream of log messages

        Returns:
            Response from uniresource. Worker output format::
            response_body: {
              "data": {
                "<claim_operation>": {
                  "id": "<id>",
                  "Properties": {
                    <properties>
                  }
                }
              }
            }

    """
    pool_id = task["inputData"]["poolId"] if "poolId" in task["inputData"] else None
    if pool_id is None:
        return failed_response("No pool id")
    user_input = (
        task["inputData"]["userInput"] if "userInput" in task["inputData"] else {}
    )
    description = (
        task["inputData"]["description"] if "description" in task["inputData"] else ""
    )
    alternative_id = (
        None
        if "alternativeId" not in task["inputData"]
        else task["inputData"]["alternativeId"]
    )
    variables = {
        "pool_id": pool_id,
        "user_input": user_input,
        "description": description,
    }

    if len(task["inputData"]["alternativeId"]) > 1 and alternative_id is not None:
        alternative_id = alternative_id.replace("'", "\"")
        alternative_id = json.loads(alternative_id)
        variables.update({"alternative_id": alternative_id})
        body = claim_resource_template.render(
            {
                "claim_resource": "ClaimResourceWithAltId",
                "alternative_id_variable": ", $alternative_id: Map!",
                "alternative_id": ", alternativeId: $alternative_id",
            }
        )
    else:
        body = claim_resource_template.render(
            {
                "claim_resource": "ClaimResource",
                "alternative_id_variable": "",
                "alternative_id": "",
            }
        )


    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    response = execute(body, variables)
    if "errors" in response:
        return failed_response({"response_body": response["errors"][0]["message"]})
    return completed_response({"response_body": response["data"]})



@logging_handler(log)
def query_claimed_resources(task, logs):
    """
    Query claimed resources from Uniresource
    Query resource can use two types of claims: QueryResources, QueryResourceWithAltId.
    For using QueryResourceWithAltId you have to fill alternativeId in input data

         Args:

             task (dict): dictionary with input data ["poolId", "alternativeId"]

             logs: stream of log messages

        Returns:
            Response from uniresource. Worker output format::
            response_body: {
              "data": {
                "<query_type>": {
                    edges {
                        node {
                          "id": "<id>",
                          "Properties": {
                            <properties>
                          }
                        }
                    }
                }
              }
            }

    """
    pool_id = task["inputData"]["poolId"] if "poolId" in task["inputData"] else None
    alternative_id = (
        None
        if "alternativeId" not in task["inputData"]
        else task["inputData"]["alternativeId"]
    )
    if pool_id is None:
        return failed_response(logs, "No pool id")
    variables = {"pool_id": pool_id}
    if alternative_id is not None:
        body = query_claimed_resource_template.render(
            {
                "query_resource": "QueryResourcesByAltId",
                "input": "input: $input",
                "input_variable": "$input: Map!",
            }
        )
        variables.update({"input": alternative_id})
    else:
        body = query_claimed_resource_template.render(
            {"query_resource": "QueryResources"}
        )
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    return completed_response({"response_body": data})


def query_resource_id(resource):
    # Query resource type and resource allocation strategy id from uniresource
    body = query_resource_template.render()
    variables = {"resource": resource}
    body = body.replace('\n', '').replace('\\', '')
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    resource_type_id = (
        data["data"]["QueryResourceTypes"][0]["id"]
        if data["data"]["QueryResourceTypes"]
        else None
    )
    resource_strategy_id = (
        data["data"]["QueryAllocationStrategies"][0]["id"]
        if data["data"]["QueryAllocationStrategies"]
        else None
    )
    return resource_type_id, resource_strategy_id


@logging_handler(log)
def create_pool(task, logs):
    """
    Create pool id in Uniresource

         Args:

             task (dict): dictionary with input data ["resource", "poolName", "poolProperties"]

             logs: stream of log messages

        Returns:
            Response from uniresource. Worker output format::
            response_body: {
              "data": {
                "CreateAllocatingPool": {
                  "pool": {
                    "id": "<id>"
                  }
                }
              }
            }

    """

    pool_name = task["inputData"]["poolName"]
    resource = task["inputData"]["resource"]
    resource_type_id, resource_strategy_id = query_resource_id(resource)
    if resource_type_id is None or resource_strategy_id is None:
        log.warning("Unknown resource: %s", resource)
        return failed_response(logs, "Unknown resource")

    variables = {
        "resource_type_id": resource_type_id,
        "resource_type_strat_id": resource_strategy_id,
        "pool_name": pool_name,
    }
    pool_types_string, pool_string, pool_variables_string = "", "", ""
    if task["inputData"]["poolProperties"]:
        pool_properties = task["inputData"]["poolProperties"]
        for index, key in enumerate(pool_properties.keys()):
            variable_type = type(pool_properties[key])
            property_variable = ""
            if variable_type is str:
                variable_type = "string"
                property_variable = "String!"
            elif variable_type is dict:
                variable_type = "map"
                property_variable = "Map!"
            elif variable_type is int:
                variable_type = "int"
                property_variable = "ID!"
            elif variable_type is bool:
                variable_type = "bool"
                property_variable = "Boolean"
            pool_types_string += key + ': "' + variable_type + '"'
            pool_variables_string += "$" + key + ": " + property_variable
            pool_string += key + ": $" + key
            if index < len(pool_properties.keys()) - 1:
                pool_string += ",\n"
                pool_types_string += ",\n"
                pool_variables_string += ", "
            variables.update({key: pool_properties[key]})

    body = create_pool_template.render(
    {
        "create_pool": "CreateAllocatingPool",
        "pool_properties_types": "poolPropertyTypes: {\n" + pool_types_string + "\n}",
        "pool_properties": "poolProperties: {\n" + pool_string + "\n}",
        "pool_properties_variables": pool_variables_string,
    }
    )
    body = body.replace('\n', '').replace('\\', '')
    
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    response = execute(body, variables)
    if "errors" in response:
        return failed_response({"response_body": response["errors"][0]["message"]})
    return completed_response({"response_body": response["data"]})


@logging_handler(log)
def create_vlan_pool(task, logs):
    """
    Create vlan pool in Uniresource
    Args:

         task (dict): dictionary with input data ["poolName", "from", "to", "parent_resource_id"]

         logs: stream of log messages
    """
    pool_name = task["inputData"]["poolName"]
    from_range = task["inputData"]["from"] if "from" in task["inputData"] else None
    to_range = task["inputData"]["to"] if "to" in task["inputData"] else None
    parent_resource_id = (
        task["inputData"]["parentResourceId"]
        if "parentResourceId" in task["inputData"]
        else None
    )
    if parent_resource_id == "":
        parent_resource_id = None

    resource_type_id, resource_strategy_id = query_resource_id("vlan")
    variables = {
        "pool_name": pool_name,
        "resource_type_id": resource_type_id,
        "resource_type_strat_id": resource_strategy_id,
        "from": int(from_range) if from_range else from_range,
        "to": int(to_range) if to_range else to_range,
    }

    if parent_resource_id is not None:
        body = create_pool_template.render(
            {
                "create_pool": "CreateNestedAllocatingPool",
                "parent_resource_id": 'parentResourceId: "'
                + str(parent_resource_id)
                + '"',
            }
        )
    else:
        body = create_pool_template.render(
            {
                "create_pool": "CreateAllocatingPool",
                "pool_properties_variables": " $from: Int!, $to: Int!",
                "pool_properties_types": 'poolPropertyTypes:{ from: "int", to: "int"}',
                "pool_properties": "poolProperties:{ from: $from, to: $to }",
            }
        )
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    return completed_response({"response_body": data})


@logging_handler(log)
def create_vlan_range_pool(task, logs):
    """
    Create vlan range pool in Uniresource
    Args:

         task (dict): dictionary with input data ["poolName", "from", "to"]

         logs: stream of log messages
    """
    pool_name = task["inputData"]["poolName"]
    from_range = task["inputData"]["from"]
    to_range = task["inputData"]["to"]

    resource_type_id, resource_strategy_id = query_resource_id("vlan_range")
    variables = {
        "pool_name": pool_name,
        "resource_type_id": resource_type_id,
        "resource_type_strat_id": resource_strategy_id,
        "from": int(from_range) if from_range else from_range,
        "to": int(to_range) if to_range else to_range,
    }

    body = create_pool_template.render(
        {
            "create_pool": "CreateAllocatingPool",
            "pool_properties_variables": " $from: Int!, $to: Int!",
            "pool_properties_types": 'poolPropertyTypes:{ from: "int", to: "int"}',
            "pool_properties": "poolProperties:{ from: $from, to: $to }",
        }
    )
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    return completed_response({"response_body": data})


@logging_handler(log)
def create_unique_id_pool(task, logs):
    """
    Create vlan range pool in Uniresource
    Args:

         task (dict): dictionary with input data ["poolName", "idFormat"]

         logs: stream of log messages
    """
    pool_name = task["inputData"]["poolName"]
    id_format = task["inputData"]["idFormat"]
    from_value = task["inputData"]["from"] if "from" in task["inputData"] else None
    if from_value == "":
        from_value = None

    to_value = task["inputData"]["to"] if "to" in task["inputData"] else None
    if to_value == "":
        to_value = None

    resource_type_id, resource_strategy_id = query_resource_id("unique_id")
    variables = {
        "resource_type_id": resource_type_id,
        "resource_type_strat_id": resource_strategy_id,
        "pool_name": pool_name,
    }

    to_poperty_type = ', to: "int"' if to_value is not None else ""
    to_poperty = ", to: " + str(to_value) if to_value is not None else ""

    from_poperty_type = ', from: "int"' if from_value is not None else ""
    from_poperty = ", from: " + str(from_value) if from_value is not None else ""

    body = create_pool_template.render(
        {
            "create_pool": "CreateAllocatingPool",
            "pool_properties_types": 'poolPropertyTypes:{ idFormat: "string"'
            + from_poperty_type
            + to_poperty_type
            + "}",
            "pool_properties": 'poolProperties:{ idFormat: "'
            + id_format
            + '"'
            + from_poperty
            + to_poperty
            + "}",
        }
    )
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    return completed_response({"response_body": data})


@logging_handler(log)
def query_pool(task, logs):
    """
    Query pool id in Uniresource

         Args:

             task (dict): dictionary with input data ["poolNames", "resourceTypeId"]

             logs: stream of log messages

        Returns:
            Response from uniresource. Worker output format::
            response_body:{
              "data": {
                "QueryResourcePools": [
                  {
                    "id": "<id>"
                  }
                ]
              }
            }

    """
    pool_names = task["inputData"]["poolNames"]
    if type(pool_names) == str:
        pool_names = [name.strip() for name in pool_names.split(",")]
    resource = task["inputData"]["resource"]
    resource_type_id, resource_strategy_id = query_resource_id(resource)
    if resource_type_id is None or resource_strategy_id is None:
        log.warning("Unknown resource: %s", resource)
        return failed_response(logs, "Unknown resource")
    pool_names_string = ""
    for index, pool_name in enumerate(pool_names):
        pool_names_string += '"' + pool_name + '"'
        if index < len(pool_names) - 1:
            pool_names_string += ", "
    variables = {"resource_type_id": resource_type_id}
    body = query_pool_template.render({"pool_names": pool_names_string})
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    return completed_response({"response_body": data})


@logging_handler(log)
def query_unique_id_pool(task, logs):
    """
    Query Unique id pool in Uniresource

         Args:

             task (dict): dictionary with input data ["poolNames"]

             logs: stream of log messages

    """
    pool_names = task["inputData"]["poolNames"]
    query_pool_result = query_pool(
        {"inputData": {"resource": "unique_id", "poolNames": pool_names}}
    )
    return completed_response(
        {"response_body": query_pool_result["output"]["response_body"]}
    )


@logging_handler(log)
def query_vlan_pool(task, logs):
    """
    Query Vlan pool in Uniresource

         Args:

             task (dict): dictionary with input data ["poolNames"]

             logs: stream of log messages

    """
    pool_names = task["inputData"]["poolNames"]
    query_pool_result = query_pool(
        {"inputData": {"resource": "vlan", "poolNames": pool_names}}
    )
    return completed_response(
        {"response_body": query_pool_result["output"]["response_body"]}
    )

@logging_handler(log)
def query_pool_by_tag(task, logs):
    """
    Query pool by tag in Uniresource

         Args:

             task (dict): dictionary with input data ["poolTag"]


         Returns:
            Response from uniresource. Worker output format::
            "response_body": {
                "data": {
                    "SearchPoolsByTags": [
                        {
                            "id": "<id>",
                            "Name": "<name>"
                        }
                    ]
                }
            } 
    
    """
    pool_tag = task["inputData"]["poolTag"]
    body = query_pool_by_tag_template.render()
    variables = {"poolTag": pool_tag}
    body = body.replace('\n', '').replace('\\', '')
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    response_data = execute(body, variables)
    return completed_response(
        {"response_body": response_data}
    )

@logging_handler(log)
def query_vlan_range_pool(task, logs):
    """
    Query Vlan range pool in Uniresource

         Args:

             task (dict): dictionary with input data ["poolNames"]

             logs: stream of log messages

    """
    pool_names = task["inputData"]["poolNames"]
    query_pool_result = query_pool(
        {"inputData": {"resource": "vlan_range", "poolNames": pool_names}}
    )
    return completed_response(
        {"response_body": query_pool_result["output"]["response_body"]}
    )


@logging_handler(log)
def update_alt_id_for_resource(task, logs):
    """
    Update alternative id for resource from Uniresource

         Args:

             task (dict): dictionary with input data ["poolId", "userInput", "alternativeId"]

             logs: stream of log messages

        Returns:
            Response from Uniresource. Worker output format::
            response_body: {
              "data": {
                "UpdateResourceAltId": {
                  "AlternativeId": {
                    <alternativeId>
                  }
                }
              }
            }

    """
    pool_id = task["inputData"]["poolId"] if "poolId" in task["inputData"] else None
    if pool_id is None:
        return failed_response(logs, "No pool id")
    user_input = (
        task["inputData"]["userInput"] if "userInput" in task["inputData"] else None
    )
    if user_input is None:
        return failed_response(logs, "No user input")
    alternative_id = (
        task["inputData"]["alternativeId"]
        if "alternativeId" in task["inputData"]
        else None
    )
    if alternative_id is None:
        return failed_response(logs, "No alternative id")
    variables = {
        "pool_id": pool_id,
        "input": user_input,
        "alternative_id": alternative_id,
    }
    body = update_alternative_id_for_resource_template.render(
        {"update_alt_id": "UpdateResourceAltId"}
    )
    log.debug("Sending graphql variables: %s\n with query: %s" % (variables, body))
    data = execute(body, variables)
    return completed_response({"response_body": data})


def start(cc):
    cc.register(
        "UNIRESOURCE_claim_resource",
        {
            "name": "UNIRESOURCE_claim_resource",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        claim_resource,
    )

    cc.register(
        "UNIRESOURCE_query_claimed_resource",
        {
            "name": "UNIRESOURCE_query_claimed_resource",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        query_claimed_resources,
    )

    cc.register(
        "UNIRESOURCE_create_pool",
        {
            "name": "UNIRESOURCE_create_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        create_pool,
    )

    cc.register(
        "UNIRESOURCE_create_vlan_pool",
        {
            "name": "UNIRESOURCE_create_vlan_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        create_vlan_pool,
    )

    cc.register(
        "UNIRESOURCE_create_vlan_range_pool",
        {
            "name": "UNIRESOURCE_create_vlan_range_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        create_vlan_range_pool,
    )

    cc.register(
        "UNIRESOURCE_create_unique_id_pool",
        {
            "name": "UNIRESOURCE_create_unique_id_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        create_unique_id_pool,
    )

    cc.register(
        "UNIRESOURCE_query_pool",
        {
            "name": "UNIRESOURCE_query_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        query_pool,
    )

    cc.register(
        "UNIRESOURCE_query_unique_id_pool",
        {
            "name": "UNIRESOURCE_query_unique_id_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        query_unique_id_pool,
    )

    cc.register(
        "UNIRESOURCE_query_vlan_pool",
        {
            "name": "UNIRESOURCE_query_vlan_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        query_vlan_pool,
    )

    cc.register(
        "UNIRESOURCE_query_pool_by_tag",
        {
            "name": "UNIRESOURCE_query_pool_by_tag",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        query_pool_by_tag,
    )


    cc.register(
        "UNIRESOURCE_query_vlan_range_pool",
        {
            "name": "UNIRESOURCE_Query_vlan_range_pool",
            "description": '{"description": "": [""]}',
            "retryCount": 0,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "inputKeys": [""],
            "outputKeys": [],
        },
        query_vlan_range_pool,
    )
