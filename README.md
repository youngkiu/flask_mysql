## Quick start

```shell
$ docker-compose up
```
Connect **http://localhost**

## How to develop

### Set up the development environment

```shell
$ conda create -n flask_mysql python=3.8
$ conda activate flask_mysql
$ pip install -r requirements.txt
```

### Launch the DB server

```shell
$ docker-compose run --rm --name project-db --service-ports db
```

### Upload the initial data of the DB server

```shell
$ conda activate flask_mysql
app$ DEBUG=1 ./migrate.sh $PWD/../db/migrations/
app$ DEBUG=1 python upload.py ../db/wanted_temp_data.csv
```

### Run application server

```shell
$ conda activate flask_mysql
app$ DEBUG=1 python $PWD/app.py
```

## How to run

### flask(:5000) + mysql(:3306)

```shell
$ docker-compose build
$ docker-compose up -d
$ docker-compose logs -f
```

### Upload the initial data of the DB server

```shell
$ docker exec -it project-app /bin/bash
# python upload.py ../db/wanted_temp_data.csv
```

## How to test

### Test by pytest

```shell
$ docker exec -it project-app /bin/bash
# pytest -v
```

### Test by curl

```shell
$ curl -X GET http://localhost/company?name=Agi
$ curl -X GET http://localhost/company/tag?name=tag_26
$ curl -X PUT -H "Content-Type: application/json" -d '{"name": "infobank", "tag_ko": "태그_5", "tag_en": "tag_5", "tag_ja": "タグ_5"}' http://localhost/company/tag
$ curl -X DELETE -H "Content-Type: application/json" -d '{"name": "Avanade Asia Pte Ltd", "tag": "tag_11"}' http://localhost/company/tag
```
