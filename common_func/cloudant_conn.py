'''
This module provide functions which to replicate data from dataframe or odm query result to cloudant database.

In general, we usually have a defualt user and password for cloudant database. but, we can always override it by specifying the user and password in the function

Function: df_2_cloudant(df, cloudant_db_name, converter = converter, keys = [], mode= 'REPLACE|APPEND', user = CLOUDANT_USER, password = CLOUDANT_PASSOWRD, drop_origin_keys = True)
        bring the dataframe into cloudant_db_name, the convert dictionary tells how to rename the field
        - df: dataframe to be populated into cloudant database
        - cloudant_db_name: is the cloudant database name which to be populated
        - keys : specify what are the keys in the dataframe. if specified, the fields in the keys will become the _id in the cloudant database
        - converter: is a dictionary which tells the mapping rule, from the original query result to key in cloudant db
        - mode: can be either REPLACE or APPEND, if REPLACE, then all the contents in the cloudant database will be removed
        - user, password will take the CLOUDANT_USER and CLOUDANT_PASSWORD as default user and password
        - drop_origin_keys : default is true. the keys will go to _id field, so no need to keep them in the cloudant database

Function: odm_2_cloudant(query, odm_env, cloudant_db_name, converter = converter,keys = [],  mode= 'REPLACE|APPEND', user = CLOUDANT_USER, password = CLOUDANT_PASSOWRD, drop_origin_keys = True)
        bring the query result into cloudant_db_name, the convert dictionary tells how to rename the field
        - query: is s sql query which is to retrieve query result from ODM database (stfmvs1)
        - odm_env: can either 'uat' or 'prod'
        - cloudant_db_name: is the cloudant database name which to be populated
        - keys : specify what are the keys in the query result. if specified, the fields in the keys will become the _id in the cloudant database
        - converter: is a dictionary which tells the mapping rule, from the original query result to key in cloudant db
        - mode: can be either REPLACE or APPEND, if REPLACE, then all the contents in the cloudant database will be removed
        - user, password will take the CLOUDANT_USER and CLOUDANT_PASSWORD as default user and password
        - drop_origin_keys : default is true. the keys will go to _id field, so no need to keep them in the cloudant database
        bring the contents from odm database to cloudant database

'''


import sys
sys.path.append('/odm_modules')
from contextlib import contextmanager
import pandas as pd
import collections as cl
import os
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from cloudant.document import Document
from common_func import odm_conn
import logging
import datetime


CLOUDANT_USER = os.environ['CLOUDANT_USER']
CLOUDANT_PASSWORD = os.environ['CLOUDANT_PASSWORD']
LOG_LEVEL = int(os.environ['LOG_LEVEL'])
url = "https://{0}:{1}@{0}.cloudant.com".format(CLOUDANT_USER, CLOUDANT_PASSWORD)

logging.basicConfig(level=LOG_LEVEL,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='cloudant_conn.log',
                filemode='w')
console = logging.StreamHandler()
console.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(levelname)-8s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
cell_format = lambda v: str(v) if isinstance(v, (int)) else str(int(v)) if isinstance(v,float) else str(v.date()) if isinstance(v, datetime.date) else v.strip() if isinstance(v, str) else v.decode('utf-8').strip()
cloudant_client = Cloudant(CLOUDANT_USER, CLOUDANT_PASSWORD, url=url)

