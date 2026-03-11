# pytest_ui_api_template

## Шаблон для автоматизации тестирования на python

### Шаги
1. Склонировать проект 'git clone https://github.com/Nadezhda110-design/pytest_ui_api_template.git' 

2. Установить зависимости 'pip install -r requirements.txt'

3. Запустить тесты 
 - Все тесты 'pytest'
 - Только UI‑тесты 'pytest -m ui -v'
 - Только API‑тесты 'pytest -m api -v'
 - С отчётом Allure 'pytest --alluredir./=allure-results' 'allure serve allure-results'


### Стек:
- pytest
- selenium
- requests
- _sqlalchemy_
- allure
- config

### Струткура:
- ./test - тесты
- - tests/test_search_ui.py – UI‑тесты поиска (5 шт.)
- - tests/test_search_api.py – API‑тесты поиска (5 шт.)
- ./pages - Page Object для UI‑тестов
- ./api - клиент для работы с API
- conftest.py – фикстуры pytest
- pytest.ini – маркеры для раздельного запуска
- requirements.txt – зависимости


### Библиотеки (!)
- pyp install pytest
- pip install selenium
- pip install webdriver-manager

### Полезные ссылки
- [Подсказка по markdown](https://www.markdownguide.org/basic-syntax/)
- [Генератор файла .gitignore](https://www.toptal.com/developers/gitignore)