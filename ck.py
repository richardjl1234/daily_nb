''' This application is to check the existence in ODM database, either PROD or UAT
It accept 2 parameters, prd or uat
and then CNUM (9 char in length) or s/n (6 char or 7 char in length)

Usage: ./ck.py prd|uat cnum[,cnum,cnum] [col,col,col]
example:
    python ./ck.py prd 943511672,123456789 CCOMPAIW,CORGWWIW [err ed]
    python ./ck.py prd 943511,123456 CCOMPAIW,CORGWWIW
    python ./ck.py prd 0943511,0123456 CCOMPAIW,CORGWWIW
'''

import requests
import re
import json
from collections import defaultdict
import pandas as pd
import numpy as np
#import datetime
from datetime import datetime, timedelta, date
import collections
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

sys.path.append('/odm_modules') # include this library so that common_func package can be searched
from common_func import odm_conn as odm
from common_func import odm_ftp



def check_err_report(fname, sn_list):
    report = open(fname, 'r').readlines()
    p1 = re.compile(r'.*Date\:\s+(\S+)\s*', re.I)
    p2 = re.compile(r'.*Feedtype\: (\S) ', re.I)
    m1 = [ p1.match(line) for line in report]
    m2 = [ p2.match(line) for line in report]
    for i in m1:
        if i:
            print( 'Date: ', i.groups()[0],)

    for i in m2:
        if i:
            print( ' Feeder Type:', 'Full feed' if i.groups()[0] == 'F' else 'Delta feed')
    for sn in sn_list:
        print( sn)
        for line in report:
            if sn in line:
                print( line)

    return

def get_err_report(fdr):
    server_fname = 'ODMAP.RES.{}.ERRORREP'.format(fdr[0])
    report_template_name = 'temp/{}_report{}.txt'
    print( server_fname)
    sn_list = fdr[1]
    with odm_ftp.odm_ftp_conn('get') as odm_get_file:
        list(map(lambda i: odm_get_file(fm=server_fname+'({})'.format(-1*i),  to = report_template_name.format(fdr[0],i )), range(5)))

    list(map(lambda fn: check_err_report(fn, sn_list),  [ report_template_name.format(fdr[0], i) for i in range(6)]))

# get the file name, db name from the command line.
if len(sys.argv) <=2:
    print( 'No enough parameter is given in the command line')
    print( 'Usage: ./ck.py prd|uat cnum[,cnum,cnum] [col,col,col]')
    exit()

default_col_list = ['RCNUM', 'TNAMLAST', 'TNAMFRST', 'CACTIVE', 'CFDRSRC', 'DUPDATE', 'RPERSID', 'RSERNUM']

env = sys.argv[1]
cnum_list = sys.argv[2].strip(',').split(',') # ignore the ending ','


for cnum in cnum_list:
    if len(cnum) not in [9, 6, 7]:
        print( 'cnum length is not 6, 7 or 9, the length is {}, program aborted! '.format(cnum))
        exit()

if env not in ['prd', 'uat']:
    print( 'the environment must be prd or uat, the provide env is {}, program aborted!'.format(env))
    exit()

col_list = sys.argv[3].split(',') if len(sys.argv) >=4 else []
print( col_list)
col_list = [col.upper() for col in col_list]

col_list = list(filter(lambda x: x not in ['ERR', 'ED']   ,col_list)  )# remove the err and ed since it is other parameter not related to ODM data fields

for field in col_list:
    if field not in default_col_list:
        default_col_list.append(field)
default_col_list_in_query = ', '.join(default_col_list)  # this is used in the query

default_col_list_nise = default_col_list[:]
default_col_list_nise.remove('DUPDATE')
default_col_list_nise.remove('CFDRSRC')
default_col_list_in_query_nise = ', '.join(default_col_list_nise)  # this is used in the query

env = 'prod' if env == 'prd' else 'uat'
print( 'Environment is: ', env)

cnum_list_7 = [ cnum if len(cnum) == 7 else '0'+ cnum for cnum in cnum_list if len(cnum) in [6,7]]  # always pad with leading 0 for the s/n with 6 char in length
cnum_list_9 = list(filter(lambda cnum: len(cnum) == 9, cnum_list))

cnum_list_7_quote = list(map(lambda sn:   "'{}'".format(sn), cnum_list_7))
cnum_list_7_quote = ["'begin'"] + cnum_list_7_quote + ["'end'"]
cnum_list_7_condition = ', '.join(cnum_list_7_quote)

cnum_list_9_quote = list(map(lambda sn:   "'{}'".format(sn), cnum_list_9))
cnum_list_9_quote = ["'begin'"] + cnum_list_9_quote + ["'end'"]
cnum_list_9_condition = ', '.join(cnum_list_9_quote)

#cnum_list_condition = ', \n'.join( ["'{}'".format(cnum) for cnum in cnum_list])
sql = ''' select {} FROM {}.ODMT_EMPLOYEE \nWHERE RCNUM IN ( {} )  OR RSERNUM IN ({}) \n
 '''.format(default_col_list_in_query, 'ODMPRD' if env == 'prod' else 'ODMUAT',cnum_list_9_condition, cnum_list_7_condition)

print( 'sql is: \n {} '.format(sql))

sql_nise = ''' select {} FROM {}.ODMT_NISE_EMPLOYEE \nWHERE RCNUM IN ( {} )  OR RSERNUM IN ({}) \n
 '''.format(default_col_list_in_query_nise, 'ODMPRD' if env == 'prod' else 'ODMUAT',cnum_list_9_condition, cnum_list_7_condition)

