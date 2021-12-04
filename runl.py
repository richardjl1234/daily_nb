'''
This application is to prepare the rdsu unload script
as well as the input for rdsu unalod

to run this program, please give the reference id as well as the model in the command line

[usage:]  python ./rdsuunl.py REK  WP WE WA

'''

import sys
sys.path.append('/odm_modules')
from common_func import odm_ftp

if len(sys.argv) <=2:
    print( 'No enough parameter is given in the command line')
    print( 'Usage: ./rdsuunl.py REK IBM ' )
    exit()

print( 'reference table name:', sys.argv[1])
print( 'model is : ' , ' '.join(sys.argv[2:]) )

server_file= 'ODMLD.PRD.RUN(ODMSUBRJ)'

local_file= 'jcl/rdsuunl_odmsubrj.jcl'
local_file_contents = open('jcl/rdsuunl_odmsubrj_template.jcl', 'r').read().format(sys.argv[1], ' '.join(sys.argv[2:]))
with open(local_file, 'w') as f:
    f.write(local_file_contents)

with odm_ftp.odm_ftp_conn('put') as odm_put_file:
    odm_put_file(fm=local_file, to=server_file)


print( 'the ODMLD.PRD.RUN(ODMSUBRJ) jcl prepared, please run trig911.sh to get the unload of the reference table' )
