#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import datetime


class AuthoritiesManager:
    def __init__(self, data_file_path: str = None):
        if data_file_path == None:
            self._data_file_path = './data/authorities.json'
        else:
            self._data_file_path = data_file_path
        while True:
            try:
                with open(self._data_file_path, 'r', encoding='utf-8') as f:
                    self._data_map = json.load(f)
                break
            except FileNotFoundError:
                self._initialize_json()
            except json.decoder.JSONDecodeError:
                print(
                    f"[Warning] AuthoritiesManager: ${self._data_file_path} is broken.\nReset system data to recover.")
                exit(code=1)

    def _initialize_json(self):
        try:
            with open(self._data_file_path, 'w', encoding='utf-8') as f:
                init_map: 'dict[str,str]' = {'users': {}}
                json.dump(init_map, f, indent=4, ensure_ascii=True)
        except FileNotFoundError:
            os.mkdir('./data')
            self._initialize_json()

    def save_to_json(self):
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            json.dump(self._data_map, f, indent=4, ensure_ascii=True)

    def add_user(self, user_id: str) -> bool or None:
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

        # check if specified userID exists
        try:
            if self._data_map['users'][user_id]['type'] == 'admin':
                return None
            else:
                return False
        except KeyError:
            self._data_map['users'][user_id] = {}
            self._data_map['users'][user_id]['type'] = 'user'
            self._data_map['users'][user_id]['addDate'] = str(
                datetime.datetime.now())
            self._data_map['users'][user_id]['lastUpdateDate'] = None
            return True

    def add_admin(self, user_id) -> bool or None:
        # check if specified userID exists
        try:
            if self._data_map['users'][user_id]['type'] == 'admin':
                return False
            else:
                self._data_map['users'][user_id]['type'] = 'admin'
                self._data_map['users'][user_id]['lastUpdateDate'] = str(
                    datetime.datetime.now())
                return True
        except KeyError:
            self._data_map['users'][user_id] = {}
            self._data_map['users'][user_id]['type'] = 'user'
            self._data_map['users'][user_id]['addDate'] = str(
                datetime.datetime.now())
            self._data_map['users'][user_id]['lastUpdateDate'] = None
            return True


if __name__ == '__main__':
    authManager = AuthoritiesManager()
    print(authManager._data_map['users'])
    print(authManager.add_user('testUserId'))
    print(authManager._data_map['users'])
    print(authManager.add_admin('testUserId'))
    print(authManager._data_map['users'])
    authManager.save_to_json()
