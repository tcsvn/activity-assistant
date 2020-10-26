#python3 manage.py makemigrations backend frontend
cd /home/app/
python3 web/manage.py makemigrations backend
python3 web/manage.py migrate
python3 web/manage.py migrate --run-syncdb
python3 web/manage.py createsuperuser --email test@test.de --username admin
python3 web/manage.py createsuperuser --email test@test.de --username frontend
python3 web/manage.py runserver