# odm-daily-public

This repository is to hold all the daily tools in github

+ docr.sh
+ ck.py
+ ckl.sh
+ ck.sh
+ rload.py
+ runl.py
+ wd_update.py
+ wd_del.py
+ dc_adhoc.py 
+ runsql.py 

## Docker Image
The docker images is the `richardjl/odm-daily-public:latest`, when you run the command docr.sh, it will pull the image from dock hub automatically.

The docker image can always be created by using the Dockerfile in the repo.
```
./build.sh 0.1
```
Where `0.1` is the version of your docker image `odm-daily-public`   


## Setup the system variables in your system to create the env.list file 

The `docr.sh` use `env.list` to get the system variables.
We use `convert_env.sh` to replace the variable into actual value and then create the `env.list` file. 

The `convert_env.sh` use the file `tempenv.txt` as input. Below is the contents of the file `tempevn.txt`: 
```
   USER=$USER
   PASSWORD=$PASSWORD
   ODM_DATABASE_PROD=$ODM_DATABASE_PROD
   ODM_DATABASE_UAT=$ODM_DATABASE_UAT
   ODM_PORT_PROD_SSL=$ODM_PORT_PROD_SSL
   ODM_PORT_UAT_SSL=$ODM_PORT_UAT_SSL
   ODM_SERVER_PROD_SSL=$ODM_SERVER_PROD_SSL
   ODM_SERVER_UAT_SSL=$ODM_SERVER_UAT_SSL
   ODM_SERVER=$ODM_SERVER
   DSR_FOLDER_ID=$DSR_FOLDER_ID
   LOG_LEVEL=$LOG_LEVEL
```
You can directly create the `env.list` file as well. If so, you can skip excuting this step and you should have the contents of `env.list` similar as below: 
```
   USER=${your userid}
   PASSWORD=${your password}
   ODM_DATABASE_PROD=USIBMVRDP2H
   ODM_DATABASE_UAT=USIBMVRDD1H
   ODM_PORT_PROD_SSL=5521
   ODM_PORT_UAT_SSL=5519
   ODM_SERVER_PROD_SSL=usibmvrdp2h.ssiplex.pok.ibm.com
   ODM_SERVER_UAT_SSL=usibmvrdd1h.ssiplex.pok.ibm.com
   ODM_SERVER=stfmvs1.pok.ibm.com
   LOG_LEVEL=30
```
The `your userid` and `your password` is the user id and password in the server stfmvs1 with which you can access DB2 database in the ODM mainframe server. 

## Setup the $ODM_DAILY_PUBLIC_ROOT variable in your pc
Make sure to setup the ${ODM_DAILY_PUBLIC_ROOT} in your pc. The value should be the absolute path of the repo. For example, if you have cloned this repo in the directory `c:\windows\odm_daily_public`, then just set this variable as this value. 

## Run docr.sh to use all the tools in this repo
docr.sh is the script the launch the docker image.
it will take the python program the the parameter. The content in the docr.sh is as below.
```
docker run \
   --env-file env.list \
    -v ${ODM_DAILY_PUBLIC_ROOT}/input:/app/input \
   -it richardjl/odm-daily-public:latest \
   python  $1 $2 $3 $4 $5 $6 $7 $8 $9
```

Example to run python program:
```
./docr.sh ck.py prd 123456672
```

### ck.py  - check data in e01 table, check the error log and also check enterprise directory for the cnum
this program takes 3 parameters

```
python ck.py prd|uat  123456672,111111897  [ccompaiw,dleave] [nonise] [err] [ed]
```

1st parameter has to be prd or uat
2nd parameter has to be the list of cnum, rsernum or s/n. the length has to be 9 or 7 or 6. otherwise, the program will reject it..
3rd parameter is optional. It takes additional odm field name to be included in the result.

The program print out the result, include the following fields list. RCNUM, TNAMLAST, TNAMFRST, CACTIVE, DUPDATE, CFDRSRC. it will also include the odm fields which comes from the 3rd paramenter.

In the result, if one paticular cnum/sn is not found, it will also be prompted in the final result.

parameter `nonise`: by default, this command will check both E01 table as well as N01 table. You can explicitly add the parameter `nonise` to request the tool not checking N01 table. 

Parameter `err`: when this parameter is given, it will automatically download the error report from odm server, and search if there's any relevant error message for the cnum 

Parameter `ed`: when is parameter is given, it will automatically use the enterprise API to retrieve the information for the given cnum and will show the result for the cnum. 


### ckl.sh



### rdsuload.py
Example to run this program:

```
./docr.sh rdsuload.py input/RCG_CEE.xlsx
```

The program will read the xlsx file and the upladed in the stfmvs1 server. In addition, it will also uplead the JCL .
After this is done, please run ./trig911.sh to excute the jcl to do the real load option on server.


### rdusunl.py

```
./docr.sh rdsuunl.sh REK IBM
```
or
```
./docr.sh rdsuunl.sh REK WA WE WP
```

The program will get the reference table id as well as the models from the command line.
then prepare the odmsubrj jcl and upload it onto server. ODMLD.PRD.RUN(ODMSUBRJ)

After upload is done. you can run the script `./trig911.sh` to do the unload operation


### Change log
Current version is 0.1 
Known issue: 
If we use ODMCLUD to be the user, then we have to address the following issue: 
+ ODMCLUD.SQL(JRA00561) requests a nonexistent partitioned data set.  Use MKD command to create it.
Need to create the ODMCLUD.SQL library to hold SQL statement
550 STOR fails: ODMLD.PRD.RUN(ODMSUBRJ).  User not authorized.
We need to grant acces of ODMLD.PRD.RUN for user id ODMCLUD  
+ The wd_updata.py does not work now, since ODMCLUD does not have the update access to the library ODMLD.PRD.RUN. 

