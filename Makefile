IMAGE=clulab/equations

default: dockerize

dockerize: Dockerfile
	docker build -t $(IMAGE) .
