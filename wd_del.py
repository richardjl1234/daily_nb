'''
This application is to read the cloud spreadsheet,
read the rek entries from rek table in odm production.
get the new entries from cloud spreadsheet and then merge them into rek.csv
then load back the csv file into rek table.
then trig the rek process to delete the records from ODM database.
rtc ticket number is optional.

usage: python ./wd_del.py input/cloud_sheet.xlsx [1234567]

### STEP 1 read the cloud spreadsheet and read contents into request_df
### STEP 2 filter all the in-processing entries and get those entries, if rct number is specified in the command line, the only process that story
### STEP 3 get the zen desk ticket number (get the information form the dataframe.
### STEP 4 get the category number, then use the sheet 2 -- category description sheet to get the description of each category
### STEP 5 get the cnum list from the dataframe.
### STEP 6 query the odm database for those cnums and print out the query result
### -------------------
### STEP 7 read the data from rek table, if there are some entries which FDISCONT <> 'Y', stop processing
### STEP 8 get the next sequence number from the result of REK and then add new entries into REK dataframe based on the request dataframe
### STEP 9 write the REK dataframe into csv file
### STEP 10 add the T, REK row in the first row of the csv file
### STEP 11 upload the csv file into ODMAP.RES.ZZ.RDMCSV.IN.EM and update the ODMSUBRJ to get ready to load the csv file
### STEP 12 prompt the message to inform user to run trig911 to upload the REK entries.

'''

### STEP 1 read the cloud spreadsheet and read contents into request_df
### STEP 2 filter all the in-processing entries and get those entries, if rct number is specified in the command line, the only process that story
### STEP 3 get the zen desk ticket number (get the information form the dataframe.
### STEP 4 get the category number, then use the sheet 2 -- category description sheet to get the description of each category
### STEP 5 get the cnum list from the dataframe.
### STEP 6-1 query the odm database for those cnums and print out the query result
### STEP 6-2 if the count of result is 0, then means the requests has been processing
### STEP 6-3 get input from terminal to determine if we proceed to get REK and update it
### -------------------
### STEP 7 read the data from rek table, if there are some entries which FDISCONT <> 'Y', stop processing
### STEP 8 get the next sequence number from the result of REK and then add new entries into REK dataframe based on the request dataframe
### STEP 9 write the REK dataframe into csv file
### STEP 10 add the T, REK row in the first row of the csv file
### STEP 11 upload the csv file into ODMAP.RES.ZZ.RDMCSV.IN.EM and update the ODMSUBRJ to get ready to load the csv file
### STEP 12 prompt the message to inform user to run trig911 to upload the REK entries.

import datetime
import pandas as pd
import sys
sys.path.append('/odm_modules')
from common_func import odm_conn as odm
from common_func import odm_ftp as odm_ftp

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

### STEP 1 read the cloud spreadsheet and read contents into request_df
#my_str = lambda x: x.strip() if type(x) == str else x.encode('utf-8') if type(x) == unicode else str(x)
my_str = lambda x: x.strip() if type(x) == str else str(x)

converters = {'RTC_task_number': my_str,  'new_value': my_str, 'COE_zendesk_number': my_str, 'COE_request_date': my_str, 'expected_due_date': my_str,   'old_value': my_str, 'action': my_str, 'email_COE_requestor': my_str, 'RCNUM': my_str, 'closure_date': my_str}

### read the archive spreadsheet
request_df_archive = pd.read_excel("input/archive/ODM_manual_delete_update_request_master_list_all.xlsx", header =1, sheet_name = "Manual Action request").fillna('')
request_df_archive = request_df_archive.applymap(lambda v: str(v) if isinstance(v, (int))
        #else str(round(v,0)) if isinstance(v,float)
        else str(int(v)) if isinstance(v,float)
        else str(v.date()) if isinstance(v, datetime.date)
        else v.strip())
print( "step 0, the archived requests is read, there are {} records in the archived spreadsheet".format(request_df_archive.shape[0]))
print( request_df_archive.head())


request_df = pd.read_excel(xlsx_name, header = 1, converters = converters).fillna('')
### merge the current request sheet with archive sheet
request_df_all = pd.concat([request_df_archive, request_df], sort = False)
request_df_all.RCNUM = request_df_all.RCNUM.astype(str)
print("step 1, the current request sheet is merged with archived spreadsheet, the total records is: {}".format(request_df_all.shape[0]))
#request_df = pd.read_excel(xlsx_name, header = 1).fillna('')


cat_df = pd.read_excel(xlsx_name, sheet_name = 1, header = 1, dtype = str).fillna('')

### STEP 2 filter all the in-processing entries and get those entries, if rct number is specified in the command line, the only process that story
## filter out all the in-processing entries and with action is D
if rtc_num_default != '':
    request_df = request_df[(request_df.status == 'In Processing') & (request_df.action =='D') & (request_df.RTC_task_number == rtc_num_default)]
