from flask_restplus import Namespace, Resource, fields, reqparse

# Создаем изолированное пространство имен (Namespace) для матчей
api = Namespace('matches', description='Операции с футбольными матчами')

# Определение Swagger-модели данных матча для автоматического маршалинга и валидации
match_model = api.model('Match', {
    'id': fields.String(required=True, description='Идентификатор матча'),
    'team_home': fields.String(required=True, description='Команда хозяев'),
    'team_away': fields.String(required=True, description='Команда гостей'),
    'goals_home': fields.Integer(required=True, description='Голы хозяев'),
    'goals_away': fields.Integer(required=True, description='Голы гостей'),
    'attendance': fields.Integer(required=True, description='Посещаемость матча')
})

# База данных в оперативной памяти (In-Memory) с начальными значениями
MATCHES = [
    {'id': '1', 'team_home': 'Спартак', 'team_away': 'Зенит', 'goals_home': 1, 'goals_away': 2, 'attendance': 45000},
    {'id': '2', 'team_home': 'ЦСКА', 'team_away': 'Динамо', 'goals_home': 0, 'goals_away': 0, 'attendance': 25000},
    {'id': '3', 'team_home': 'Локомотив', 'team_away': 'Краснодар', 'goals_home': 3, 'goals_away': 1, 'attendance': 18000}
]

@api.route('/')
class MatchList(Resource):
    @api.doc('list_matches')
    @api.marshal_list_with(match_model)
    def get(self):
        """Получение списка всех футбольных матчей"""
        return MATCHES

    @api.doc('create_match')
    @api.expect(match_model)
    @api.marshal_with(match_model, code=201)
    def post(self):
        """Добавление новой записи о матче (Валидация через expect)"""
        new_match = api.payload
        MATCHES.append(new_match)
        return new_match, 201

@api.route('/<id>')
@api.param('id', 'Идентификатор футбольного матча')
@api.response(404, 'Матч с указанным ID не найден')
class MatchResource(Resource):
    @api.doc('get_match')
    @api.marshal_with(match_model)
    def get(self, id):
        """Получение информации о матче по его ID"""
        for match in MATCHES:
            if match['id'] == id:
                return match
        api.abort(404)

    @api.doc('update_match')
    @api.expect(match_model)
    @api.marshal_with(match_model)
    def put(self, id):
        """Обновление записи о матче по его ID"""
        for match in MATCHES:
            if match['id'] == id:
                match.update(api.payload)
                return match
        api.abort(404)

    @api.doc('delete_match')
    @api.response(204, 'Запись о матче успешно удалена')
    def delete(self, id):
        """Удаление записи о матче по его ID"""
        global MATCHES
        MATCHES = [m for m in MATCHES if m['id'] != id]
        return '', 204

# Настройка парсера аргументов для сортировки в GET-запросе
sort_parser = reqparse.RequestParser()
sort_parser.add_argument('field', type=str, required=True, help='Поле для сортировки (id, team_home, team_away, goals_home, goals_away, attendance)')
sort_parser.add_argument('reverse', type=str, default='false', help='Сортировка по убыванию (true/false)')

@api.route('/actions/sort')
class MatchSort(Resource):
    @api.doc('sort_matches')
    @api.expect(sort_parser)
    @api.marshal_list_with(match_model)
    def get(self):
        """Динамическая сортировка по абсолютно любому полю записи"""
        args = sort_parser.parse_args()
        field = args['field']
        reverse = args['reverse'].lower() == 'true'
        try:
            sorted_matches = sorted(MATCHES, key=lambda x: x.get(field), reverse=reverse)
            return sorted_matches
        except TypeError:
            api.abort(400, "Невозможно выполнить сортировку по указанному полю")

@api.route('/actions/stats')
class MatchStats(Resource):
    @api.doc('get_stats')
    def get(self):
        """Вычисление min, max и аvg по всем числовым полям выборки"""
        if not MATCHES:
            return {"message": "Данные отсутствуют"}, 400
        
        stats = {}
        numeric_fields = ['goals_home', 'goals_away', 'attendance']
        
        for field in numeric_fields:
            values = [m[field] for m in MATCHES]
            stats[field] = {
                'min': min(values),
                'max': max(values),
                'avg': round(sum(values) / len(values), 2)
            }
        return stats
