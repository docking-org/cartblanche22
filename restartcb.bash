git add .
git commit -m "autocommit $(date)"

for img in $(sudo docker ps | tail -n+2 | awk '{print $1}'); do

	echo $img
	sudo docker stop $img
	sudo docker rm $img

done

sudo /usr/local/bin/gitlab-runner exec shell 'deploy job'