else:
    request_df = request_df[(request_df.status == 'In Processing') & (request_df.action =='D')]

rtc_num = request_df.RTC_task_number.unique()
if len(rtc_num) != 1:
    print( 'the following rtc tickets number in the spreadsheet! {} ... '.format(','.join(rtc_num)))
    print( '''can not handle multiple task in same time, please pick up one of the rtc ticket number in the command line to specify which ticket to process... ''')
    exit()
else:
    rtc_num = rtc_num[0]
    rtc_num = rtc_num.split('-')[1]
    #rtc_num = 'RA' + rtc_num.split('-')[1].zfill(5)
    print('converted rtc number is: {}'.format(rtc_num))

print( '-- now processing the ticket number {} ... '.format(rtc_num))

### STEP 3 getthe zen desk ticket number (get the information form the dataframe.
print( )
print( )
print( "[zen desk tickets: ]")
print( '\n'.join(request_df.COE_zendesk_number.unique()))
print( )

### STEP 4 get the category number, then use the sheet 2 -- category description sheet to get the description of each category
cat_df = cat_df.loc[:, ['cat', 'description']]
cat_df.set_index('cat', inplace = True)
cat_dict = cat_df.to_dict(orient = 'index')
cat_list = request_df.issue_category.unique()
list(map(lambda x: sys.stdout.write("[{}]: \n {}".format(x, cat_dict[x]['description'])), cat_list))

### STEP 5 get the cnum list from the dataframe.
cnum_list = request_df.loc[:, 'RCNUM']


### step 5.1 validate if the cnum has been processed in the past
print((">" * 50))
print("validating if the cnum has been processed in the past")
request_df_all = request_df_all.loc[request_df_all.status == 'Completed', :]
print("totol completed records is {}".format(request_df_all.shape[0]))
temp_df_check = request_df_all.loc[request_df_all.RCNUM.isin(cnum_list),:]
print("we can found the folloiwng completed records for those cnum to be processed!!")
print(temp_df_check)
if len(temp_df_check) >0 :
    tmp_df = request_df.loc[request_df.RCNUM.isin(temp_df_check.RCNUM.unique()), :]
    temp_df_check = pd.concat([temp_df_check, tmp_df], sort = False)
    validate_fname = 'input/archive/request_validate_{}.xlsx'.format(rtc_num)
    temp_df_check.to_excel(validate_fname, index = False, engine='openpyxl')
    print("the validate request is written the following file {}".format(validate_fname))
print(">" * 50)
print()

### validate ends here


print( )
print( '[CNUM to be deleted:]')
print( '{}'.format('\n'.join(cnum_list)))

### STEP 6-1 query the odm database for those cnums and print out the query result
### STEP 6-2 if the count of result is 0, then means the requests has been processing

cnum_list = [ "'{}'".format(i)  for i in cnum_list]
query_col_list = ['RCNUM', 'TNAMLAST', 'TNAMFRST', 'CFDRSRC', 'CACTIVE', 'DUPDATE', 'CCOUNTRY', 'CCOUNTRQ', 'RSERNUM']
query = '''SELECT {}  FROM ODMPRD.ODMT_EMPLOYEE
WHERE RCNUM IN ( {} ) '''.format(', '.join(query_col_list), ', '.join(cnum_list))

print( )
print( '[Query before deletion]: ({} CNUMs in total)'.format(len(cnum_list)))
print( query )
print( )

with odm.odm_adhoc('prod') as odmprd_adhoc:
    results = odmprd_adhoc(query)

if len(results) == 0:
    print( 'the result has been processed already!, no record in resultset... ')
    exit()
# setup the dataframe display options
result_df = pd.DataFrame(results)
pd.set_option('display.max_rows',None)
# pd.set_option('display.max_colwidth', -1)
pd.set_option("display.colheader_justify","left")
result_df = result_df[query_col_list]
result_df.set_index('RCNUM', inplace = True)
result_df.to_csv('temp.csv', sep = '|', index = True,  encoding = 'utf-8')
print('\n&nbsp;\n')
#print( result_df)
p_tempcsv()
print('\n&nbsp;\n')
print('\n&nbsp;\n')
print( '     {} record(s) selected. '.format(len(result_df)))


print('''\n\n ---------------------------------------
        We are going to existing REK process to perform the deletion, the deleted data will be backuped in 2 datasets. No dry run is needed..

        WE NEED TO FIX THE ISSUE THA THE CURRENT PROGRAM NEED TO BE MODIFIED TO MAKE IT COMPATIBLE TO THE JIRA INSTEAD OF RTC.
        most likely the following rows need to be changed to remove RA from the ticket number, since the field RRTCTASK does not accept non numeric numbers.
        rtc_num = 'RA' + rtc_num.split('-')[1].zfill(5)
        print('converted rtc number is: {}'.format(rtc_num))


        ''')


