import logging
import threading
import sqlparse

from typing import Generator, Union
from contextlib import contextmanager
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

from common_lib.utils.singleton import Singleton, initialize_once


logger = logging.getLogger(__name__)


class DB(Singleton):
    @initialize_once
    def __init__(self, name: str):
        self.name = name
        self.mysql_host = None
        self.mysql_user = None
        self.mysql_password = None
        self.mysql_db = None
        self.mysql_port = 3306
        self.connection_timeout = 20

        self._connection_pool = None
        self.__singleton_lock = threading.Lock()

    def init_app(
        self,
        mysql_host: str,
        mysql_user: str,
        mysql_password: str,
        mysql_db: str,
        mysql_port: int = 3306,
        connection_timeout: int = 20,
    ):
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_db = mysql_db
        self.mysql_port = mysql_port
        self.connection_timeout = connection_timeout

    @contextmanager
    def cursor(
        self,
        buffered=None,
        raw=None,
        prepared=None,
        cursor_class=None,
        dictionary=None,
        named_tuple=None,
    ) -> Generator[
        Union[
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
        None,
        None,
    ]:
        conn = MySQLConnection(
            host=self.mysql_host,
            user=self.mysql_user,
            password=self.mysql_password,
            db=self.mysql_db,
            port=self.mysql_port,
            charset="utf8",
            buffered=True,
            connection_timeout=self.connection_timeout,
        )

        cursor = conn.cursor(
            buffered=buffered,
            raw=raw,
            prepared=prepared,
            cursor_class=cursor_class,
            dictionary=dictionary,
            named_tuple=named_tuple,
        )
        try:
            yield cursor
        except Exception as e:
            conn.rollback()
            if cursor.statement:
                logger.error(sqlparse.format(cursor.statement, reindent=True))
            logger.error(e)
            raise e
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    @contextmanager
    def get_connection(self) -> Generator[MySQLConnection, None, None]:
        conn = MySQLConnection(
            host=self.mysql_host,
            user=self.mysql_user,
            password=self.mysql_password,
            db=self.mysql_db,
            port=self.mysql_port,
            charset="utf8",
            buffered=True,
            connection_timeout=self.connection_timeout,
        )

        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(e)
            raise e
        finally:
            conn.commit()
            conn.close()

    def get_connection_without_ctx_manager(self) -> MySQLConnection:
        conn = MySQLConnection(
            host=self.mysql_host,
            user=self.mysql_user,
            password=self.mysql_password,
            db=self.mysql_db,
            port=self.mysql_port,
            charset="utf8",
            buffered=True,
            connection_timeout=self.connection_timeout,
        )

        return conn

    def get_cursor(
        self,
        mysql_connection: MySQLConnection,
        buffered=None,
        raw=None,
        prepared=None,
        cursor_class=None,
        dictionary=None,
        named_tuple=None,
    ) -> Union[
        MySQLCursor,
        MySQLCursorBuffered,
        MySQLCursorRaw,
        MySQLCursorBufferedRaw,
        MySQLCursorDict,
        MySQLCursorBufferedDict,
        MySQLCursorNamedTuple,
        MySQLCursorBufferedNamedTuple,
        MySQLCursorPrepared,
    ]:
        cursor = mysql_connection.cursor(
            buffered=buffered,
            raw=raw,
            prepared=prepared,
            cursor_class=cursor_class,
            dictionary=dictionary,
            named_tuple=named_tuple,
        )
        if self.connection_timeout > 0:
            cursor.execute(
                f"SET SESSION MAX_EXECUTION_TIME = {self.connection_timeout * 1000}"
            )
        return cursor
