from flasgger import SwaggerView
from flask import jsonify
from apps.storage.models import Prefix, BucketPrefix
from flask_jwt_extended import jwt_required, get_jwt_identity


class CheckBucketRules(SwaggerView):
    """
    check if user allowed to create bucket with given prefix or not
    """
    tags = ["bucket"]
    parameters = [
        {
            "name": "Authorization",
            "description": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
        },
        {
            "in": "path",
            "required": True,
            "id": "CheckBucketRules",
            "name": "bucket_name",
            "type": "string",
        }]

    @jwt_required
    def get(self, bucket_name):
        guess_prefixes = list(map(lambda x: bucket_name[:x], range(3, len(bucket_name) + 1)))
        user_id = get_jwt_identity()
        prefixes = Prefix.objects.filter(prefix__in=guess_prefixes).values_list('id')
        users_with_this_prefixes = BucketPrefix.objects.filter(prefix__in=prefixes).values_list('user', 'is_allowed')
        user_allow = {}
        user_allow.update(map(lambda x: (str(x[0].id), x[1]), users_with_this_prefixes))
        if not user_allow or (user_id in user_allow.keys() and user_allow.get(user_id)):
            return jsonify({"allowed": True})
        return jsonify({"msg": "You're not allowed to create this bucket name since the prefix is restricted"}), 403
