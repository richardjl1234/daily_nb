//ODM911ET JOB ('QQY5ODM,39U28,SU45RMR,STF-08'),'ODM TRIGGER',          00010000
//         MSGCLASS=H                                                   00020000
//*MAIN PROC=14,CLASS=NFTP                                              00030000
//JOBOUT OUTPUT DEFAULT=YES,JESDS=ALL,FORMS=ODU1                        00040000
//**********************************************************************00050000
//*                --- OPERATIONAL DATA MANAGER ---                    *00060000
//*   Country name    : Ops job can took over by this job              *00070000
//**********************************************************************00080000
//STEP01   EXEC PGM=EQQEVPGM                                            00090000
//EQQMLIB  DD   DSN=ESPP.MSTRMLIB,DISP=SHR                              00100000
//EQQMLOG  DD   SYSOUT=*                                                00110000
//SYSIN    DD   *                                                       00120000
SRSTAT 'OU$911ET'               SUBSYS(ETKR) AVAIL(YES)                 00130000
SRSTAT 'OU$911ET'               SUBSYS(ETKR) AVAIL(NO)                  00140000
/*                                                                      00150000
//                                                                      00160000
