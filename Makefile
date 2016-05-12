
checkfiles = django_vumi/ *.py

help:
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    check	Checks that build is sane"
	@echo  "    test	Runs tests"
	@echo  "    lint	Reports pylint violations"
	@echo  "    migrate     Runs db migrations"
	@echo  "    run         Runs a dev instance"
	@echo  "    redb	Resets the dev db to new"

check: 
	@echo "# Check sources for errors..."
	@pylint -E $(checkfiles)
	@python setup.py check -mrs

test:
	@coverage run --omit=*/migrations/*,*/tests/* --source=django_vumi --branch manage.py test django_vumi
	@coverage report -m

lint:
	@-flake8 $(checkfiles)
	@-pylint $(checkfiles)
	@-python setup.py check -mrs

migrate:
	./manage.py migrate

run:
	./manage.py runserver 0.0.0.0:8000

redb: 
	@-rm -f db.sqlite3
	@./manage.py migrate --noinput
	@./manage.py loaddata django_vumi/fixtures/devs_user.json
