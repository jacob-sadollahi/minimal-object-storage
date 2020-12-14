from core.conf import app

from apps.storage.views import CheckBucketRules
from apps.user.views import Auth, Register

app.add_url_rule('/api/user/auth', view_func=Auth.as_view('auth'), methods=['POST'])
app.add_url_rule('/api/user/register', view_func=Register.as_view('register'), methods=['POST'])

app.add_url_rule('/api/storage/bucket/check/<bucket_name>', view_func=CheckBucketRules.as_view('bucket-check'), methods=['GET'])


if __name__ == '__main__':
    app.run(debug=True)
