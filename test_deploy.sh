#/bin/bash

flaskenv=$(cat .env)
for i in $flaskenv; do
    export $i
done

sudo docker build --build-arg SW_GIT_KEY=${SW_GIT_KEY} --build-arg SW_GIT_REPO=${SW_GIT_REPO} -t test-cb .

sudo docker stop test-cb || true
sudo docker rm test-cb || true
sudo 