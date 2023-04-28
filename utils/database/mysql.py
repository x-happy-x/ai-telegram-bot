from pymysql import cursors, connect
from ..configs import DBConfig


class MySQLDatabase:
    default_cursor = cursors.DictCursor
    connection = None

    def __init__(self, config: DBConfig = None) -> None:
        self.config = config
        self.connect(config)

    def connect(self, config: DBConfig, cursor=None):
        if config is None:
            return
        if cursor is not None:
            self.default_cursor = cursor
        self.connection = connect(host=config['SERVER'],
                                  user=config['USER'],
                                  password=config['PASSWORD'],
                                  database=config['DATABASE'],
                                  charset='utf8mb4',
                                  cursorclass=self.default_cursor)

    def close(self):
        self.connection.close()
        self.connection = None

    def select(self, query: str):
        cursor = self.connection.cursor()
        self.exec(cursor, query)
        return cursor

    def select_one(self, query: str):
        if self.is_connected():
            return self.select(query).fetchone()

    def select_many(self, query: str, size: int):
        if self.is_connected():
            return self.select(query).fetchmany(size)

    def select_all(self, query: str):
        if self.is_connected():
            return self.select(query).fetchall()

    def exec(self, cursor: cursors.DictCursor, query: str):
        # if self.is_connected():
        #     cursor.execute(query)
        try:
            if self.is_connected():
                cursor.execute(query)
        except ConnectionError:
            print("Повторная попытка подключения")
            self.close()
            self.connect(self.config)
            cursor.connection = self.connection
            cursor.execute(query)

    def insert(self, query: str):
        if self.is_connected():
            self.select(query)
            self.connection.commit()

    def is_connected(self):
        return self.connection is not None
