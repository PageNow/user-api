# user-api

## Local Development

### Run without docker

To run the server locally (not through docker), run
```shell
$ export POSTGRES_SERVER=localhost
$ uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

### Run with docker

Run
```shell
$ docker-compose up -d # build and deploy
```

To install extension 'uuid-ossp', 

### Connect to dockerized postgres

Run
```shell
docker exec -it postgres_local psql -h localhost -U USERNAME --dbname=DBNAME
```

The extension ```uuid-ossp``` must be installed by running
```shell
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```
in postgres shell before migrating..

### Postgres migration

Run
```shell
$ docker-compose run web alembic revision --autogenerate -m "MESSAGE" # make migrations
$ docker-compose run web alembic upgrade head # migrate
```

To reset alembic versions, connect to docker postgres, drop all the tables in the datbase.

## TODO

[] Logging errors properly

## References

### FastAPI with Postgres

* https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-pydantic-models
* https://ahmed-nafies.medium.com/fastapi-with-sqlalchemy-postgresql-and-alembic-and-of-course-docker-f2b7411ee396
* https://www.jeffastor.com/blog/pairing-a-postgresql-db-with-your-dockerized-fastapi-app

### FastAPI with Cognito JWT

* https://gntrm.medium.com/jwt-authentication-with-fastapi-and-aws-cognito-1333f7f2729e

### SQLAlchemy

* http://www.dein.fr/writing-a-subquery-with-sqlalchemy-core.html
* https://overiq.com/sqlalchemy-101/crud-using-sqlalchemy-core/

## DEBUG NOTES

* sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not translate host name "db" to address: Name or service not known

- Postgres container exited with error message ```PostgreSQL Database directory appears to contain a database; Skipping initialization```
- Ran ```docker-compose down --volumes```