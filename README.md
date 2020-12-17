### Minimal object storage communication app

a fun and challenging project to communicate with [ArvanCloud](https://arvancloud.com) S3

also this could be used for AWS s3(both have almost same endpoint architecture)

#### the data flow:

![Screenshot of Data Flow](data_flow.png)

### how to run:
- #### step 1:
first of all , you should create an `env` file

```
the default is env_file.env, you could edit it inside docker-compose.yml.

required env vars:
```

- ### JWT_SECRET_KEY
- ### DB_NAME
- ### DB_HOST
  note: you should write docker service name(here is `mongo-db`)
  
- ### MONGO_INITDB_ROOT_USERNAME
- ### MONGO_INITDB_ROOT_PASSWORD
- ### S3_ACCESS_KEY
- ### S3_SECRET_KEY
- ### S3_REGION
- ### S3_ENDPOINT

there is also another environment variable called `DEBUG`, but it would not affect if you put in env file, because of `gunicorn`
- #### step 2:
create an external volume called object_storage_mongo

`docker volume create --name=object_storage_mongo`
- #### step 3:
after creating env_file.env you could simply run docker-compose.yml

`docker-compose up -d`


### Api:
1. register users with allowed_prefixes:

 - `example: curl -X POST -H "Content-Type: application/json" -d '{"email": "example@gmail.com", "password": "password", "allowed_prefixes":["arvan","aws", "sas"]}}' http://127.0.0.1:8080/middleware/api/v1/user/register`

2. user authentication:

 - `example: curl -X POST -H "Content-Type: application/json" -d '{"email": "example@gmail.com", "password": "password"}' http://127.0.0.1:8080/middleware/api/v1/user/auth`

3. create bucket:

 - `example: curl -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MDgxNDgxOTYsIm5iZiI6MTYwODE0ODE5NiwianRpIjoiNmIzMmU0NDUtNGZhMS00MDk3LWI1MDAtOTY0ZDBhY2Q3MTdjIiwiZXhwIjoxNjA4MTQ5MDk2LCJpZGVudGl0eSI6IjVmZGE1ODk3ZWIxYWUwNGM0NjBiNzdhZSIsImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.JoxTz2cqP9-VJgXKTCQHron9G49Ky0tkwZur406sMjA' http://127.0.0.1:8080/resty-api/bucket/mybucket56235454`

### Test:

there is several external/integration tests , you can run them by executing `run_tests.sh` script:

`./run_tests.sh`

the output should looks like this:

```
test_object_storage_mongo
Creating network "minimal-object-storage_default" with the default driver
Creating minimal-object-storage_mongo-db_1 ... done
Creating minimal-object-storage_middleware_1 ... done
........
----------------------------------------------------------------------
Ran 8 tests in 3.916s

OK
Stopping minimal-object-storage_middleware_1 ... done
Stopping minimal-object-storage_mongo-db_1   ... done
Removing minimal-object-storage_middleware_1 ... done
Removing minimal-object-storage_mongo-db_1   ... done
Removing network minimal-object-storage_default
test_object_storage_mongo

```

this automatically runs test containers and volume ,then at the end destroys them.

### motivation

the reason behind this project was solving `ArvanCloud Challenge`, to implement a middleware to control users `bucket` prefix, using OpenResty/Lua plus Python/Flask

## Rules:
let's assume users (A and B) defined in db, and have permission to create bucket with `arvan` prefix 
1. user A could create buckets with `arvan` prefix
2. user A could create any bucket with any prefix that is not defined in database or not allowed to another user exclusively
3. nobody could create bucket with `arvan` prefix , except users A and B


