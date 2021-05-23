IMAGE_NAME = flaskblog_evgeny
VERSION = 0.01

build:
	docker build -t $(IMAGE_NAME):$(VERSION) .
run:
	docker run -p 8800:5000 --name image --rm $(IMAGE_NAME):$(VERSION)
lint:
	docker run --rm -v $(PWD):/code eeacms/pylint