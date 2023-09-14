import datetime
import json
import os
import string
from random import randint, shuffle
from sqlite3 import OperationalError

from hakoirimusume.db import get_db


class AuthoritiesManager:
    NOT_USER = -1
    NORMAL_USER = 0
    ADMIN_USER = 1

    def __init__(self, time_out_sec: int):
        self.TIME_OUT = time_out_sec

    def is_user(self, user_id):
        cur = get_db().cursor()
        try:
            result = cur.execute(f"SELECT auth_type FROM user WHERE id='{user_id}';").fetchone()
            if result is None:
                result = -1
            else:
                result = result[0]
        except OperationalError as e:
            print(e)
            result = -1
        return result

    def invite_user(self, requester_user_id, auth_type):
        if self.is_user(requester_user_id) >= auth_type:
            password = self.generate_password(auth_type)
            db = get_db()
            cur = db.cursor()
            cur.execute(f"DELETE FROM otp WHERE auth_type={auth_type};")
            cur.execute(
                f"INSERT INTO otp VALUES({auth_type}, '{password}', datetime('now', '+{self.TIME_OUT} seconds'));"
            )
            db.commit()
            return password
        else:
            return False

    def generate_password(self, auth_type: int):
        if auth_type == 0:
            # Generate Aikotoba for normal users
            seed = [
                ["かわいい", "ちっちゃな", "自立した", "よく食べる", "健気な", "若々しい", "いたずら好きの", "お利口な"],
                ["姫", "お姫様", "箱入り娘", "うさちゃん", "うさぎ", "プリンセス", "ラビット"],
            ]
            shuffle(seed[0])
            shuffle(seed[1])
            return seed[0][0] + seed[0][1] + seed[1][0]
        else:
            # Generate Password for admin users
            seed = string.ascii_letters + string.digits
            return "".join([seed[s] for s in [randint(0, len(seed)) for i in range(8)]])

    def authorize(self, user_id: str, password: str, type: int):
        """Add user to authrities.json

        Parameters
        ----------
        user_id : str
            Specify LINE user ID of added user

        Returns
        -------
        bool or None
            True  : success to add user.
            False : specified userID already exists.
            None  : specified userID already exists as admin.
        """
        db = get_db()
        cur = db.cursor()
        # Delete expired passwords
        cur.execute(f"DELETE FROM otp WHERE strftime('%s', expired_time)<strftime('%s', 'now')")
        # Check if user is already registerd
        users = [v for u in cur.execute(f"SELECT id FROM user WHERE auth_type>={type};").fetchall() for v in u]
        if user_id in users:
            print("auth None")
            return None
        else:
            print("elseelse")
            # Check Aikotoba
            # Delete expired passwords
            cur.execute(f"DELETE FROM otp WHERE strftime('%s', expired_time)<strftime('%s', 'now')")
            # todo: delete ---------------------------------------
            result = db.execute("SELECT datetime('now');").fetchone()[0]
            print("curTime", result)
            print("--------------- user ---------------")
            result = db.execute("SELECT * from user;").fetchall()
            for r in result:
                for v in r:
                    print(v, end="\t")
                print("")
            print("--------------- otp ---------------")
            result = db.execute("SELECT * from otp;").fetchall()
            for r in result:
                for v in r:
                    print(v, end="\t")
                print("")
            # todo: delete ---------------------------------------
            correct_aikotoba = cur.execute(f"SELECT password FROM otp WHERE auth_type={type};").fetchone()[0]
            if correct_aikotoba and password == correct_aikotoba:
                # add user data to db
                cur.execute(
                    f"INSERT INTO user VALUES('{user_id}', {type}, 0, datetime('now', '+{self.TIME_OUT} seconds'));"
                )
                # Delete password that is used at this time.
                cur.execute(f"DELETE FROM otp WHERE auth_type={type};")
                db.commit()
                return True
            else:
                return False


if __name__ == "__main__":
    manager = AuthoritiesManager(5)
    print(manager.generate_password(0))