def df_2_cloudant(df, cloud_db_name, keys = [],  converter={}, mode = 'REPLACE', src_code = '', user = CLOUDANT_USER, password = CLOUDANT_PASSWORD, drop_origin_keys = True):
    client = Cloudant(CLOUDANT_USER, CLOUDANT_PASSWORD, url=url)
    client.connect()
    df = df.fillna('').applymap(cell_format)

    logging.debug('df.types is {}'.format(df.dtypes))
    df.rename(columns = converter, inplace = True)
    df['src'] = src_code
    logging.debug('result is : \n {}'.format(df))
    if mode == 'REPLACE' :
        my_database = client.create_database(cloud_db_name)
        if my_database.exists():
            client.delete_database(cloud_db_name)
            print('the mode is REPLACE, the existing database {} is deleted!'.format(cloud_db_name))
    my_database = client.get(cloud_db_name, client.create_database(cloud_db_name))  # if database does not exist, then create it
    if len(keys) != 0:
        logging.debug('original key is {}'.format(keys))
        mapped_keys = [converter.get(key, key) for key in keys]
        logging.debug('mapped keys is {}'.format(mapped_keys))
        if not all([key in df.columns for key in mapped_keys]):
            logging.error('the keys specified is not a columns in the result set, program aborted! \nkey is {},\n mapped keys is {}, \ncolumns are {}...'.format(keys, mapped_keys, df.columns))
            return {'status': False, 'count' :0 }
        else:
            logging.debug(mapped_keys)
            df['_id'] = df[mapped_keys].apply(lambda y: '.'.join(y), axis = 1)
            if drop_origin_keys:
                df.drop(columns = mapped_keys, inplace = True)
                print('the drop_origin_keys flag is True, the keys {} are removed and not loaded into cloudant database'.format(mapped_keys))
            #df.rename(columns = {mapped_key: '_id'}, inplace = True)
            df_dict_list = df.T.to_dict().values()
            logging.debug('the result dict is \n {}'.format(df_dict_list))
            my_database.bulk_docs(list(df_dict_list))
            count = df.shape[0]
    else:  # if key is not specified, then directly
        logging.debug('the df is {}'.format(df.head(2)))
        df_dict_list = df.T.to_dict().values()
        logging.debug('the result dict is \n {}'.format(df_dict_list))
        my_database.bulk_docs(list(df_dict_list))
        count = df.shape[0]
    return {'success': True, 'count': count}

def odm_2_cloudant(query, odm_env, cloud_db_name, keys = [],  converter={}, mode = 'REPLACE', src_code = '', user = CLOUDANT_USER, password = CLOUDANT_PASSWORD, drop_origin_keys = True):
    with odm_conn.odm_adhoc(odm_env) as odmprd_adhoc:
        result = odmprd_adhoc(query)
    df = pd.DataFrame(result).applymap(cell_format)
    return df_2_cloudant(df, cloud_db_name, keys = keys, converter = converter, mode = mode, src_code = src_code, user = user, password = password, drop_origin_keys = drop_origin_keys)

if __name__ == '__main__':
    query_rz1 = "select CTID, CTABNAME, TTID, UTID from odmprd.odmt_ddict_tables fetch first 2 rows only ;  "
    converter_rz1 = {'CTABNAME': 'table name', 'TTID': "description"}
    res =  odm_2_cloudant(query_rz1, 'prod', 'temp3', converter = converter_rz1, keys = ['CTID'] , mode = 'REPLACE', src_code = 'RZ1')
    print(res)

    query_rz2 = "select CTID, CCOLNAME, CCOLFMT, TCOLNAME, CCLASS, CKEY, COLNO, TEXTRA from odmprd.odmt_ddict_columns where fdiscont <> 'Y' and CLANGUAG = ''  fetch first 10 rows only ; "
    converter_rz2 = {
            'CTID': 'table id',
            'CCOLNAME': 'column name',
            'CCOLFMT': 'format',
            'TCOLNAME': 'description',
            'CCLASS': 'data class',
            'CKEY': 'key field',
            'COLNO': 'column number',
            'TEXTRA': 'extra information'
            }
    logging.debug('now in RZ2 program')
    res = odm_2_cloudant(query_rz2, 'prod', 'temp3',  converter = converter_rz2, keys = ['CTID', 'CCOLNAME'] , mode = 'APPEND', src_code = 'RZ2')
    print(res)

    res  = df_2_cloudant(pd.read_excel('interface.xlsx', sheet_name = 'active_interfaces'), 'interface1')
    print(res)