### STEP 6-3 get input from terminal to determine if we proceed to get REK and update it
choice = input('Shall we proceed to update the REK table? (y/n):')
if choice not in ('Yy'):
    exit()


### STEP 7 read the data from rek table, if there are some entries which FDISCONT <> 'Y', stop processing
print( '*' * 40)
print( '-- STEP 6, read the data from REK table ----')

cols = ['C','CMODEL','CCOUNTRY','CCOUNTRQ','RSERNUM','NCOUNTRY','NCOUNTRQ','NSERNUM','RRTCTASK','FACTION','CLANGUAG','FDISCONT','QSORTSEQ','TCOUNTRY' ]

tid = 'REK'
tbname = 'ODMT_EMP_KEYCHANGE'
sql_template = " SELECT 'R' as {} FROM ODMPRD.{};  "
sql = sql_template.format( ', '.join(cols), tbname)
print( sql )


with odm.odm_adhoc('prod') as odmprd_adhoc:
    results = odmprd_adhoc(sql)

rek_df = pd.DataFrame(results)
if any(rek_df.FDISCONT != 'Y'):
    print( ' there are entries with FDISCONT <> Y, those entreis are pending processing')
    print( rek_df.loc[rek_df.FDISCONT != 'Y', :])
    print( 'please consider to complete those entries in REK before processing current task, processing aborted! ')
    exit()


### STEP 8  get the next sequence number from the result of REK and then add new entries into REK dataframe based on the request dataframe
next_seq = rek_df.QSORTSEQ.astype(int).max() + 1
print( 'next sequence number is: ', next_seq)

    #print row[1].CCOUNTRY    row[1] is the data part of the row tuple. the row[0] is the index
rek_entries = list(map(lambda row: {
            'C': 'R',
            'CMODEL': 'IBM ',
            'CCOUNTRY': row[1].CCOUNTRY,
            'CCOUNTRQ': row[1].CCOUNTRQ,
            'RSERNUM' : row[1].RSERNUM,
            'NCOUNTRY': '',
            'NCOUNTRQ': '',
            'NSERNUM': '',
            'RRTCTASK': rtc_num,
            'FACTION': 'D',
            'CLANGUAG': '',
            'FDISCONT': '',
            'QSORTSEQ': str(next_seq),
            'TCOUNTRY': 'Zendesk Number: {}'.format(request_df.loc[request_df.RCNUM == row[0].strip(), 'COE_zendesk_number'].to_string(index = False).strip())
            } , result_df.iterrows()))
print( rek_entries)

rek_df = rek_df.append(rek_entries )

### STEP 9 write the REK dataframe into csv file
csv_fname = 'csv/rek_T{}.csv'.format(rtc_num)
rek_df.to_csv(csv_fname, index=False, columns = cols )

### STEP 10 add the T, REK row in the first row of the csv file
print( 'add the file line T,REK ... in the csv file' )
contents = open(csv_fname, 'r').readlines()
contents.insert(0, 'T,REK - Employee Primary key change (ODMT_EMP_KEYCHANGE)\n')
with open(csv_fname, 'w') as f:
    contents = ''.join(contents)
    f.write(contents)

### STEP 11 upload the csv file into ODMAP.RES.ZZ.RDMCSV.IN.EM and update the ODMSUBRJ to get ready to load the csv file
print( '-- STEP 11-1, upload the csv file into ODMAP.RES.ZZ.RDMCSV.IN.EM --- ')
print( '-- STEP 11-2, upload the jcl which for rsduload -- ')
with odm_ftp.odm_ftp_conn('put') as odm_put_file:
    odm_put_file(fm=csv_fname, to = 'ODMAP.RES.ZZ.RDMCSV.IN.EM')
    print( 'the file {} is uploaded... '.format(csv_fname))
    odm_put_file(fm='jcl/rdsuload_odmsubrj.jcl', to = 'ODMLD.PRD.RUN(ODMSUBRJ)')
    print( 'the ODMLD.PRD.RUN(ODMSUBRJ) jcl for rdsuload is uploaded ... ')

### STEP 12 prompt the message to inform user to run trig911 to upload the REK entries.
print( )
print( '-' * 40 )
print( 'better to do rdsuunl.sh to get the backup of the reference tables ' )
print( 'the ODMLD.PRD.RUN(ODMSUBRJ) jcl prepared, please run trig911.sh to get the unload of the reference table' )
print( 'run ./trig911.sh to upload the REK new entries')
print( 'after that, please run trig_ccq.sh to prepare the jcl which will trigger the ccq change process')
print( 'after that, run ./trig911.sh again to actually run the ccq change process')
print( 'then, check REK table to make sure there is no entries with FDISCONT <> Y')
print( 'then go to the server to check if the deleted record has been backuped in the dataset')
print( 'then, rerun the wd_del to check if the records have been deleted')
