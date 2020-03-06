import unittest

import postgresql_worker

create_interface = """CREATE TABLE interface (
            id SERIAL PRIMARY KEY,
            device int NOT NULL,
            connection int NOT NULL,
            name VARCHAR(255),
            description VARCHAR(255),
            config bytea,
            type VARCHAR(50),
            infra_type VARCHAR(50),
            port_channel_id int,
            max_frame_size int
        )"""


class TestConnection(unittest.TestCase):
    def test_connect(self):
        conn, cur = postgresql_worker.open_conn()
        cur.close()
        postgresql_worker.close_conn(conn)


class TestCreateTable(unittest.TestCase):
    def test_create_table(self):
        request = postgresql_worker.execute_command({"inputData": {"command": create_interface}})
        self.assertEqual(request["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
