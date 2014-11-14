sdist:
	python setup.py sdist

itest_trusty:
	mkdir -p dist
	make -C docker_ci package
	mv docker_ci/dist/*.deb dist/
