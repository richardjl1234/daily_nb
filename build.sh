echo $#
if [ $# -eq 0 ]
then
   echo 'Missing odmdaily docker image version number....'
   echo 'Usage: ./build.sh odmdaily_docker_version , example: ./build.sh 0.53y-temp2 [hub]'
   exit
fi
rm -r common_func BOX
cp -r ../odm_modules/common_func/ common_func
cp -r ../odm_modules/BOX/ BOX
# create the docker image and push to docker hub when needed.
docker build -t odm-daily-public:$1 .
docker tag odm-daily-public:$1 richardjl/odm-daily-public:$1
docker tag odm-daily-public:$1 richardjl/odm-daily-public:latest
if [ "$2" = "hub" ]
then
   docker push richardjl/odm-daily-public:$1
   docker push richardjl/odm-daily-public:latest
fi


