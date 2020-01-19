PROJECT := flask-upload-uwsgi
EXPOSED_PORT := 8080

clean:
	sudo docker stop $(PROJECT) >/dev/null 2>&1 | true
	sleep 1
	sudo docker rm $(PROJECT) >/dev/null 2>&1 | true
	sudo docker image rm $(PROJECT) | true

docker-build:
	sudo docker build -f Dockerfile-alpine-uwsgi -t $(PROJECT) .

docker-rm:
	sudo docker stop $(PROJECT) >/dev/null 2>&1 | true
	sleep 1
	sudo docker rm $(PROJECT) >/dev/null 2>&1 | true

docker-run:
	sudo docker run -d --name $(PROJECT) -p 8080:$(EXPOSED_PORT) $(PROJECT)

docker-run-constraints:
	sudo docker run -d --name $(PROJECT) -p 8080:$(EXPOSED_PORT) -m 24m --cpus=1 --tmpfs /tempdisk:rw,noexec,nosuid,size=2m $(PROJECT)

docker-stop:
	sudo docker stop $(PROJECT)

docker-ssh:
	sudo docker exec -it $(PROJECT) /bin/sh

docker-logs:
	sudo docker logs -f $(PROJECT) 2>&1

