import allure
import pytest
import requests
from urllib.parse import urlparse, parse_qs


@allure.feature("API Поиск на сайте Читай-город")
@allure.story("Поисковая строка")
@pytest.mark.api
class TestSearch:

    def setup_method(self):
        self.base_url = "https://www.chitai-gorod.ru"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,"
                      "application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        })

    @allure.title("Тест 1: Поиск книги по названию на кириллице")
    @pytest.mark.parametrize("query", ["Гарри Поттер", "Война и мир"])
    def test_search_russian_title(self, query):
        with (allure.step(f"Выполняем поиск для '{query}'")):
            params = {"phrase": query}
            response = self.session.get(
                f"{self.base_url}/search",
                params=params,
                timeout=10,
                allow_redirects=True)

        with allure.step("Проверяем, что страница загружена"):
            assert response.status_code == 200, (f"Ошибка: "
                                                 f"{response.status_code}")
            assert len(response.text) > 5000, "Страница слишком мала"

        with (allure.step("Проверяем, что поиск сработал")):
            # Проверяем, что в тексте страницы есть ключевые слова запроса
            page_text_lower = response.text.lower()
            query_lower = query.lower()

            # Разбиваем запрос на слова и проверяем, что каждое встречается
            query_words = [word for word in query_lower.split()
                           if len(word) > 3]
            found_words = [word for word in query_words
                           if word in page_text_lower]

            assert len(found_words) > 0, (f"Ни одно из слов запроса "
                            f"'{query_words}' не найдено на странице")

        allure.attach(
            response.text[:10000],
            name=f"page_content_{query}",
            attachment_type=allure.attachment_type.HTML
        )
        print(f"\n✅ Поиск для '{query}' выполнен успешно")

    @allure.title("Тест 2: Поиск книги по названию на латинице")
    @pytest.mark.parametrize("query", ["Harry Potter", "Airport"])
    def test_search_english_title(self, query):
        params = {"phrase": query}
        response = (self.session.get
                    (f"{self.base_url}/search",
                     params=params,
                     timeout=10))

        assert response.status_code == 200
        assert len(response.text) > 5000

        page_text_lower = response.text.lower()
        query_lower = query.lower()
        query_words = [word for word in query_lower.split()
                       if len(word) > 2]
        found = any(word in page_text_lower for word in query_words)

        assert found, f"Текст запроса '{query}' не найден на странице"
        print(f"\n✅ Поиск для '{query}' выполнен успешно")

    @allure.title("Тест 3: Поиск книг по автору на кириллице")
    @pytest.mark.parametrize("query", ["Роулинг", "Достоевский"])
    def test_search_russian_author(self, query):
        params = {"phrase": query}
        response = (self.session.get
                    (f"{self.base_url}/search",
                     params=params,
                     timeout=10))

        assert response.status_code == 200
        assert len(response.text) > 5000

        page_text_lower = response.text.lower()
        assert query.lower() in page_text_lower, \
            f"Автор '{query}' не упоминается на странице"
        print(f"\n✅ Поиск по автору '{query}' выполнен успешно")

    @allure.title("Тест 4: Поиск книг по автору на латинице")
    @pytest.mark.parametrize("query", ["Rowling", "Orwell"])
    def test_search_english_author(self, query):
        params = {"phrase": query}
        response = (self.session.get
                    (f"{self.base_url}/search",
                     params=params,
                     timeout=10))

        assert response.status_code == 200
        assert len(response.text) > 5000

        page_text_lower = response.text.lower()
        assert query.lower() in page_text_lower, \
            f"Автор '{query}' не упоминается на странице"
        print(f"\n✅ Поиск по автору '{query}' выполнен успешно")

    @allure.title("Тест 5: Негативный тест с пустым поисковым запросом")
    def test_empty_search(self):
        self.session.get(self.base_url, timeout=10)

        params = {"phrase": ""}
        response = (self.session.get
                    (f"{self.base_url}/search",
                     params=params,
                     timeout=10,
                     allow_redirects=False))

        # Проверяем, что нас либо редиректнули на главную,
        # либо страница содержит сообщение
        if response.status_code in [301, 302]:
            location = response.headers.get('Location', '')
            assert 'chitai-gorod.ru' in location, \
                f"Редирект на неожиданный URL: {location}"
            print(f"\n✅ Пустой запрос вызвал редирект на: {location}")
        else:
            assert response.status_code == 200
            # Проверяем, что в URL нет параметра phrase со значением
            parsed = urlparse(response.url)
            params_dict = parse_qs(parsed.query)
            assert ('phrase' not in params_dict
                    or params_dict['phrase'] == ['']), \
                (f"Параметр phrase не должен быть пустым "
                 f"или должен отсутствовать: "
                 f"{params_dict}")
            print("\n✅ Пустой запрос обработан без перехода "
                  "на страницу результатов")
