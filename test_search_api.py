import allure
import pytest
from api.client import ApiClient
from api.endpoints import SearchEndpoint
from api.models import SearchResponse, Product, AuthorSearchResponse


@allure.feature("API Поиск на сайте Читай-город")
@allure.story("Поисковый API")
@allure.link("https://www.chitai-gorod.ru/api", name="API документация")
class TestSearchAPI:

    def setup_method(self):
        """Подготовка перед каждым тестом."""
        self.client = ApiClient()
        self.search_endpoint = SearchEndpoint(self.client)

    def teardown_method(self):
        """Очистка после каждого теста."""
        self.client.close()

    @allure.title("API: Поиск книги по названию на кириллице")
    @allure.description("Проверяем, что API возвращает книги по русскому названию")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("API-TC-001", name="Поиск по русскому названию")
    @pytest.mark.parametrize("query,expected_min_results", [
        ("Гарри Поттер", 5),
        ("Война и мир", 3),
        ("Мастер и Маргарита", 2)
    ])
    def test_search_by_russian_title(self, query, expected_min_results):
        with allure.step(f"Выполняем поиск по запросу '{query}'"):
            response_data = self.search_endpoint.search(query)

            # Преобразуем ответ в модель Pydantic для валидации
            search_response = SearchResponse(**response_data)

        with allure.step("Проверяем структуру ответа"):
            assert search_response.total >= 0, "Общее количество должно быть неотрицательным"
            assert search_response.page >= 1, "Номер страницы должен быть >= 1"
            assert search_response.limit > 0, "Лимит должен быть положительным"

        with allure.step(f"Проверяем, что найдено хотя бы {expected_min_results} книг"):
            assert search_response.total >= expected_min_results, \
                f"Найдено только {search_response.total} книг, ожидалось минимум {expected_min_results}"

            # Проверяем, что на текущей странице есть товары
            assert len(search_response.items) > 0, "На странице нет товаров"

        with allure.step("Проверяем соответствие найденных книг запросу"):
            # Проверяем, что хотя бы в одной книге есть слова из запроса в названии
            query_words = query.lower().split()
            found_matching = False

            for product in search_response.items[:5]:  # Проверяем первые 5
                title_lower = product.title.lower()
                if any(word in title_lower for word in query_words):
                    found_matching = True
                    break

            assert found_matching, f"Ни одна из первых 5 книг не содержит слова из запроса '{query}'"

        with allure.step("Логируем результаты"):
            print(f"\n✅ Найдено книг по запросу '{query}': {search_response.total}")
            print(f"📚 Первые 3 книги:")
            for i, product in enumerate(search_response.items[:3], 1):
                print(f"   {i}. {product.title} - {product.price.current}₽")

    @allure.title("API: Поиск книги по названию на латинице")
    @allure.description("Проверяем, что API возвращает книги по английскому названию")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.testcase("API-TC-002")
    @pytest.mark.parametrize("query", ["Harry Potter", "Lord of the Rings", "1984"])
    def test_search_by_english_title(self, query):
        with allure.step(f"Выполняем поиск по запросу '{query}'"):
            response_data = self.search_endpoint.search(query)
            search_response = SearchResponse(**response_data)

        with allure.step("Проверяем наличие результатов"):
            assert search_response.total > 0, f"По запросу '{query}' не найдено книг"
            assert len(search_response.items) > 0, "На странице нет товаров"

        with allure.step("Проверяем цены товаров"):
            for product in search_response.items[:3]:
                assert product.price.current > 0, f"Цена книги '{product.title}' должна быть положительной"

        print(f"\n✅ Найдено книг по запросу '{query}': {search_response.total}")

    @allure.title("API: Поиск книг по автору на кириллице")
    @allure.description("Проверяем, что API возвращает книги по русскому автору")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("API-TC-003")
    @pytest.mark.parametrize("author,expected_min_books", [
        ("Роулинг", 3),
        ("Достоевский", 5),
        ("Пушкин", 5)
    ])
    def test_search_by_russian_author(self, author, expected_min_books):
        with allure.step(f"Выполняем поиск по автору '{author}'"):
            response_data = self.search_endpoint.search(author)
            search_response = SearchResponse(**response_data)

        with allure.step(f"Проверяем, что найдено минимум {expected_min_books} книг"):
            assert search_response.total >= expected_min_books, \
                f"По автору '{author}' найдено только {search_response.total} книг"

        with allure.step("Проверяем, что книги принадлежат указанному автору"):
            # Проверяем первые несколько книг
            for product in search_response.items[:5]:
                if product.author:
                    assert author.lower() in product.author.lower(), \
                        f"Книга '{product.title}' не принадлежит автору '{author}' (автор: {product.author})"

        with allure.step("Проверяем наличие ID товаров"):
            for product in search_response.items:
                assert product.id, "У книги отсутствует ID"
                assert len(product.id) > 0, "ID книги не может быть пустым"

        print(f"\n✅ Найдено книг по автору '{author}': {search_response.total}")

    @allure.title("API: Поиск книг по автору на латинице")
    @allure.description("Проверяем, что API возвращает книги по английскому автору")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("API-TC-004")
    @pytest.mark.parametrize("author", ["Rowling", "Tolkien", "Orwell"])
    def test_search_by_english_author(self, author):
        with allure.step(f"Выполняем поиск по автору '{author}'"):
            response_data = self.search_endpoint.search(author)
            search_response = SearchResponse(**response_data)

        with allure.step("Проверяем наличие результатов"):
            assert search_response.total > 0, f"По автору '{author}' не найдено книг"

        with allure.step("Проверяем структуру товаров"):
            for product in search_response.items[:3]:
                # Проверяем обязательные поля
                assert product.title, "Отсутствует название книги"
                assert product.price.current > 0, "Цена должна быть положительной"

                # Проверяем, что автор указан (если есть)
                if product.author:
                    print(f"   📖 {product.title} - {product.author}")

        print(f"\n✅ Найдено книг по автору '{author}': {search_response.total}")

    @allure.title("API: Негативный тест - пустой поисковый запрос")
    @allure.description("Проверяем поведение API при пустом поисковом запросе")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.testcase("API-TC-005")
    def test_empty_search_query(self):
        with allure.step("Выполняем поиск с пустым запросом"):
            response = self.client.get("catalog/search", params={"phrase": ""})

        with allure.step("Проверяем код ответа"):
            # API может вернуть 400 (Bad Request) или 200 с пустым списком
            assert response.status_code in [200, 400], \
                f"Неожиданный код ответа: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            with allure.step("Проверяем ответ при успешном запросе"):
                assert "total" in data, "Отсутствует поле total"
                assert "items" in data, "Отсутствует поле items"
                print(f"\n✅ Пустой запрос вернул {data.get('total', 0)} результатов")
        else:
            with allure.step("Проверяем сообщение об ошибке"):
                error_data = response.json()
                assert "error" in error_data or "message" in error_data, \
                    "Отсутствует сообщение об ошибке"
                print(f"\n✅ Пустой запрос обработан корректно: {error_data}")

    @allure.title("API: Проверка пагинации")
    @allure.description("Проверяем работу пагинации в поиске")
    @allure.severity(allure.severity_level.MINOR)
    @allure.testcase("API-TC-006")
    @pytest.mark.parametrize("query,page,limit", [
        ("Гарри Поттер", 1, 5),
        ("Гарри Поттер", 2, 5),
        ("Гарри Поттер", 1, 10)
    ])
    def test_search_pagination(self, query, page, limit):
        with allure.step(f"Выполняем поиск с page={page}, limit={limit}"):
            response_data = self.search_endpoint.search(query, page=page, limit=limit)
            search_response = SearchResponse(**response_data)

        with allure.step("Проверяем параметры пагинации"):
            assert search_response.page == page, f"Ожидалась страница {page}, получена {search_response.page}"
            assert search_response.limit == limit, f"Ожидался лимит {limit}, получен {search_response.limit}"
            assert len(
                search_response.items) <= limit, f"Количество элементов превышает лимит: {len(search_response.items)} > {limit}"

        print(
            f"\n✅ Пагинация работает корректно: страница {page}, показано {len(search_response.items)} из {search_response.total}")

    @allure.title("API: Проверка детальной информации о книге")
    @allure.description("Получаем детальную информацию о конкретной книге")
    @allure.severity(allure.severity_level.MINOR)
    @allure.testcase("API-TC-007")
    def test_product_details(self):
        # Сначала находим какую-нибудь книгу
        with allure.step("Находим книгу для теста"):
            search_response = SearchResponse(**self.search_endpoint.search("Гарри Поттер"))
            assert len(search_response.items) > 0, "Не найдено книг для теста"

            test_product = search_response.items[0]
            product_id = test_product.id

        with allure.step(f"Получаем детальную информацию о книге ID={product_id}"):
            product_details = self.search_endpoint.get_product_details(product_id)

        with allure.step("Проверяем детальную информацию"):
            assert product_details.get("id") == product_id, "ID книги не совпадает"
            assert "title" in product_details, "Отсутствует название"
            assert "description" in product_details, "Отсутствует описание"
            assert "characteristics" in product_details, "Отсутствуют характеристики"

        print(f"\n✅ Детальная информация получена для книги: {product_details.get('title')}")