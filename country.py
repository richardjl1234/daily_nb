'''
this application is to refresh the text file in country.txt

also update the meta/country.csv file
usage:
    python country.py

'''
import datetime
import sys
sys.path.append('/odm_modules')
from common_func import odm_conn
import pandas as pd


sql = open('sql/country.sql', 'r').read()

#with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
#    result = odmprd_adhoc(sql)

result = odm_conn.odmprd_sql(sql)

df = pd.DataFrame( result)
df.fillna('', inplace = True)
df = df.applymap(lambda v:
        str(v).strip() if isinstance(v, (int))
        #else str(round(v,0)) if isinstance(v,float)
        else str(int(v)).strip() if isinstance(v,float)
        else str(v.date()).strip() if isinstance(v, datetime.date)
        else v.strip())

pd.options.display.max_rows = 1000
pd.options.display.max_columns = 200
pd.options.display.width = 1000

df = df.loc[:,['CCOMPAIW','CCQ','CFDRSRC','CNT_A','CNT_I','CNT_N','MAX_CNUM','MIN_CNUM','MODEL2','MODEL3','MODEL4','PSC','TBDSCOMP','TISOCTRY']]
with open('country_n.txt', 'w') as f:
#    sys.stdout = f
    f.write(str(df))
    #print >>f,   df

df.to_csv('meta/country.csv', index = False)

