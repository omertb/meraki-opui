FROM python:latest

WORKDIR /project
COPY ./meraki-opui/requirements.txt requirements.txt
RUN apt update && apt install build-essential python3-dev libldap2-dev libsasl2-dev ldap-utils tox lcov valgrind && apt clean && pip --no-cache-dir install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "--chdir", "/project", "run:app", "--reload", "--timeout", "900"]