with odm.odm_adhoc(env) as odmprd_adhoc:
    result_raw = odmprd_adhoc(sql)
    if 'nonise' not in sys.argv:
        result_raw_nise = odmprd_adhoc(sql_nise)
        df_nise = pd.DataFrame(result_raw_nise)
        if df_nise.shape[0] > 0:
            df_nise['CFDRSRC'] = 'HN1'
    else:
        df_nise = pd.DataFrame({})

df = pd.DataFrame(result_raw)
df = pd.concat([df, df_nise]).fillna('')

if len(df) != 0:
    df = df.loc[:, default_col_list]
else:
    print( 'no records in reuslt!')

col_mapping = {'TNAMLAST': 'LAST_NAME', 'TNAMFRST': 'FRST_NAME'}
default_col_list = [ col if col not in col_mapping else col_mapping[col]  for col in default_col_list]
df.rename(columns= col_mapping, inplace = True)
df.fillna('')
#df['LAST_NAME'] = df.LAST_NAME.apply(lambda x: x.encode('utf-8'))
#df['FRST_NAME'] = df.FRST_NAME.apply(lambda x: x.encode('utf-8'))
print()

#if len(df) != 0:
#    df_no_rsernum = df.drop(columns = ['RSERNUM'])
#    df_no_rsernum = df.drop(columns = [])
#else:
#    df_no_rsernum = df

df_no_rsernum = df

pd.set_option('display.max_rows',None)
#pd.set_option('display.max_colwidth', -1)
pd.set_option("display.colheader_justify","left")
if len(df) != 0:
    print( df_no_rsernum.set_index('RCNUM'))
#df = df.stack()
results = df_no_rsernum.to_dict(orient = 'records')
# reformat the result in the results data-> str, int -> str
results = [{k:(str(v) if isinstance(v, (int,float, date)) else v.strip())
                for k,v in i.items()}
                for i in results]

print()
print( 'formatted printing as below')
#default_col_list.remove('RSERNUM')
def f(row):
    print( '-' * 40)
    for col in default_col_list:
        print( '%-20s %-20s' % (col, row[col]))
    print()

list(map(f, results))

# last step, check the result against the original list given to see any record is missing.
if len(df) != 0:
    cnums_in_result = df.RCNUM.to_dict()
    sn_in_result = df.RSERNUM.to_dict()
    cnums_in_result = set([ v.strip()   for k,v in cnums_in_result.items()])
    sn_in_result = set([ v.strip()   for k,v in sn_in_result.items()])
else:
    cnums_in_result = set({})
    sn_in_result = set({})

cnum_list_9 = set(cnum_list_9)
cnum_list_7 = set(cnum_list_7)

print( 'the following cnums can not be found in ODM database:')

cnum_list_9_nf = cnum_list_9 - cnums_in_result
for i in cnum_list_9_nf:
    print( i)

days = 5
print( 'the following cnums can be found in ODM database but the dupdate is older than {} days from now:'.format(days))
cnum_list_9_old = set([ row['RCNUM'].strip() for row in result_raw if datetime.now() - datetime.combine(row['DUPDATE'], datetime.min.time()) > timedelta(days=days)] )
for i in cnum_list_9_old:
    print( i)

cnum_list_9_nf = cnum_list_9_nf | cnum_list_9_old


print( 'the following sn can not be found in ODM database:')
for i in (cnum_list_7 - sn_in_result) :
    print( i)

# step to get all the potential fdr code for each cnum_9
print( '-' * 30)
psc_sn_list = [  (cnum[6:], cnum[:6])  for cnum in cnum_list_9_nf]
psc_sn_dict = collections.defaultdict(list)
for psc, sn in psc_sn_list:
    psc_sn_dict[psc].append(sn)

print( psc_sn_list)

print( '-' * 30)
print( psc_sn_dict)

print( sys.argv)
if 'err' in sys.argv:
    country_df = pd.read_csv('meta/country.csv')
    for psc, sn_list in psc_sn_dict.items():
        print( '*' * 40)
        print( 'checking error messages for cnum {}... '.format( ','.join([sn+psc for sn in sn_list])))
        print( 'psc, sn_list: ', psc, sn_list)
        country_df_filtered = country_df[country_df.PSC == psc].dropna(subset= ['CNT_A']).loc[:, [ 'CFDRSRC', 'PSC']].drop_duplicates()
        psc_dict = country_df_filtered.to_dict(orient = 'records')
        #print( psc_dict)
        fdr_list = [(i['CFDRSRC'][1:], sn_list) for i in psc_dict]
        #print( fdr_list)
        list(map(get_err_report, fdr_list))

payload_list = [{'byCnum': cnum_9} for cnum_9 in cnum_list_9]
print( payload_list)

with open('temp_result.txt', 'w') as f_temp:
    def edir_api(payload):
        r = requests.get('http://bluepages.ibm.com/BpHttpApisv3/wsapi', params = payload)
        if r.status_code == 200:
            print( r.text)
            f_temp.write(r.text)
            line_list =  r.text.split('\n')
            line_list = '\n'.join([line.replace(':', '|', 1) for line in line_list])
            text = StringIO(line_list)
            if 'count=0' not in line_list:
                ser = pd.read_csv(text, sep= '|', header = None, index_col = 0, squeeze=True, comment = '#' , skip_blank_lines=True)
                print( 'ser is \n', ser)
                return ser
            else:
                print( 'empty series!!')
                return pd.Series({})
        else:
            print( ('r.status_code is {}'.format(r.status_code)))
            return None

    if 'ed' in sys.argv:
        ser_list = list(map(edir_api, payload_list))
        df_ed = pd.DataFrame(ser_list).fillna('')
        df_ed=  df_ed.loc[:, ['CNUM', 'NAME', 'DIRECTORY', 'COUNTRY', 'INTERNET']] if not df_ed.empty else pd.DataFrame([{}])
        df_ed.to_excel('temp_result.xlsx', index = False)
        print( df_ed)
