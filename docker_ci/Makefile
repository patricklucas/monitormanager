package:
	mkdir -p dist
	docker build -t monitormanager-build .
	docker run --rm \
		-v $(shell dirname $(shell pwd)):/root/monitormanager:ro \
		-v $(shell pwd)/dist:/root/dist:rw monitormanager-build \
		/root/build-deb.sh
