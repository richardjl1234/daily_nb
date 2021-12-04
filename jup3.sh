docker run \
   --env-file env.list \
   -v ${ODM_DAILY_PUBLIC_ROOT}/result:/result \
   -v ${ODM_DAILY_PUBLIC_ROOT}/sql:/sql \
   -v ${ODM_DAILY_PUBLIC_ROOT}/input:/input \
   -v ${ODM_DAILY_PUBLIC_ROOT}:/app  \
   -p 8888:8888 \
   -it richardjl/odm-daily-public:latest \
   jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
