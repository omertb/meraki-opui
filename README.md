## Container Deployment:
### Database:
```
$ pwd
/home/user

$ mkdir pgsql_data

$ docker run -d -p 5432:5432 --rm --name opui-postgres -v /home/user/pgsql_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=mysecretpassword postgres
$ docker exec -ti opui-postgres psql -U postgres

psql (12.3 (Debian 12.3-1.pgdg100+1))
Type "help" for help.

postgres=# CREATE DATABASE meraki_operator;
CREATE DATABASE

postgres=# exit
```

#### Flask Server:
```
$ git clone https://github.com/omertb/meraki-opui.git
$ docker run -ti --name my-flask-project -v /home/user/meraki-opui:/project python bash

## python-ldap requirements installation on debian:
root@689d54ef82ad:/project# apt-get install build-essential python3-dev python2.7-dev \
 libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind
##
root@689d54ef82ad:/# cd project
root@689d54ef82ad:/project# pip install -r requirements.txt
root@689d54ef82ad:/project# exit

## Save your container as image not to lose your pip libraries:

$ docker commit my-flask-project my-flask-project
```

> Delete the container and run saved image with required environmental variables (replace the variables):
>
> docker run -ti --name my-flask-project --rm -p 5000:5000 --link opui-postgres -v /home/user/meraki-opui:/project -e PASSWDSALT=**your_pass_salt_for_bcrypt** -e FSECRETKEY=**your_random_flask_secret_key** -e PGCRED=postgres:**your_pg_pass** -e APIKEY=**your_meraki_api_key** -e USERDNSDOMAIN=**your_ldap_server_fqdn** my-flask-project python /project/run.py 0.0.0.0
>

```
$ docker rm my-flask-project

$ docker run -ti -d --name my-flask-project --rm -p 5000:5000 --link opui-postgres -v /home/user/meraki-opui:/project -e PASSWDSALT=your_pass_salt_for_bcrypt -e FSECRETKEY=your_random_flask_secret_key -e PGCRED=postgres:your_pg_pass -e APIKEY=your_meraki_api_key -e USERDNSDOMAIN=your_ldap_server_fqdn my-flask-project python /project/run.py 0.0.0.0

## let's create first tables
$ docker exec -ti my-flask-project bash
root@689d54ef82ad:/# cd project
root@689d54ef82ad:/project# python db_create.py

## Ready !! # first user who logs in is going to be admin

```
