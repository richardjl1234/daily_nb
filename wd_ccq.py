import sys
import datetime as dt
sys.path.append('/odm_modules')
import pandas as pd
from common_func import odm_conn

def p_tempcsv():
    with open('temp.csv' , 'r') as f:
        lines = f.readlines()
        lines = list(map(lambda x: '| {} |'.format(x.strip()), lines))
        print('\n'.join(lines))
        print('&nbsp;')


if len(sys.argv) <=1:
    print( 'No sufficient parameters in the command line!')
    print( 'usage: python rek_del.py  input/cloud_sheet.xlsx [1234567]')

xlsx_name = sys.argv[1]
rtc_num_default = sys.argv[2] if len(sys.argv) == 3 else ''
### STEP 1 read the cloud spreadsheet and read contents into df
#my_str = lambda x: x.strip() if type(x) == str else x.encode('utf-8') if type(x) == unicode else str(x)

df = pd.read_excel(xlsx_name, header = 2).fillna('')
df = df.loc[(df.CMODEL == 'IBM') & (df.status == 'In Processing'), :]

print('*Zendesk Ticket*  ')
zen_list = df.COE_zendesk_number.astype(str).unique()
print('\n'.join(zen_list))

print('\n&nbsp;\n')
print('\n&nbsp;\n')

df['=>'] = '=>'
df_map = df.loc[:, ['CCOUNTRY', 'CCOUNTRQ', 'RSERNUM', '=>', 'NCOUNTRY', 'NCOUNTRQ', 'NSERNUM']].applymap(str).applymap(lambda x: ' ' if x =='' else x)
#print(df_map.sort_values('RSERNUM').reset_index(drop = True))
df_map.sort_values('RSERNUM').reset_index(drop = True).to_csv('temp.csv', sep = '|', index = False)
p_tempcsv()

print()
print()

df_map = df.loc[:, ['CCOUNTRY', 'CCOUNTRQ', 'RSERNUM', 'NCOUNTRY', 'NCOUNTRQ', 'NSERNUM']].applymap(str)

df_x = df.loc[:, ['CCOUNTRY', 'CCOUNTRQ', 'RSERNUM']].applymap(str)
conditions = [ """ (CCOUNTRY = '{}' AND CCOUNTRQ = '{}' AND RSERNUM = '{}') """.format(*row)  for i, row in df_x.iterrows()]
conditions = ' OR '.join(conditions)

field_list =['RCNUM', 'TNAMLAST', 'TNAMFRST', 'CACTIVE', 'DUPDATE', 'CFDRSRC', 'CCOUNTRY', 'CCOUNTRQ', 'RSERNUM']
sql = '''select {} from ODMPRD.ODMT_EMPLOYEE where {} ORDER BY RSERNUM'''.format(', '.join(field_list), conditions)
print(f'{sql=}')

rek_sql = '''select * from odmprd.odmt_emp_keychange where fdiscont <> 'Y' and clanguag = '' '''


with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
    result = odmprd_adhoc(sql)
    rek_res =  odmprd_adhoc(rek_sql)

df_result = pd.DataFrame(result)


def cell_format(v):
    return str(v) if isinstance(v, int) else str(int(v)) if isinstance(v,float) else str(v) if isinstance(v, dt.date) else v.decode('utf-8') if isinstance(v, bytes) else '' if v is None else v.strip()
#df_result = df_result.loc[:, field_list].applymap(str).applymap(lambda x: x.strip())
df_result = df_result.loc[:, field_list].applymap(cell_format).applymap(lambda x: ' ' if x == '' else x)
df_result.to_csv('temp.csv', sep = '|', index = False, encoding = 'utf-8')
#df_result.sort_values('RSERNUM').reset_index(drop = True).
df_rek = pd.DataFrame(rek_res)

print
print('Total impacted cnums are : {}'.format(len(df)))
print(''' *Query result before processing:* \n {}'''.format(f'_{sql}_ &nbsp;\n &nbsp;\n'))
p_tempcsv() # print the temp.csv in the format accepted by jira
print('We are going to use existing REK process to perform the deletion, no dry run is needed, the old data will be backuped in 2 datasets. &nbsp;\n')
print('\n' + '-' * 60)
print('the current entries in the REK table: ')
print(df_rek)

df_result_merged = df_result.merge(df_map, how = 'outer', on = ['CCOUNTRY', 'CCOUNTRQ', 'RSERNUM'])
print(df_result_merged)

cnum_list = df_result.RCNUM.unique()
cnum_list = ', '.join([ "'{}'".format(cnum) for cnum in cnum_list])
print(cnum_list)
sql_after = '''
select {}
from ODMPRD.ODMT_EMPLOYEE
where RCNUM in ({}) \nORDER BY RSERNUM '''.format(', '.join(field_list), cnum_list)
print('Query result after processing is:\n {}'.format(sql_after))
print

with odm_conn.odm_adhoc('prod') as odmprd_adhoc:
    result = odmprd_adhoc(sql)
df_after_result = pd.DataFrame(result)
#df_after_result = df_after_result.loc[:, field_list].applymap(str).applymap(lambda x: x.strip())
df_after_result = df_after_result.loc[:, field_list].applymap(cell_format)
print(df_after_result)


### merge the current request sheet with archive sheet
