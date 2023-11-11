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
                connection = psycopg.connect(
                    connection_string, row_factory=dict_row, autocommit=True
                )
                return connection
            except psycopg.OperationalError as e:
                print("Unable to connect to database. Retrying...")
                time.sleep(3)
        print("Unable to connect to database")
        sys.exit(1)

    def execute_one(self, query_tuple: tuple):
        try:
            assert isinstance(query_tuple[0], str), "Query must be a string"
            assert query_tuple[1] is None or isinstance(
                query_tuple[1], tuple
            ), "Query parameters must be a tuple or None"

            (query, param_tuple) = query_tuple

            cursor = self.connection.cursor()
            cursor.execute(query, param_tuple)

            if cursor.description is not None:
                result = cursor.fetchall()
                return {"result": result, "affected_rows": cursor.rowcount}
            else:
                return {"affected_rows": cursor.rowcount}
        except psycopg.Error as e:
            print(e)
            return {"affected_rows": 0}

    def execute_many(self, query_tuple_list: List[tuple]):
        try:
            total_affected_rows = 0
            cursor = self.connection.cursor()
            with self.connection.transaction():
                for query, param_tuple in query_tuple_list:
                    assert isinstance(query, str), "Query must be a string"
                    assert param_tuple is None or isinstance(
                        param_tuple, tuple
                    ), "Query parameters must be a tuple or None"

                    cursor.execute(query, param_tuple)
                    total_affected_rows += cursor.rowcount
                return {"affected_rows": total_affected_rows}
        except psycopg.Error as e:
            print(e)
            return {"affected_rows": 0}
