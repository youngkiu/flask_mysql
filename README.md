## Quick start

```shell
$ docker-compose up
```
Connect **http://localhost/api**

## How to develop

```shell
$ docker-compose run --rm --name project-db --service-ports db
```

```shell
$ conda create -n nginx_flask_postgres python=3.8
$ conda activate nginx_flask_postgres
$ pip install -r requirements.txt
app$ DEBUG=1 ./migrate.sh $PWD/../db/migrations/
app$ DEBUG=1 python upload.py ../db/wanted_temp_data.csv
app$ DEBUG=1 python $PWD/app.py
```

### Test on development

```shell
$ curl -i -X GET http://localhost:5000/api/company?name=Agi
$ curl -i -X GET http://localhost:5000/api/company?tag=tag_26
$ curl -i -X PUT -H "Content-Type: application/json" -d '{"name": "infobank", "tag_ko": "태그_5", "tag_en": "tag_5", "tag_ja": "タグ_5"}' http://localhost:5000/api/company
$ curl -i -X DELETE -H "Content-Type: application/json" -d '{"name": "Avanade Asia Pte Ltd", "tag": "tag_11"}' http://localhost:5000/api/company
```

## How to run

### nginx(:80) + flask(:5000) + postgres(:5432)

```shell
$ docker-compose up -d
$ docker-compose logs -f
```

```shell
$ docker exec -it project-app /bin/bash
# python upload.py ../db/wanted_temp_data.csv
```

### Test on production

```shell
$ curl -X GET http://localhost/api/company?name=Agi | jq '.'
$ curl -X GET http://localhost/api/company?tag=tag_26 | jq '.'
$ curl -X PUT -H "Content-Type: application/json" -d '{"name": "infobank", "tag_ko": "태그_5", "tag_en": "tag_5", "tag_ja": "タグ_5"}' http://localhost/api/company | jq '.'
$ curl -X DELETE -H "Content-Type: application/json" -d '{"name": "Avanade Asia Pte Ltd", "tag": "tag_11"}' http://localhost/api/company | jq '.'
```
