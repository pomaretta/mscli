run:
	python3 setup.py bdist_wheel
	pip3 uninstall mscli
	pip3 install dist/mscli-0.0.3-py3-none-any.whl
	rm -rf build dist src/mscli.egg-info

deploy:
	python3 setup.py bdist_wheel