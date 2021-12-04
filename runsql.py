#import  dotenv
import pandas as pd
import datetime

import sys
sys.path.append('/odm_modules') # include this library so that common_func package can be searched
from common_func import odm_conn as odm

# get the file name, db name from the command line.
if len(sys.argv) <=1:
    print( 'No enough parameter is given in the command line')
    print( 'Usage: python runsql.py prd|uat')
    exit()

env = sys.argv[1]
env = 'prod' if env == 'prd' else 'uat'
with open('input/adhoc_sql.sql', 'r') as f:
    sqls = f.read().split(';')

sqls = [sql.strip() for sql in sqls]
sqls = list(filter(lambda sql: sql !='' , sqls))
for sql in sqls:
    print( sql)
    print()

with odm.odm_adhoc(env) as odmprd_adhoc:
    results = [odmprd_adhoc(sql) for sql in sqls]


dfs = [pd.DataFrame(result).fillna('') for result in results]
pd.set_option('display.max_rows',None)

for df in dfs:
    print('-'*100)
    df = df.applymap(lambda v: str(v) if isinstance(v, (int))
            #else str(round(v,0)) if isinstance(v,float)
            else str(int(v)) if isinstance(v,float)
            else str(v) if isinstance(v, datetime.date)
            else v.strip())
    for col in filter(lambda col: col[0] == 'U' , df.columns) :
            df[col] = df[col].apply(lambda x: x.decode('utf-8'))
    print(df)
    print()
#pd.set_option('display.max_colwidth', -1)
#pd.set_option("display.colheader_justify","left")
#df.set_index(['USERID'], inplace = True)
#col_list =list( df.columns)
#
#col_list.remove('USERID')
#print pd.melt(df, id_vars = ['USERID'], value_vars = col_list).set_index(['USERID']).sort_index()
