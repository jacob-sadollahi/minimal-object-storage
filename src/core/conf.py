import os
from flask import Flask
from pymongo import MongoClient
from urllib.parse import quote_plus
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from flasgger import Swagger

app = Flask(__name__)
swag = Swagger(app)
db = MongoEngine()

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'ChangeMe!@#$')
jwt = JWTManager(app)

DEBUG = os.getenv("DEBUG", False)
db_name = os.getenv("DB_NAME", "mymongo")
db_username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "mongo_user")
db_password = quote_plus(os.getenv("MONGO_INITDB_ROOT_PASSWORD", "mongoXYZ123!@#"))
db_host = os.getenv("DB_HOST", "mongo-db")
db_port = 27017
db_authSource = "admin"
mongo_uri = f'mongodb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}?authSource={db_authSource}'

app.config['MONGODB_SETTINGS'] = {
    "db": 'admin',
    "host": mongo_uri,
}
db.init_app(app)

client = MongoClient(mongo_uri)
if db_name not in client.list_database_names():
    client[db_name]["user"].insert_one({})
    print("DB constructed")
