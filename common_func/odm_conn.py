'''
this application is to build the connection to odm database
this module provides the following fucntions
1. odmprd_conn(),  return: db conntion hnadle
2. odmuat_conn(), return: db connection handle
3. odm_adhoc(env), env has to be prod or uat, return a function which takes sql statement as the parameter and return the query result in json format.

this module is already python2 and python3 compatible
'''
import sys
import ibm_db
from contextlib import contextmanager
import pandas as pd
import collections as cl
import os
import logging

logging.basicConfig(stream=sys.stdout, level=int(os.environ['LOG_LEVEL']))

odm_database_prod = os.environ['ODM_DATABASE_PROD']
odm_database_uat = os.environ['ODM_DATABASE_UAT']
odm_server_prod = os.environ['ODM_SERVER_PROD_SSL']
odm_server_uat = os.environ['ODM_SERVER_UAT_SSL']
odm_port_prod = os.environ['ODM_PORT_PROD_SSL']
odm_port_uat = os.environ['ODM_PORT_UAT_SSL']

arm_path = '/odm_modules/common_func/carootcert.arm'

@contextmanager
def odm_adhoc(env, odm_user = os.environ['USER'], odm_password = os.environ['PASSWORD']): #env can be 'uat' or 'prod', default user id and password will be retrieved from system variables
    conn_str_prod  = f" DATABASE= {odm_database_prod}; HOSTNAME={odm_server_prod}; PORT={odm_port_prod}; PROTOCOL=TCPIP; UID={odm_user}; PWD={odm_password}; sslservercertificate={arm_path}; SECURITY=ssl;"
    conn_str_uat   = f" DATABASE= {odm_database_uat}; HOSTNAME={odm_server_uat}; PORT={odm_port_uat}; PROTOCOL=TCPIP; UID={odm_user}; PWD={odm_password}; sslservercertificate={arm_path}; SECURITY=ssl;"
    logging.debug(f'{conn_str_prod=}')
    logging.debug(f'{conn_str_uat=}')

    conn = ibm_db.connect(conn_str_uat, "", "") if env == 'uat' else ibm_db.connect(conn_str_prod, "", "") if env == 'prod' else None

    def f_adhoc(sql_stmt):
        stmt = ibm_db.exec_immediate(conn,sql_stmt)
        results = []
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            result = cl.OrderedDict(result)
            results.append(result)
            result = ibm_db.fetch_assoc(stmt)
        return results
    try:
        logging.info( 'the db2 connection established... ')
        yield f_adhoc
    finally:
       ibm_db.close(conn) # close the connection after processing
       logging.info( 'the db2 connection destroyed...')

def odmprd_sql(sql):
    with odm_adhoc('prod') as adhoc:
        result = adhoc(sql)
    return result

def odmuat_sql(sql):
    with odm_adhoc('uat') as adhoc:
        result = adhoc(sql)
    return result

if __name__ == '__main__':
    logging.debug('-' * 20 + 'testing production connection' + '-' * 20)
    sql = '''
    select * from odmprd.odmt_address where rsernum = '0943511'
    '''
    with odm_adhoc('prod') as odmprd_adhoc:
        rsts = odmprd_adhoc(sql)
    print( rsts)
    df = pd.DataFrame(rsts)
    print(df)

    logging.debug('-' * 20 + 'testing uat connection' + '-' * 20)
    sql = '''
    select * from odmuat.odmt_domain
    '''
    with odm_adhoc('uat') as odmprd_adhoc:
        rsts = odmprd_adhoc(sql)
    print( rsts)
    df = pd.DataFrame(rsts)
    print(df)

    logging.info('-- testing odmprd_sql function --')
    sql = 'select * from odmprd.odmt_domain fetch first 10 rows only'
    result = odmprd_sql(sql)
    print(result)

    logging.info('-- testing odmuat_sql function --')
    sql = 'select * from odmuat.odmt_domain fetch first 10 rows only'
    result = odmuat_sql(sql)
    print(result)


