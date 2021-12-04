'''
This application is to:
    1. read the full execl file
    2. convert it into csv file
    3. upload it to server
    4. update the jcl to server
    5. show the sample of csv, display the jcl to confirm
    6. prompt the command to run the jcl

[usage:]  python ./rdsuload.py xxxx.xlsx|xxxx.xls

'''
import sys
sys.path.append('/odm_modules')
from common_func import odm_ftp
import pandas as pd
import datetime

if len(sys.argv) <=1:
    print( 'No enough parameter is given in the command line')
    print( 'Usage: ./rdsuload.py xxxx.xlsx|xxxx.xls')
    exit()

# step 1 read the TID from the excel file
print( ' -- step 1, get the file name, and tid from the input excel file -- ')
print( 'excel file name is: ', sys.argv[1])
df_tid = pd.read_excel(sys.argv[1], header =0)
tid_with_desc =df_tid.columns[1]
tid = df_tid.columns[1].split()[0]
print( 'the TID is : ', tid)

# step 2 get the offset of the column list (field list, with C in the first column
print()
print( ' -- step 2  get the offset of the column list (field list, with C in the first column')
rowno_of_fdlist = df_tid.index[df_tid.iloc[:,0] == 'C']  # get the index of the column
print(rowno_of_fdlist)
print(df_tid.index)
header = rowno_of_fdlist[0] + 1
print( 'the offset of header is :', header)

# step 3 read the excel file into dataframe
print()
print( ' -- step 3&4, read the excel file again, and get the cmodel from the dataframe')
print( ' Assumption: output for date will be in yyyy-mm-dd \n output for float will be rounded to interger string. \n output for int will be in string format')
df_col = pd.read_excel(sys.argv[1], header = header).columns
print( df_col)
#converter_col = {col: str for col in df_col}
#print converter_col

#df = pd.read_excel(sys.argv[1], header = header, converters = converter_col ).fillna('')

df = pd.read_excel(sys.argv[1], header = header, keep_default_na=False ).fillna('')
# assumption is the for float, we only keep 1 digit, for int, we convert it to str, for datetime, we use date format yyyy-mm-dd
df = df.applymap(lambda v: str(v) if isinstance(v, (int))
        #else str(round(v,0)) if isinstance(v,float)
        else "%.7f" % v if isinstance(v,float)
        else str(v.date()) if isinstance(v, datetime.date)
        else v)
print( df.head())
# step 4 get the CMODEL from the dataframe
df1 = df.loc[df.C != '*']
cmodels = df1.CMODEL.unique()
print( 'the cmodels in the excel file are: ', cmodels)

# step 5 write the data into csv file, put the csv file into the csv folder
print()
print( ' -- step 5 write the dataframe into csv file (in csv folder) -- ')
csv_file_name = 'input/csv/{}_{}.csv'.format(tid ,  str(datetime.datetime.now().date()) )
df.to_csv(csv_file_name, index= False)

# add the T, Tid line in the beginning of the file
print( 'add the file line T,TID ... in the csv file')
contents = open(csv_file_name, 'r').readlines()
contents.insert(0, 'T, {}\n'.format(tid_with_desc))
with open(csv_file_name, 'w') as f:
    contents = ''.join(contents)
    f.write(contents)

print( 'the excel file is converted to csv file and saved in {}'.format(csv_file_name))
print( 'below are 20 sample rows in the file')
#print( df.sample(20))

# step 6 update the csv file into ODMAP.RES.ZZ.RDMCSV.IN.EM
# step 7 upload the jcl which to do rsduload
print()
print( '-- step 6, upload the csv file into ODMAP.RES.ZZ.RDMCSV.IN.EM --- ')
print( '-- step 7,  upload the jcl which to do rsduload -- ')
with odm_ftp.odm_ftp_conn('put') as odm_put_file:
    odm_put_file(fm=csv_file_name, to = 'ODMAP.RES.ZZ.RDMCSV.IN.EM')
    print( 'the file {} is uploaded... '.format(csv_file_name))
    odm_put_file(fm='jcl/rdsuload_odmsubrj.jcl', to = 'ODMLD.PRD.RUN(ODMSUBRJ)')
    print( 'the ODMLD.PRD.RUN(ODMSUBRJ) jcl for rdsuload is uploaded ... ')

print()
print( '-' * 40)
print( 'better to do rdsuunl.sh to get the backup of the reference tables ')
print( 'the ODMLD.PRD.RUN(ODMSUBRJ) jcl prepared, please run trig911.sh to get the unload of the reference table')
