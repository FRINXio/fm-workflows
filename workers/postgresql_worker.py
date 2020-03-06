import psycopg2
from configparser import ConfigParser


def config(filename='../database.ini', section='postgresql'):

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


def open_conn():
    conn = None
    cur = None
    try:
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')

        conn = psycopg2.connect(**params)
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return cur, conn


def close_conn(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')


def execute_command(task):
    command = task['inputData']['command']
    cur, conn = open_conn()
    try:
        cur.execute(command)
        cur.close()

        conn.commit()
        close_conn(conn)
        return {'status': 'COMPLETED', 'output': {'result': command % " was executed"},
                'logs': [command % " was executed"]}
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return {'status': 'FAILED', 'output': {'result': error},
                'logs': ["Error"]}


def start(cc):
    cc.register('POSTGRESQL_execute_command', {
        "name": "POSTGRESQL_execute_command",
        "description": "check unified node exists - BASICS,UNIFIED",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "command"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('POSTGRESQL_execute_command', execute_command, False)
