from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Эта настройка нужна, чтобы Flask корректно отображал кириллицу (русский язык) в JSON,
# а не конвертировал её в юникод-последовательности вида \u0421
app.config['JSON_AS_ASCII'] = False

# Имитация базы данных: список словарей с информацией о футбольных матчах
matches = [
    {
        "id": 1, 
        "home_team": "Спартак", 
        "away_team": "Зенит", 
        "home_score": 1, 
        "away_score": 2, 
        "date": "2023-10-15",
        "stadium": "Открытие Банк Арена"
    },
    {
        "id": 2, 
        "home_team": "ЦСКА", 
        "away_team": "Динамо", 
        "home_score": 0, 
        "away_score": 0, 
        "date": "2023-10-16",
        "stadium": "ВЭБ Арена"
    }
]

# Вспомогательная функция для генерации нового ID (как автоинкремент в базах данных)
def get_next_id():
    if len(matches) == 0:
        return 1
    return max(match["id"] for match in matches) + 1


# ==========================================
# REST API ЭНДПОИНТЫ (МАРШРУТЫ)
# ==========================================

# 1. READ ALL (Получить список всех матчей)
@app.route('/api/matches', methods=['GET'])
def get_matches():
    return jsonify({"matches": matches, "count": len(matches)}), 200

# 2. READ ONE (Получить конкретный матч по ID)
@app.route('/api/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    # Ищем матч с нужным ID в списке
    match = next((m for m in matches if m["id"] == match_id), None)
    if match is None:
        # Если матч не найден, возвращаем ошибку 404 Not Found
        abort(404, description="Матч с таким ID не найден")
    
    return jsonify({"match": match}), 200

# 3. CREATE (Добавить новый матч)
@app.route('/api/matches', methods=['POST'])
def create_match():
    # Проверяем, что запрос пришел в формате JSON
    if not request.json:
        abort(400, description="Запрос должен быть в формате JSON")
    
    # Обязательные поля для создания матча
    required_fields = ['home_team', 'away_team', 'date']
    for field in required_fields:
        if field not in request.json:
            abort(400, description=f"Отсутствует обязательное поле: {field}")
            
    # Формируем новый объект матча
    new_match = {
        "id": get_next_id(),
        "home_team": request.json['home_team'],
        "away_team": request.json['away_team'],
        # Используем метод get(), чтобы поставить 0, если счет не передан (матч еще не сыгран)
        "home_score": request.json.get('home_score', 0),
        "away_score": request.json.get('away_score', 0),
        "date": request.json['date'],
        "stadium": request.json.get('stadium', 'Неизвестный стадион')
    }
    
    matches.append(new_match)
    # Возвращаем созданный матч и код 201 (Created)
    return jsonify({"match": new_match, "message": "Матч успешно добавлен"}), 201

# 4. UPDATE (Обновить данные матча, например, изменить счет)
@app.route('/api/matches/<int:match_id>', methods=['PUT'])
def update_match(match_id):
    match = next((m for m in matches if m["id"] == match_id), None)
    if match is None:
        abort(404, description="Матч с таким ID не найден")
    
    if not request.json:
        abort(400, description="Запрос должен быть в формате JSON")
        
    # Обновляем поля, если они переданы в запросе
    match['home_team'] = request.json.get('home_team', match['home_team'])
    match['away_team'] = request.json.get('away_team', match['away_team'])
    match['home_score'] = request.json.get('home_score', match['home_score'])
    match['away_score'] = request.json.get('away_score', match['away_score'])
    match['date'] = request.json.get('date', match['date'])
    match['stadium'] = request.json.get('stadium', match['stadium'])
    
    return jsonify({"match": match, "message": "Данные матча обновлены"}), 200

# 5. DELETE (Удалить матч)
@app.route('/api/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    global matches
    match = next((m for m in matches if m["id"] == match_id), None)
    if match is None:
        abort(404, description="Матч с таким ID не найден")
        
    # Пересобираем список, исключая удаляемый элемент
    matches = [m for m in matches if m["id"] != match_id]
    
    return jsonify({"result": True, "message": f"Матч с ID {match_id} успешно удален"}), 200

# Глобальный обработчик ошибок
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
