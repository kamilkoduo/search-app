docker-login:
	docker login docker.pkg.github.com/kamilkoduo/search-app -u kamilkoduo

docker-build-python:
	docker build -f Dockerfile -t docker.pkg.github.com/kamilkoduo/search-app/python:local .

docker-build-python-nocache:
	docker build -f Dockerfile -t docker.pkg.github.com/kamilkoduo/search-app/python:local . --no-cache

docker-push-python:
	docker push docker.pkg.github.com/kamilkoduo/search-app/python:local
