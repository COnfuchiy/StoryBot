# NAW sql class by SemD
import sqlite3 as Sql


class NAWDataBase:
    def __init__(self):
        self._db_name = "naw.db"
        self._db = None
        self._connection = Sql.connect(self._db_name, check_same_thread=False)
        self._err = 0
        if self.check_connection():
            self.check_table()

    def __del__(self):
        if self._connection:
            self._connection.commit()
            self._connection.close()

    def check_connection(self):
        if self._connection:
            # logging
            cursor = self._connection.cursor()
            if cursor:
                self._db = cursor
                return True
            else:
                self._err = -1
                return False
        else:
            # logging
            self._err = -1
            return False

    def check_table(self):
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS naw_players (ID INT, 'Step' INT, 'Path' TEXT, 'Position' INT)")
        self._connection.commit()

    def is_ok(self):
        return self._err == 0

    def create_user(self, user_id, path):
        if self.get_user_data(user_id)!={}:
            self._db.execute("DELETE FROM naw_players WHERE ID = ?", (user_id,))
        self._db.execute("INSERT INTO naw_players VALUES (?, ?, ?, ?)", (user_id, 0, path,0,))
        self._connection.commit()

    def get_user_data(self, user_id):
        self._db.execute("SELECT * FROM naw_players WHERE ID = ?", (user_id,))
        user_data = self._db.fetchone()
        if user_data:
            return {'step': user_data[1], 'path': user_data[2].split('|'), 'position': user_data[3]}
        else:
            return {}

    def upd_data(self, user_id, user_data):
        self._db.execute("UPDATE naw_players SET Step = ?, Path = ?, Position = ? WHERE ID = ?",
                         (user_data['step'], '|'.join(user_data['path']), user_data['position'], user_id,))
        self._connection.commit()
