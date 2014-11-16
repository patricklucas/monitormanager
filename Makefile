sdist:
	python setup.py sdist

deb:
	mkdir -p dist
	make -C docker_ci package
	mv docker_ci/dist/*.deb dist/
