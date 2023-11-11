from flask import Blueprint

from .users import user_router
from .yandex_api import yandex_api_router


main_router = Blueprint('main', __name__)
main_router.register_blueprint(user_router)
main_router.register_blueprint(yandex_api_router, url_prefix='/api/yandex')
