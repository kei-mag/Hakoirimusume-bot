import sqlite3

from hakoirimusume.authorizer import Authorizer


class DB:
    BANNED_USER = -1
    UNAUTHORIZED_USER = 0
    USER = 1
    ADMIN = 2
    
    def __init__(self, dbname: str) -> None:
        self.conn = sqlite3.connect(dbname)
        self._dbname = dbname

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def _create_users_table(self):
        self.reconnect_if_need()
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id TEXT PRIMARY KEY,"
            "role INTEGER DEFAULT 0 NOT NULL,"
            "state INTEGER DEFAULT 0 NOT NULL,"
            "request_time TEXT DEFAULT NULL,"
            "CHECK (role >= -1 AND role <= 2),"  # -1: Banned, 0: Unauthorized User, 1: Normal User, 2: Admin
            ");"
        )

    def reconnect_if_need(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self._dbname)

    def close(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None
    
    def reset_states(self):
        cur = self.conn.cursor()
        cur.execute("UPDATE users SET state = 0, request_time = NULL")
        self.conn.commit()


    def get_state(self, user_id: str):
        cur = self.conn.cursor()
        cur.execute("SELECT state FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return row[0]
    
    def set_state(self, user_id: str, state: int):
        cur = self.conn.cursor()
        cur.execute("UPDATE users SET state = ? WHERE id = ?", (state, user_id))
        self.conn.commit()

    def get_users(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id WHERE role >= ?", (self.USER,))
        rows = cur.fetchall()
        return [row[0] for row in rows]

    def get_admins(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id WHERE role >= ?", (self.ADMIN,))
        rows = cur.fetchall()
        return [row[0] for row in rows]

    def get_banned_users(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id WHERE role < 0")
        rows = cur.fetchall()
        return [row[0] for row in rows]

    def add_user(self, user_id: str):
        cur = self.conn.cursor()
        # Check if the user is already in the table
        if cur.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone():
            # Check existing user's authority level, if the user is banned, return False
            if cur.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()[0] < 0:
                return False
            else:
                return True
        else:
            cur.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            self.conn.commit()
            return True

    def remove_user(self, user_id: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()

    def get_role(self, user_id: str):
        cur = self.conn.cursor()
        cur.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return row[0]

    def is_satisfied_role(self, user_id: str, level: int):
        cur = self.conn.cursor()
        cur.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if row is None:
            return False
        return row[0] >= level

    def set_role(self, user_id: str, level: int):
        cur = self.conn.cursor()
        cur.execute("UPDATE users SET role = ? WHERE id = ?", (level, user_id))
        self.conn.commit()

    def print_table(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        if not rows:
            print("No data in the table.")
        for row in rows:
            print(row)

    def commit(self, close=True):
        self.conn.commit()
        if close:
            self.conn.close()


db = DB("test.db")


class AuthorityManager:
    def __init__(self) -> None:
        self.db = db
        self.authorizer = Authorizer()

    def create_new_aikotoba(self, user_id: str):
        return self.authorizer.create_new_aikotoba(user_id)

    def authorize_request(self, user_id: str):
        self.db.add_user(user_id)
        self.db.set_state(user_id, 1)
        print("Aikotoba: ", self.create_new_aikotoba("test_user"))  # WARNING: DEBUG ONLY!

    def authorize(self, user_id: str, aikotoba: str):
        is_succeed = self.authorizer.authorize(aikotoba)
        if is_succeed:
            self.db.set_role(user_id, 1)
        return is_succeed

    def can_access(self, user_id: str, need_level: int):
        return self.db.is_satisfied_role(user_id, need_level)

    def delete_user(self, user_id: str):
        self.db.remove_user(user_id)

    def is_wait_for_aikotoba(self, user_id: str):
        return self.db.get_state(user_id) == 1


auth_manager = AuthorityManager()
