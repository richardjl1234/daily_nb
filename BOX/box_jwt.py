#!/usr/bin/env python
# coding: utf-8
import base64
import time
import os
import json
import sys
import collections
import datetime
from boxsdk import JWTAuth, Client
import requests
import logging

logging.basicConfig(stream=sys.stdout, level=int(os.environ['LOG_LEVEL']))
#box_jwt_json = os.environ['BOX_JWT_JSON']
jwt_dict = json.loads(base64.b64decode(os.environ['BOX_JWT_JSON_B64']).decode('ascii'))

def get_box_client():
    '''
    get the client based on the jwt json strring by using the jwt_dict variable
    Input: None
    return: authorized client
    '''
    logging.info('entering get_box_client function...')

    auth = JWTAuth.from_settings_dictionary(jwt_dict)
    #auth = JWTAuth.from_settings_file(string_out)
    auth.authenticate_instance()
    client = Client(auth)
    sa_user = client.user().get()
    logging.info(sa_user['name'])
    logging.info(sa_user['login'])
    return client  # normal box server can not reach to ibm dedicated cloud application
# normal box server can not reach to ibm dedicated cloud application
# normal box server can not reach to ibm dedicated cloud application

def save2box_folder(client, folder_id, file_name):
    logging.info('checking if the file name {} is already in the folder {}...'.format(file_name, folder_id))
    items = client.folder(folder_id).get_items()
    file_id = None
    for item in items:
        logging.debug('{0} {1} is named "{2}"'.format(item.type.capitalize(), item.id, item.name))
        if item.name.strip()== file_name.split('/')[-1].strip(): # remove the path from the file name
            file_id = item.id
    # after the iteration, check if file_id is set
    logging.info(file_id if file_id else 'None')
    if file_id:
        logging.info('\n BOX API to add file of NEW VERSION to folder {}....'.format(folder_id))
        new_file = client.file(file_id).update_contents(file_name)
        logging.info('File "{0}" uploaded to Box with file ID {1}'.format(new_file.name, new_file.id))
    else:
        logging.info('\n BOX API to add file to folder {}....'.format(folder_id))
        new_file = client.folder(folder_id).upload(file_name)
        logging.info('File "{0}" uploaded to Box with file ID {1}'.format(new_file.name, new_file.id))

if __name__ == '__main__':
    folder_id = '94491814782' #  tempx folder in public box.com
    client = get_box_client()
    for i in range(2):
        from datetime import datetime
        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        test_file_name = 'cache/test_{}.txt'.format(now)
        print('test file name {} is created!'.format(test_file_name))
        with open(test_file_name, 'w') as f:
            f.write('this is a test file for testing oauth2, {}'.format(now))
        save2box_folder(client, folder_id, test_file_name)
        time.sleep(1)

