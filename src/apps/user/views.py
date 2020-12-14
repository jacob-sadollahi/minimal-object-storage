from core.conf import swag
from flasgger import SwaggerView
from apps.user.models import User
from mongoengine import DoesNotExist
from flask import jsonify, request, abort
from argon2 import PasswordHasher, exceptions
from flask_jwt_extended import create_access_token
from apps.storage.models import Prefix, BucketPrefix


class Register(SwaggerView):
    """
    creating user and allowed prefixes
    NOTE: it could be better to design superuser api to creating allowed prefixes
    """
    tags = ["user"]
    parameters = [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "id": "Register",
                "properties": {
                    "email": {"type": "string", "minLength": 5},
                    "password": {"type": "string", "minLength": 8},
                    "allowed_prefixes": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "minLength": 3}},
                },
                "required": ["email", "password", "allowed_prefixes"]
            }
        }]
    responses = {
        201: {
            'description': 'When the register process is successful, return nothing but 201 status'
        }
    }
    validation = True

    @classmethod
    def diff_prefixes_and_create(cls, values):
        prefix_objects = Prefix.objects.filter(prefix__in=values)
        prefix_list = prefix_objects.values_list('prefix')
        diff = values - set(prefix_list)
        if diff:
            allowed_prefixes_key_value = [{"prefix": data} for data in diff]
            prefix_instances = [Prefix(**data) for data in allowed_prefixes_key_value]
            prefix_objects = list(prefix_objects)
            prefix_objects.extend(list(Prefix.objects.insert(prefix_instances, load_bulk=False)))
        return prefix_objects

    @classmethod
    def check_user_duplication(cls, email):
        try:
            User.objects.get(email=email)
            abort(400, "This email already exist")
        except DoesNotExist:
            pass

    @swag.validate('Register')
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        self.check_user_duplication(email)
        allowed_prefixes = set(data.get('allowed_prefixes'))
        prefixes = self.diff_prefixes_and_create(allowed_prefixes)
        ph = PasswordHasher()
        password_hash = ph.hash(password)
        user = User(
            email=email,
            password=password_hash,
            is_active=True
        ).save()
        bucket_prefixes = [{"prefix": prefix, "user": user, "is_allowed": True} for prefix in prefixes]
        bucket_prefix_instances = [BucketPrefix(**data) for data in bucket_prefixes]
        BucketPrefix.objects.insert(bucket_prefix_instances, load_bulk=False)
        return "", 201


class Auth(SwaggerView):
    """
    authenticate with email and password
    """
    tags = ["user"]
    parameters = [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "id": "Auth",
                "properties": {
                    "email": {"type": "string", "minLength": 5},
                    "password": {"type": "string", "minLength": 8},
                },
                "required": ["email", "password"]
            }
        }]
    responses = {
        200: {
            "schema": {
                "token": {"type": "string"}
            }
        }
    }
    validation = True

    @swag.validate('Auth')
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        ph = PasswordHasher()
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            return abort(400, "Email of password is not correct.")
        try:
            ph.verify(user.password, password)
        except exceptions.VerifyMismatchError:
            return abort(400, "Email of password is not correct.")

        access_token = create_access_token(identity=str(user.id))
        return jsonify({'token': access_token})
