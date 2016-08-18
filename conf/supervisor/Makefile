run: clean
	$(VIRTUAL_ENV_PATH)python manage.py runserver


run_deploy: clean
	$(VIRTUAL_ENV_PATH)gunicorn --config conf/gunicorn.conf wsgi_gunicorn:app


pip:
	$(VIRTUAL_ENV_PATH)pip install -r requirements.txt


restart_all:
	supervisorctl status shuxin_manager | grep RUNNING && supervisorctl restart shuxin_manager || echo skip
	service nginx reload


clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;

.PHONY: run, run_deploy, pip, restart_all, clean
