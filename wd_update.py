'''
This is a lite version for workday data change (update) request.
1. It will read the file from box folder directly.
2. It will just prepare the SQL statement. figout all the entries which are with the "in-processing" status
3. It will also print out the text informat which you can copy to the Jira story. 
4. rtc ticket number is optional. If there are multiple 'in-processing' update ticket, then give the rtc ticket number in the command line

No need to use the docker image. 
'''

import datetime
import pandas as pd
import sys
import os
sys.path.append('/odm_modules')
from common_func import odm_conn as odm
from common_func import odm_ftp as odm_ftp
from common_func import cloudant_conn as cc
from common_func import box_oauth as box

file_id = '731566115825'
client = box.get_box_client()
pd.read_excel(client.file(file_id).content())


def cell_format(v):
    return str(v) if isinstance(v, (int)) else str(int(v)) if isinstance(v,float) else str(v.date()) if isinstance(v, datetime.date) else v.decode('utf-8') if isinstance(v, bytes) else '' if v is None else v.strip()


xlsx_name = sys.argv[1]
rtc_num_default = sys.argv[2] if len(sys.argv)  ==3 else ''
print( 'rtc ticket number given in command line is: ', rtc_num_default)

# step 1, read the cloudspreadsheet into dataframe.
# make sure the format from the spreadsheet is correctly loaded in df with correct format.

request_df = pd.read_excel(client.file(file_id).content(), header = 1, sheet_name = 'Manual Action request').fillna('')
cat_df = pd.read_excel(client.file(file_id).content(), sheet_name = 1, header = 1, dtype = str).fillna('')
