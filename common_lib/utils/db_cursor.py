from typing import Union
from mysql.connector.connection import (
    MySQLConnection,
    MySQLCursor,
    MySQLCursorBuffered,
    MySQLCursorRaw,
    MySQLCursorBufferedRaw,
    MySQLCursorDict,
    MySQLCursorBufferedDict,
    MySQLCursorNamedTuple,
    MySQLCursorBufferedNamedTuple,
    MySQLCursorPrepared,
)


class GlobalMysql:
    db_connection = None
    cursor = None

    @classmethod
    def get_cursor(
        cls,
        cursor: Union[
            MySQLCursor,
            MySQLCursorBuffered,
            MySQLCursorRaw,
            MySQLCursorBufferedRaw,
            MySQLCursorDict,
            MySQLCursorBufferedDict,
            MySQLCursorNamedTuple,
            MySQLCursorBufferedNamedTuple,
            MySQLCursorPrepared,
        ],
    ):
        cls.cursor = cursor

    @classmethod
    def get_db_connection(cls, connection: MySQLConnection):
        cls.db_connection = connection

    @classmethod
    def reset(cls):
        cls.cursor = None
        cls.db_connection = None
