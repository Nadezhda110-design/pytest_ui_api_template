import allure
from typing import Optional, List, Dict, Any
from .client import ApiClient
from .models import SearchResponse, Product, AuthorSearchResponse


class SearchEndpoint:
    """
    Класс для работы с поисковыми эндпоинтами API.
    Аналог Page Object для API-тестирования.
    """

    def __init__(self, client: ApiClient):
        self.client = client

    @allure.step("Поиск по строке запроса")
    def search(self, query: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Выполняет поиск по строке запроса.

        Args:
            query: Поисковый запрос
            page: Номер страницы
            limit: Количество результатов на странице

        Returns:
            Dict с результатами поиска
        """
        params = {
            "phrase": query,
            "page": page,
            "limit": limit
        }

        response = self.client.get("catalog/search", params=params)

        # Проверяем статус ответа
        assert response.status_code == 200, f"Ошибка API: {response.status_code}"
        x = response.json()
        return response.json()

    @allure.step("Поиск по автору")
    def search_by_author(self, author: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Выполняет поиск книг по автору.

        Args:
            author: Имя автора
            page: Номер страницы
            limit: Количество результатов на странице
        """
        # Для поиска по автору используем тот же эндпоинт,
        # но с дополнительным фильтром
        params = {
            "authors[]": author,
            "page": page,
            "limit": limit
        }

        response = self.client.get("catalog/search", params=params)
        assert response.status_code == 200

        return response.json()

    @allure.step("Получить детальную информацию о книге")
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Получает детальную информацию о книге по ID.
        """
        response = self.client.get(f"product/{product_id}")
        assert response.status_code == 200

        return response.json()

    @allure.step("Получить популярные поисковые запросы")
    def get_popular_searches(self) -> List[str]:
        """
        Получает список популярных поисковых запросов.
        """
        response = self.client.get("search/popular")
        assert response.status_code == 200

        return response.json()

    @allure.step("Проверить наличие книги в магазинах")
    def check_availability(self, product_id: str, city_id: str = "1") -> Dict[str, Any]:
        """
        Проверяет наличие книги в магазинах.

        Args:
            product_id: ID книги
            city_id: ID города (1 = Москва)
        """
        params = {
            "cityId": city_id,
            "productIds[]": product_id
        }

        response = self.client.get("stock/availability", params=params)
        assert response.status_code == 200

        return response.json()