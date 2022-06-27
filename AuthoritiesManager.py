#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import datetime

class AuthoritiesManager:
    def __init__(self, dataFilePath:str=None):
        if dataFilePath == None:
            self._dataFilePath = './data/authorities.json'
        else:
            self._dataFilePath = dataFilePath
        while True:
            try:
                with open(self._dataFilePath, 'r', encoding='utf-8') as f:
                    self._dataMap = json.load(f)
                break
            except FileNotFoundError:
                self._initializeJson()
            except json.decoder.JSONDecodeError:
                print(f"[Warning] AuthoritiesManager: ${self._dataFilePath} is broken.\nReset system data to recover.")
                exit(code=1)
    
    def _initializeJson(self):
        try:
            with open(self._dataFilePath, 'w', encoding='utf-8') as f:
                initMap:'dict[str,str]' = {'users':{}}
                json.dump(initMap, f, indent=4, ensure_ascii=True)
        except FileNotFoundError:
            os.mkdir('./data')
            self._initializeJson()

    def saveToJson(self):
        with open(self._dataFilePath, 'w', encoding='utf-8') as f:
            json.dump(self._dataMap, f, indent=4, ensure_ascii=True)

    def addUser(self, userID:str) -> bool or None:
        """Add user to authrities.json

        Parameters
        ----------
        userID : str
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
            if self._dataMap['users'][userID]['type'] == 'admin':
                return None
            else:
                return False
        except KeyError:
            self._dataMap['users'][userID] = {}
            self._dataMap['users'][userID]['type'] = 'user'
            self._dataMap['users'][userID]['addDate'] = str(datetime.datetime.now())
            self._dataMap['users'][userID]['lastUpdateDate'] = None
            return True

    def addAdmin(self, userID) -> bool or None:
        # check if specified userID exists
        try:
            if self._dataMap['users'][userID]['type'] == 'admin':
                return False
            else:
                self._dataMap['users'][userID]['type'] = 'admin'
                self._dataMap['users'][userID]['lastUpdateDate'] = str(datetime.datetime.now())
                return True
        except KeyError:
            self._dataMap['users'][userID] = {}
            self._dataMap['users'][userID]['type'] = 'user'
            self._dataMap['users'][userID]['addDate'] = str(datetime.datetime.now())
            self._dataMap['users'][userID]['lastUpdateDate'] = None
            return True

if __name__ == '__main__':
    authManager = AuthoritiesManager()
    print(authManager._dataMap['users'])
    print(authManager.addUser('asdgbxg'))
    print(authManager._dataMap['users'])
    print(authManager.addAdmin('asdgbxg'))
    print(authManager._dataMap['users'])
    authManager.saveToJson()