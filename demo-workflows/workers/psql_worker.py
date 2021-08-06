import psycopg2
import random
import requests
import string


from configparser import ConfigParser

pool = None


def config(filename='/home/app/netinfra_utils/workers/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def _open_conn():
    conn, cur = None, None
    try:
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn, cur


def _close_conn(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')


def exec_command(command, conn=None):
    conn, cur = None, None
    try:
        conn, cur = _open_conn()
        if conn is not None and cur is not None:
            cur.execute(command)
            mobile_records = command if "SELECT" not in command else cur.fetchall()
            conn.commit()
            print(mobile_records)
            return 200, mobile_records
        else:
            raise Exception('No connection')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return 400, error
    finally:
        if cur is not None:
            cur.close()
            _close_conn(conn)


def select_device(task):
    device = task['inputData']['device']
    command = "SELECT devicedata.devicedata FROM devmandpoc.devicedata WHERE devicedata.devicename='" + device + "'"
    response_code, response_data = exec_command(command)
    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'result': response_data},
                'logs': [command]}
    else:
        return {'status': 'FAILED', 'output': {'result': response_data},
                'logs': [response_data]}


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def insert_organizations(task):
    command = "INSERT INTO devmandpoc.organizations (api_key) VALUES ('" + id_generator() + "')"
    response_code, response_data = exec_command(command)
    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'result': response_data},
                'logs': [command]}
    else:
        return {'status': 'FAILED', 'output': {'result': response_data},
                'logs': [response_data]}


def start(cc):
    print('Start PSQL workers')

    cc.register('PSQL_select_device', {
        "description": '{"description": "Select device", "labels": ["PSQL"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device"
        ],
        "outputKeys": [
            "result"
        ]
    }, select_device)

    cc.register('PSQL_insert_organizations', {
        "description": '{"description": "Select insert_organizations", "labels": ["PSQL"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
        ],
        "outputKeys": [
            "result"
        ]
    }, insert_organizations)
