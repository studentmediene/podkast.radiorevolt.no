.PHONY : uwsgi
uwsgi : venv/bin/uwsgi ../podkast.radiorevolt.no.ini
	. venv/bin/activate && uwsgi --ini ../podkast.radiorevolt.no.ini

.PHONY : images
images : venv/bin/python
	. venv/bin/activate && python process_images.py -e
