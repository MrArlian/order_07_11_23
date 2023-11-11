from flask import Flask

from router import main_router


app = Flask(
    import_name=__name__,
    template_folder='template',
    static_folder='static',
    static_url_path='/'
)
app.register_blueprint(main_router)


if __name__ == '__main__':
    app.run('0.0.0.0', '8000', debug=True)
