'''
this module is to provide functions to ftp between local machine to odm server

To call the function:

with odm_ftp_conn('get') as odm_get_file:
    odm_get_file(fm=, to=)

with odm_ftp_conn('put') as odm_put_file:
    odm_put_file(fm=, to=)

this module is already python2 and python3 compatible
'''

from ftplib import FTP
from contextlib import contextmanager
import sys
import os

odm_user = os.environ['USER']
odm_password = os.environ['PASSWORD']
odm_server = os.environ['ODM_SERVER']

@contextmanager
def odm_ftp_conn(action):  # can be get or put
    ftp = FTP(odm_server)
    ftp.login(user=odm_user, passwd = odm_password)
    ftp.cwd('..')
    def get_file(fm='server_file', to='local_file.txt'):
        f = open(to, 'w')
        ftp.retrlines('RETR ' + fm, lambda s, w=f.write: w(s+'\n'))
        f.close()

    def put_file(fm='local_file.txt', to='server_file.txt'):
        ftp.storlines('STOR ' + to, open(fm, 'rb'))
    try:
        print( 'the ftp connection to stfmvs1 established...')
        if action == 'get' :
            yield get_file
        elif action == 'put':
            yield put_file
        else:
            pass

    finally:
       ftp.quit() # close the connection after processing
       print( 'the ftp connection to stfmvs1 destroyed...')



if __name__ == '__main__':
    with odm_ftp_conn('get') as odm_get_file:
        odm_get_file(fm='ODMLD.PRD.RUN(ODMSUBRJ)', to='/odm_modules/common_func/odmsubrj.txt')
        odm_get_file(fm='ODMAP.RES.HI.ERRORREP(0)', to='/odm_modules/common_func/temp_report.txt')

    with odm_ftp_conn('put') as odm_put_file:
        odm_put_file(fm='/odm_modules/common_func/odmsubrj.txt', to='C943511.TMP.TXT')
        odm_put_file(fm='/odm_modules/common_func/odmsubrj.txt', to='C943511.SQL(TMP1)')








        #odm_get_file(fm='' to= 'temp1.txt')







