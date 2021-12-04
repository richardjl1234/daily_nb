'''
this application is to read the RZ1 table and then get the contents into tid dictionary
this application is to read the RZ2 table and then get the contents into tid dictionary

there are the following 4 functions
refresh() is to call all the 4 refresh functions
odm_tid_dict_refresh()
odm_col_dict_refresh()
odm_tid_df_from_csv()
odm_col_df_from_csv()
tid_gen()
col_gen()

refresh() is to get all csv file refreshed, and save it in the folder /odm_modules/common_func/meta

xxx_refresh is to get the data from the RZ1 or RZ2 table and also save the contents into csv file
xxx_from_csv is to get the data from the csv file
odm_col_df_from_csv  to return a dataframe, which combine the information from rz2 as well as syscolomuns information
odm_tid_df_from_csv to return a dataframe, which combines the infromation from rz1 as well as systables information
tid_gen is a generater and return a function which can take tid as parameter..
col_gen is a generator and return a function which can take col as parameter
'''
import sys
sys.path.append('/odm_modules')  # odm common_func modules should be placed in this top level folder
from common_func import odm_conn
import pandas as pd
from addict import Dict
import datetime

schema_list = ['ODMPRD']
col_csv_file_name = '/odm_modules/common_func/meta/col.csv'
tid_csv_file_name = '/odm_modules/common_func/meta/tid.csv'
systb_csv_file_name = '/odm_modules/common_func/meta/systb.csv'
syscol_csv_file_name = '/odm_modules/common_func/meta/syscol.csv'

# python 3
cell_format = lambda v: str(v) if isinstance(v, (int)) else str(int(v)) if isinstance(v,float) else str(v.date()) if isinstance(v, datetime.date) else v.strip()
# python 2
#cell_format = lambda v: str(v) if isinstance(v, (int)) else str(int(v)) if isinstance(v,float) else str(v.date()) if isinstance(v, datetime.date) else v.strip().decode('utf-8')


def odm_tid_dict_refresh():
    with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
        results = odmprd_adhoc('select ctid, ctabname, ttid from odmprd.odmt_ddict_tables')
    print( 'the tid_dict is prepared!!')
    df = pd.DataFrame(results)
    df = df.applymap(cell_format)
    df.set_index('CTID', inplace = True)
    tid_dict = Dict(df.to_dict(orient = 'index'))
    df.to_csv(tid_csv_file_name)
    print( 'the tid csv file is written into /odm_modules/common_func/meta/tid.csv file')
    return tid_dict
def odm_col_dict_refresh():
    with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
        results = odmprd_adhoc(''' select rz2.ctid,rz1.ctabname, ccolname, tcolname, cclass from odmprd.odmt_ddict_columns rz2, odmprd.odmt_ddict_tables rz1 where rz1.ctid = rz2.ctid    ''')
    print( 'the col_dict is prepared!!')
    df = pd.DataFrame(results)
    df = df.applymap(cell_format)
    df.set_index(['CTID', 'CCOLNAME'], inplace = True)
    col_dict = Dict(df.to_dict(orient = 'index'))
    df.to_csv(col_csv_file_name)
    print( 'the col csv file is written into /odm_modules/common_func/meta/col.csv file')
    return col_dict
def odm_systb_dict_refresh():
    with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
        condition  = ', '.join([ "'{}'".format(schema) for schema in schema_list ])
        print( condition)
        sql = """select name, creator, type, dbname, tsname, createdts, alteredts, spacef from sysibm.systables where creator in ({}) """.format(condition)
        results = odmprd_adhoc(sql)
    print( 'the systb_dict is prepared!!')
    df = pd.DataFrame(results)
    df = df.applymap(cell_format)
    df.set_index('NAME', inplace = True)
    systb_dict = Dict(df.to_dict(orient = 'index'))
    # write to csv file
    df.to_csv(systb_csv_file_name)
    print( 'the sys table csv file is written into /odm_modules/common_func/meta/systb.csv file')
    return systb_dict
def odm_syscol_dict_refresh():
    with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
        condition  = ', '.join([ "'{}'".format(schema) for schema in schema_list ])
        print( condition)
        sql = """select name, tbname, tbcreator, colno, coltype, length, default, keyseq, createdts, alteredts from sysibm.syscolumns where tbcreator in ({}) """.format(condition)
        results = odmprd_adhoc(sql)
    print( 'the syscol_dict is prepared!!')
    df = pd.DataFrame(results)
    df = df.applymap(cell_format)
    df.set_index(['TBNAME', 'NAME'], inplace = True)
    syscol_dict = Dict(df.to_dict(orient = 'index'))
    # write to csv file
    df.to_csv(syscol_csv_file_name, encoding = 'UTF_8')
    print( 'the sys table csv file is written into /odm_modules/common_func/meta/syscol.csv file')
    return syscol_dict
def refresh():
    odm_tid_dict_refresh()
    odm_col_dict_refresh()
    odm_systb_dict_refresh()
    odm_syscol_dict_refresh()

def odm_tid_df_from_csv():
    tid_df = pd.read_csv(tid_csv_file_name)
    systb_df = pd.read_csv(systb_csv_file_name)
    tid_df = tid_df.merge(systb_df, left_on = 'CTABNAME', right_on = 'NAME', how = 'outer')
    #tid_df.set_index('CTID', inplace = True)
    #tid_df.drop(columns = ['CTABNAME'], inplace = True)
    tid_df = tid_df.fillna('')
    return tid_df

def odm_col_df_from_csv():
    col_df = pd.read_csv(col_csv_file_name)
    syscol_df = pd.read_csv(syscol_csv_file_name)
    col_df = col_df.merge(syscol_df, left_on = ['CTABNAME', 'CCOLNAME'], right_on = ['TBNAME', 'NAME'], how = 'outer')
    #col_df.set_index(['CTID', 'CTABNAME', 'CCOLNAME'], inplace = True)
    #col_df.drop(columns = ['CTABNAME', 'CCOLNAME'], inplace = True)
    col_df = col_df.fillna('')
    return col_df

def tid_gen():
    def tid(id):
        tid_df = odm_tid_df_from_csv()
        tid_df = tid_df.loc[tid_df.CTID == id]
        #print(tid_df)
        return tid_df
    return tid


def col_gen():
    def col(id):
        col_df = odm_col_df_from_csv()
        #col_df = col_df.loc[col_df.CTID == id].sort_values('COLNO')
        col_df = col_df.loc[col_df.CTID == id]
        #print(col_df)
        return col_df
    return col

if __name__ == '__main__':
    refresh()
    #tid_df = odm_tid_df_from_csv()
    #col_df = odm_col_df_from_csv()
    #col = col_gen()
    #tid = tid_gen()

