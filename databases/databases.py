import sqlite3
from pathlib import Path

from time import sleep

from .database_factories import SqliteDatabaseFactory


class SqliteDatabase:
    def __init__(self, database_name: str, database_path: Path,
                 database_config: str = '', override: bool = False):
        print(f'constructing sqlite database {database_name}')

        # Create database directory if not exists
        self.database_dir = database_path / 'sqlite'
        self.database_dir.mkdir(parents=True, exist_ok=True)

        # Create database if not exists
        self.database_path = self.database_dir / f'{database_name}.db'
        if self.database_path.exists() and override:
            self.database_path.unlink()
        self.database_path.touch(exist_ok=True)

        # Attempt connection to newly created database
        print(
            f'attemting to connect to sqlite database at path '
            f'{self.database_path}')
        while True:
            try:
                con = sqlite3.connect(str(self.database_path))
                con.row_factory = SqliteDatabaseFactory.dict_factory
                print(f'connected to sqlite database {database_name}')
                print(str(self.database_path))
                break
            except sqlite3.OperationalError as e:
                print(
                    f'Error connecting to database at {self.database_path},\n'
                    f'retrying in 1sec...')
                sleep(1)

        if not database_config == '':
            self.configure_database(database_config)

    def _get_database_connection(self):
        con = sqlite3.connect(str(self.database_path))
        con.row_factory = SqliteDatabaseFactory.dict_factory
        return con

    def configure_database(self, database_config: str):
        print(f'configuring database...')
        for query in database_config.split(';'):
            self.send_query(query)

    def _execute_query(self, query):
        with self._get_database_connection() as con:
            try:
                cur = con.cursor()
                cur.execute(query)
                return cur
            except sqlite3.OperationalError as e:
                print(f'Query failed.\n'
                      f'"{query}"\n{e}')

    def send_query(self, query):
        self._execute_query(query)

    def fetchone_query(self, query):
        q = self._execute_query(query)
        if not q:
            return None
        return q.fetchone()

    def fetchmany_query(self, query, size):
        q = self._execute_query(query)
        if not q:
            return []
        return q.fetchmany(size)

    def fetchall_query(self, query):
        q = self._execute_query(query)
        if not q:
            return []
        return q.fetchall()
