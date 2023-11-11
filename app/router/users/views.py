from flask import Blueprint, render_template, request, redirect


user_router = Blueprint('user', __name__)


@user_router.get('/')
def index():
    if not request.cookies.get('yandex_token'):
        return redirect('/api/yandex/login')
    return render_template('index.html')
