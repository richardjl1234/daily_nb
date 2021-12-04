//ODMSUBRJ JOB ('QQY5ODM,39U28,SU45RMR,STF-08'),'ODM team support',
//            MSGCLASS=P,MSGLEVEL=(1,1),REGION=4096K,USER=PCODM,
//            NOTIFY={2}
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
//*---------------------------------------------------------------------
//* This job is for the RTC story {0}
//*---------------------------------------------------------------------
//DELOLD   EXEC PGM=IEFBR14
//UNLE01P  DD DSN={2}.T{0}.RESULT.TXT,
//            DISP=(MOD,DELETE,DELETE),UNIT=SYSDA,SPACE=(1,(0),RLSE)
//*---------------------------------------------------------------------
//STEP010  EXEC PGM=IKJEFT01
//SYSTSIN   DD DSN=ODMLD.PRD.UTIL(DSNX),DISP=SHR
//          DD DSN=ODMLD.PRD.UTIL(DSNTEP2),DISP=SHR
//SYSTSPRT  DD SYSOUT=*
//SYSOUT    DD SYSOUT=*
//*SYSPRINT  DD SYSOUT=*
//SYSPRINT  DD DSN={2}.T{0}.RESULT.TXT,
//             DISP=(NEW,CATLG,CATLG),
//             UNIT=(SYSDA,5),SPACE=(CYL,(5,5),RLSE)
//SYSABOUT  DD SYSOUT=*
//SYSUDUMP  DD SYSOUT=*
//SYSIN   DD *
{1}
/*
//
