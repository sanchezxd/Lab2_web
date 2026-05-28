from flask import Flask
from flask_restplus import Api
from matches import api as matches_namespace

app = Flask(__name__)

# Инициализируем Swagger API
api = Api(app, version='1.0', title='Football Matches REST API',
          description='Документированный веб-сервис для ведения статистики футбольных матчей')

# Подключаем созданный неймспейс к общему дереву API
api.add_namespace(matches_namespace, path='/matches')

if __name__ == '__main__':
    app.run(debug=True)
