Candideitor Django
==================

this is an API client for candideit.org usable in any django project.

#Tests

##Requirements
-sqlite3
-mercurial
-virtualenvwrapper

##Execution
create local virtual environment

```shell
mkvirtualenv candideitorg_django
```

install requirements

```shell
pip install -r requirements.txt
```

run script start_local_candideitorg.bash

```shell
./start_local_candideitorg.bash
```

run tests
```shell
python manage.py test candideitorg
```

Afterwards you might want to kill the candideitorg process. For that you'll have to find its pid

```shell
ps aux | grep candideitorg
```

And then kill it

```shell
kill <pid of candidaitorg process>
```
