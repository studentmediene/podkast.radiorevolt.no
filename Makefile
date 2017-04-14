.PHONY : run
run : venv/bin/uwsgi podkast.radiorevolt.no.ini
	. venv/bin/activate && uwsgi --ini podkast.radiorevolt.no.ini
