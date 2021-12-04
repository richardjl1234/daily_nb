//ODMSUBRJ JOB ('QQY5ODM,39U28,SU45RMR,STF-08'),'ODM team support',             
//            MSGCLASS=P,MSGLEVEL=(1,1),REGION=4096K,USER=PCODM,                
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
//COPY     EXEC PGM=PIPE,                                             
//         PARM='< DDNAME=IN | > DDNAME=INSAVED COERCE'               
//SYSPRINT DD SYSOUT=*                                                
//IN       DD DSN=&HLQDSET..RES.ZZ.RDMCSV.IN.EM,DISP=SHR              
//INSAVED  DD DSN=&HLQDSET..RES.ZZ.RDMCSV.INSAVED.EM(+1),             
//            DISP=(NEW,CATLG,DELETE),UNIT=SYSDA,                     
//            SPACE=(CYL,(900,900),RLSE),DCB=(RECFM=VB,LRECL=10004)   
//*---------------------------------------------------------------------        
//*  Convert spreadsheet to RDM batch file                                      
//*---------------------------------------------------------------------        
//CONVERT  EXEC PGM=IKJEFT1B,                                                   
//         PARM='ODMRDM2 EM',REGION=0M,COND=(4,LT)                              
//STEPLIB  DD DSN=SYS1.SEZALOAD,DISP=SHR                                        
//         DD DSN=SYS1.BPIPE.LINKLIB,DISP=SHR                                   
//         DD DSN=SYS1.REXXSQL.LINKLIB,DISP=SHR                                 
//         DD DSN=DB2.DP2H.DB2.RUNLIB.LOAD,DISP=SHR                             
//         DD DSN=DB2.DP2H.DB2.SDSNLOAD,DISP=SHR                                
//SYSEXEC  DD DSN=ISCTL.PRODCLST.ODM,DISP=SHR                                   
//ODMRDM   DD DSN=&HLQDSET..RES.UTILLONG,DISP=SHR                               
//DISTLIST DD DSN=C943511.UTIL(ODPAXMZE),DISP=SHR                               
//SUBJECT  DD DSN=&&SUBJECT,DISP=(,PASS),UNIT=SYSDA,                            
//            SPACE=(TRK,(1,1),RLSE),                                           
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=0)                                 
//JCL      DD DSN=OPC.PRODJCL.HR(ODM##Y0E),DISP=SHR                             
//ENVIRON  DD DSN=ISCTL.PRODCNTL.ODM(ODPARAT),DISP=SHR                          
//REFDATA  DD DSN=&HLQDSET..RES.ZZ.RDMCSV.OUTEM,DISP=SHR                        
//SYSTSPRT DD SYSOUT=*                                                          
//SYSTSIN  DD DUMMY                                                             
//RDMCSV   DD DSN=&HLQDSET..RES.ZZ.RDMCSV.IN.EM,DISP=SHR                        
//REPORT   DD DSN=&HLQDSET..RES.ZZ.RDMCSV.REPORT.EM(+1),                        
//            DISP=(NEW,CATLG,CATLG),                                           
//            UNIT=SYSDA,                                                       
//            SPACE=(TRK,(900,750),RLSE),                                        
//            DCB=(RECFM=VB,LRECL=150)                          
//                                                                              
