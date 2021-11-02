# user-api

## Local Development

### Run without docker

To run the server locally (not through docker), run
```shell
$ export RDS_HOST=localhost
$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
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

## Cloud Development

### Uploading Docker Image to ECR

Execute the following commands as instructed [here](https://us-west-2.console.aws.amazon.com/ecr/repositories/private/257206538165/pagenow-user-api?region=us-west-2)
```shell
$ aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 257206538165.dkr.ecr.us-west-2.amazonaws.com
$ docker build -t 257206538165.dkr.ecr.us-west-2.amazonaws.com/pagenow-user-api:latest .
$ docker push 257206538165.dkr.ecr.us-west-2.amazonaws.com/pagenow-user-api:latest
```

### Terraform Setup

Set AWS credentials as environment variables
```shell
$ export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
$ export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
$ export AWS_DEFAULT_REGION="YOUR_AWS_REGION"
```

Set RDS password by running
```shell
$ export TF_VAR_rds_password=RDS_PASSWORD
```

Then, update the cloud resources by running
```shell
$ terraform plan
$ terraform apply
```

Set up API Gateway following instructions at https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-http.html where endpoint url is 'http://${alb_dns}/{proxy}' and deploy.

### ECS RDS Setup

1. Change the target of the VPC route table 0.0.0.0/0 to Internet Gateway of the VPC.
2. SSH into EC2 instance.
3. Run `docker ps` to obtain the docker container id.
4. Run `docker exec -it DOCKER_CONTAINER_ID alembic upgrade head`.

### RDS Access using Bastion instance

1. Get the public IP address of bastion-instance and the private IP address of private-instance.
2. Update the SSH config file as follows.
```
Host bastion-instance
   HostName <Bastion Public IP>
   User ubuntu
Host private-instance
   HostName <Private IP>
   User ubuntu
   ProxyCommand ssh -q -W %h:%p bastion-instance
```
3. SSH into private-instance by running `ssh -i "~/.ssh/id_rsa" private-instance`.

### Update ECS Service after updating Django backend

After building and pushgin Docker image to ECR, run
```shell
$ python update-ecs.py --cluster=user-api-production-cluster --service=user-api-production-service
```

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
* https://stackoverflow.com/questions/3576382/select-as-in-sqlalchemy

### Asyncio

* https://medium.com/@s.zeort/asynchronous-aws-s3-client-in-python-4f6b33829da6
* https://medium.com/tysonworks/concurrency-with-boto3-41cfa300aab4
* https://www.trek10.com/blog/aws-lambda-python-asyncio

### RDS Proxy Terraform

* https://aws.plainenglish.io/have-your-lambda-functions-connect-to-rds-through-rds-proxy-c94072560eee
* https://www.jbssolutions.com/resources/blog/amazon-rds-proxy-terraform/

### Connecting to AWS instance in private subnet
* https://towardsdatascience.com/connecting-to-an-ec2-instance-in-a-private-subnet-on-aws-38a3b86f58fb

### Testing

* https://testdriven.io/blog/fastapi-crud/
* https://www.jeffastor.com/blog/testing-fastapi-endpoints-with-docker-and-pytest


## DEBUG NOTES

* sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not translate host name "db" to address: Name or service not known

- Postgres container exited with error message ```PostgreSQL Database directory appears to contain a database; Skipping initialization```
- Ran ```docker-compose down --volumes```

## Notes

* Setting up CORS is not supported (to be more accurate, unnecessarily complicated) compared to the one click if you do it at console. Also, redirecting ANY method's url path parameter to integration path paramter is not supported by Terraform. So, I left that part to be done at console.
