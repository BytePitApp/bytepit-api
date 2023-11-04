import sys
import time

from typing import List

import psycopg
from psycopg.rows import dict_row


class Database:
    def __init__(self, connection_string):
        self.connection = self.connect(connection_string)

    def connect(self, connection_string, max_retries=3):
        for _ in range(0, max_retries):
            try:
                connection = psycopg.connect(connection_string, row_factory=dict_row, autocommit=True)
                return connection
            except psycopg.OperationalError as e:
                print("Unable to connect to database. Retrying...")
                time.sleep(3)
        print("Unable to connect to database")
        sys.exit(1)

    def execute_one(self, query_tuple: tuple):
        (query, param_dict) = query_tuple

        cursor = self.connection.cursor()
        cursor.execute(query, param_dict)

        if cursor.description is not None:
            result = cursor.fetchall()
            return {"result": result, "affected_rows": cursor.rowcount}
        else:
            return {"affected_rows": cursor.rowcount}

    def execute_many(self, query_tuple_list: List[tuple]):
        total_affected_rows = 0
        cursor = self.connection.cursor()
        with self.connection.transaction():
            for query, param_dict in query_tuple_list:
                cursor.execute(query, param_dict)
                total_affected_rows += cursor.rowcount
            return {"affected_rows": total_affected_rows}
