import unittest
import json
from main import app

class FootballApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_get_all_matches(self):
        """Проверка получения стартового списка матчей"""
        response = self.app.get('/matches/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)

    def test_02_get_statistics(self):
        """Проверка работы математического блока вычисления статистики"""
        response = self.app.get('/matches/actions/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('attendance', data)
        self.assertEqual(data['attendance']['max'], 45000)

    def test_03_create_match(self):
        """Проверка CRUD-операции: добавление записи"""
        new_match = {
            'id': '4', 'team_home': 'Рубин', 'team_away': 'Ростов',
            'goals_home': 2, 'goals_away': 0, 'attendance': 12000
        }
        response = self.app.post('/matches/', data=json.dumps(new_match), content_type='application/json')
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
