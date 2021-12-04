''' 
Fuction enrich_col(): 

This module is to enrich_col() is to get the information form RZ2 table, and setup the dictionary 
the return a function f. The returned function f will take 2 parameters , rsts and tid. 
the returned function will utilized the RZ2 dictionary and then create the result which contains the named tuple: 
1. column name
2. col description
3. col classification
4. col value

Function enrich_sql(sql): 

this module also provide the function sql_enrich(sql)
the data items selected in sql is in the format something like E01.TNAMLAST , 
in order that the data field name in the output can be effectively use the enrich_col function, we need the 
output field naem in the format E01_TNAMLAST
'''

import sys
sys.path.append('/odm_modules')  # odm common_func modules should be placed in this top level folder
from common_func import odm_conn
from contextlib import contextmanager
from collections import namedtuple

def enrich_col(): 
    sql = '''
    select CTID,COLNO, CCLASS, CCOLNAME, TCOLNAME, CCOLFMT, CKEY
    FROM ODMPRD.ODMT_DDICT_COLUMNS
    WHERE CLANGUAG = '' AND FDISCONT <> 'Y'
    ;
    '''
    Col = namedtuple('Col', ['col_name', 'col_des', 'col_no', 'col_class', 'col_value'])
    with odm_conn.odm_adhoc('prod') as odmprd_adhoc: 
        rz2_results = odmprd_adhoc(sql)

    # remove the blanks from the value
    rz2_results = [ {k:v.strip()    for k,v in i.items()}    for i in rz2_results]
#    rz2_results = filter(lambda x: x['CTID'] == tid    , rz2_results)
    rz2_results_dict = {i.pop('CTID')+'_'+i.pop('CCOLNAME'):i   for i in rz2_results}
    def f(rsts, tid): 
        if tid != '':
            tid +='_'
        rs = [ tuple(Col._make([
            tid+k,
            rz2_results_dict.get(tid+k, {}).get('TCOLNAME', ''),
            rz2_results_dict.get(tid+k, {}).get('COLNO', '999'),
            rz2_results_dict.get(tid+k, {}).get('CCLASS', ''),
            value] ) for k,value in i.items() )
            for i in rsts]
        
        def getkey(item): 
            return item.col_name.split('_')[0]+'{:0>3d}'.format(int(item.col_no))
        rs = [ sorted(i, key = getkey)   for i in rs]
        return rs
    return f


def enrich_sql(sql):
    
    x = sql.find('FROM')
    y = sql[:x].replace('SELECT', '').replace('\n', ' ')
    z = y.split(',')
    z = [i.strip() for i in z]
    z = ['{0} AS {1}_{2}'.format(i, i.split('.')[0], i.split('.')[1]) for i in z]
    return 'SELECT \n'  + ',\n'.join(z) + '\n' + sql[x:]
    

if __name__ == '__main__': 
    sql = '''
    select
    *
    from 
    ODMPRD.ODMT_EMPLOYEE
    WHERE
    RCNUM = '943511672'
    '''
    with odm_conn.odm_adhoc('prod') as odmprd_adhoc: 
        results = odmprd_adhoc(sql)
    enrich_col_f = enrich_col()
    x_enriched = enrich_col_f(results, 'E01') 
    for i in x_enriched: 
        print( '-' * 110)
        for j in i: 
            print( '%4s|%-12s|%-55s|%-30s|%-3s' % (j.col_no, j.col_name, j.col_des, str(j.col_value).strip(), j.col_class ))
    
        


