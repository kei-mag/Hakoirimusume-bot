import datetime
import json
import os

from hakoirimusume.db import get_db


class AuthoritiesManager:
    DELETED_USER = -1
    NORMAL_USER = 0
    ADMIN_USER = 1

    def __init__(self, time_out_sec: int):
        self.TIME_OUT = time_out_sec

    def add_user(self, user_id: str, password: str, type: int):
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
        # Check if user is already registerd
        users = cur.execute(f"SELECT id FROM user WHERE auth_type>={type};")
        if user_id in users:
            return None
        else:
            # Check Aikotoba
            # Delete expired passwords
            cur.execute(f"DELETE FROM otp WHERE strftime('%s', expired_time)<strftime('%s', 'now')")
            correct_aikotoba = cur.execute(f"SELECT password FROM otp WHERE auth_type={type};")
            if correct_aikotoba and password == correct_aikotoba:
                # add user data to db
                cur.execute(
                    f"INSERT INTO user VALUES('{user_id}', {type}, 0, datetime('now', '+{self.TIME_OUT} seconds'));"
                )
                # Delete password that is used at this time.
                cur.execute(f"DELETE FROM otp WHERE auth_type={type};")
                return True
            else:
                return False
