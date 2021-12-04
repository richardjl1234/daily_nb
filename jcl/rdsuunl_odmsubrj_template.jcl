//ODMSUBRJ JOB ('QQY5ODM,39U28,SU45RMR,STF-08'),'ODM team support',             
//            MSGCLASS=P,MSGLEVEL=(1,1),REGION=4096K,USER=PCODM,                
//            CARDS=(1000,WARNING),PAGES=(1000,WARNING),                        
//            LINES=(1000,WARNING),BYTES=(1000,WARNING),                        
//            NOTIFY=C943511                                                    
//JOBOUT OUTPUT DEFAULT=YES,JESDS=ALL,FORMS=ODM1                                
//LIBS     JCLLIB  ORDER=(ISCTL.PRODPROC.ODM)                                   
//INCLMEM INCLUDE MEMBER=ODMNA        level dependent JCL variables             
//**********************************************************************        
//* Name of member  : ODMSUBRJ                                                  
//* Function        : This triggers the OPC Application called ODMP911          
//*                   The job running is ODM911SJ, which starts the             
//*                   required process to run, this ODMSUBRJ job                
//*                                                                             
//* ODM Team instructions                                                       
//*                   Always copy the STEP you want to run just below           
//*                   these instructions. Always leave the other steps          
//*                   in and ensure 2 there is the // above AND that            
//*                   there is NO JOB CARD                                      
//*                   When "You're done" put the // below this comments         
//*                                                                             
//* Restart Info    : Fix the problem and restart at the step that              
//*                   failed.                                                   
//* Operators Instructions                                                      
//*                 : NONE                                                      
//**********************************************************************        
//*                                                                             
//*  Extract data from reference tables. Name of Original Job: ODMRDM1E         
//*                                                                             
//STEP0004 EXEC PGM=IKJEFT1B,PARM='ODMRDM1',REGION=200M                         
//STEPLIB  DD DSN=SYS1.SEZALOAD,DISP=SHR                                        
//         DD DSN=SYS1.BPIPE.LINKLIB,DISP=SHR                                   
//         DD DSN=SYS1.REXXSQL.LINKLIB,DISP=SHR                                 
//         DD DSN=DB2.DP2H.DB2.RUNLIB.LOAD,DISP=SHR                             
//         DD DSN=DB2.DP2H.DB2.SDSNLOAD,DISP=SHR                                
//SYSEXEC  DD DSN=ODMLD.PROD.CLIST,DISP=SHR                                     
//ODMRDM   DD DSN=&HLQDSET..RES.UTILLONG,DISP=SHR                               
//DATADICT DD DSN=ISCTL.PRODCLST.ODM(ODMDDICT),DISP=SHR                         
//ENVIRON  DD DSN=ISCTL.PRODCNTL.ODM(ODPARAT),DISP=SHR                          
//DISTLIST DD DSN=C943511.UTIL(ODPAXMZE),DISP=SHR                               
//SUBJECT  DD DSN=&&SUBJECT,DISP=(,PASS),UNIT=SYSDA,                            
//            SPACE=(TRK,(1,1),RLSE),                                           
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=0)                                 
//SYSTSPRT DD SYSOUT=*                                                          
//SYSTSIN  DD DUMMY                                                             
//PARMTR   DD DSN=&&PARMTR,DISP=(,PASS),UNIT=(SYSDAL,20),                       
//            SPACE=(CYL,(1500,1500),RLSE),                                     
//            DCB=(RECFM=VB,LRECL=2004,BLKSIZE=0)                               
//RESULT   DD DSN=&HLQDSET..RES.ZZ.RDMXML.OUT.EM(+1),                           
//            DISP=(NEW,CATLG,CATLG),UNIT=(SYSDAL,20),                          
//            SPACE=(CYL,(1500,1500),RLSE),                                     
//            DCB=(RECFM=VB,LRECL=2004,BLKSIZE=0)                               
//*PARM     DD DSN=ODMAP.RES.ZZ.RDMXML.PARM.EM,DISP=SHR                          
//PARM     DD *
TID {}
CMODEL {}
//*                                                                             
//                                                           
