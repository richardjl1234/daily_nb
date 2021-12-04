#!/usr/bin/env python
# coding: utf-8

import time
import os
import sys
import collections
import datetime
from boxsdk import OAuth2, Client
import requests
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from cloudant.document import Document
import logging

logging.basicConfig(stream=sys.stdout, level=int(os.environ['LOG_LEVEL']))

box_client_id=os.environ['BOX_CLIENT_ID']
box_client_secret = os.environ['BOX_CLIENT_SECRET']
callback_url = os.environ['BOX_CALLBACK_URL']

CLOUDANT_USER = os.environ['CLOUDANT_USER']
CLOUDANT_PASSWORD = os.environ['CLOUDANT_PASSWORD']
CLOUDANT_URL_ROOT_PUBLIC = os.environ['CLOUDANT_URL_ROOT_PUBLIC']
cloudant_url = "https://{0}:{1}@{0}{2}".format(CLOUDANT_USER, CLOUDANT_PASSWORD, CLOUDANT_URL_ROOT_PUBLIC)
cloudant_client = Cloudant(CLOUDANT_USER, CLOUDANT_PASSWORD, url=cloudant_url)
cloudant_box_token = os.environ['CLOUDANT_BOX_TOKEN'] #'boxtoken'

# create the database for box token
# the boxtoken database, the _id should be the client id
#my_database = cloudant_client.create_database(cloudant_box_token)

def save_token_2_cloudant(atrt, box_client_id = box_client_id, cloudant_box_token = cloudant_box_token):
    cloudant_client.connect()
    save_token = {"_id": box_client_id, "access_token": atrt[0], "refresh_token": atrt[1]}
    logging.debug("token to be saved" + str(save_token))
    my_database = cloudant_client.get(cloudant_box_token, cloudant_client.create_database(cloudant_box_token))  # if database does not exist, then create it
    if box_client_id not in my_database:
        logging.debug('box client id {} NOT found in database'.format(box_client_id))
        document = my_database.create_document(save_token)
    else:
        logging.debug('box client id {} found in database'.format(box_client_id))
        document = my_database[box_client_id]
        document['access_token'] = atrt[0]
        document['refresh_token'] = atrt[1]
        document.save()

    logging.debug('box token {} is saved in database {}'.format(document, cloudant_box_token))
    cloudant_client.disconnect()

def get_token_from_cloudant(box_client_id = box_client_id, cloudant_box_token = cloudant_box_token):
    #my_database = list(cloudant_client[cloudant_box_token])
    #save_token = list(filter(lambda x: x['_id'] == box_client_id, my_database))[0]
    cloudant_client.connect()
    my_database = cloudant_client[cloudant_box_token]
    if box_client_id not in my_database:
        document = my_database[box_client_id]
        atrt = document['access_token'], document['refresh_token']
        logging.error('atrt is {}'.format(atrt))
        logging.error('the client id {} is not found in cloudant database, please do the oAuth2 process to update cloudant database!!!'.format(box_client_id))
    else:
        document = my_database[box_client_id]
        atrt = document['access_token'], document['refresh_token']
        logging.debug('atrt retrieve from the get_token_from_cloudant function is' + str(atrt))
    cloudant_client.disconnect()
    return atrt

def get_authcode():
    oauth0 = OAuth2(
        client_id=box_client_id,
        client_secret=box_client_secret
    )
    logging.debug(box_client_id)
    logging.debug("callback  url is: \n\n {}".format(callback_url))

    auth_url, csrf_token = oauth0.get_authorization_url('{}/authcode2_token_file'.format(callback_url))
    logging.debug(auth_url+ csrf_token)
    return auth_url, csrf_token

def authcode2_token_file(code):
    oauth0 = OAuth2(
        client_id=box_client_id,
        client_secret=box_client_secret
    )

    atrt = oauth0.authenticate(code)
    save_token_2_cloudant(atrt)
#    with open('BOX/cache/save_token.txt', 'w') as f:
#        f.write('#'.join(atrt))

def refresh_token(atrt):
    '''
    refresh_token function takes a tuple of tokens (access token and refresh token) and refresh it so that we always have the correct at and rt

    input: tuple of access token and refresh token
    return: tuple of access token and refresh token
    '''
    at = atrt[0]
    rt = atrt[1]
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': rt,
        'client_id': box_client_id,
        'client_secret': box_client_secret
    }
    res = requests.post('https://api.box.com/oauth2/token', data = data)
    logging.debug('response from the function refresh_token is {}'.format(str(res)))
    at = res.json()['access_token']
    rt = res.json()['refresh_token']
    #store_tokens(at, rt)
    return at, rt


def get_box_client():
    '''
    get_box_client function retrieve the token from the cloudant database 'boxtoken' as the token tuple. it will read the contents and then refresh it and then save it back to cloudant database
    Input: None
    return: authorized client
    '''
    logging.info('entering get_box_client function...')
#    atrt = open('BOX/cache/save_token.txt', 'r').read().strip().split('#')
    atrt = get_token_from_cloudant()
    logging.debug('the access token received from the get_token_from_cloudant fucntion is: ' + str(atrt))
    atrt = refresh_token(atrt)
    oauth = OAuth2(
        client_id=box_client_id,
        client_secret=box_client_secret,
        access_token = atrt[0]
    )

    save_token_2_cloudant(atrt)
    #with open('BOX/cache/save_token.txt', 'w') as f:
    #    f.write('#'.join(atrt))
    client = Client(oauth)
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
    folder_id = '67003744201' #  odmmeta_share/temp_data
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

