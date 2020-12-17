#!/bin/bash

docker volume create --name=test_object_storage_mongo || true
docker-compose -f docker-compose.test.yml up -d
sleep 2
cd tests && python3 -m unittest test_object_storage_externally.TestObjectStorage
cd .. && docker-compose -f docker-compose.test.yml down
docker volume rm test_object_storage_mongo || true