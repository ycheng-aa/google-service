CHECK_DIRS=.

CONFIG_FILE=tox.ini

all_tests: test_install flake8 verify_migrations django_test cover_django_test

flake8:
	flake8 $(CHECK_DIRS) --config=$(CONFIG_FILE)

test_install:
    pip3 install -r requirements/devel.txt -i https://mirrors.aliyun.com/pypi/simple