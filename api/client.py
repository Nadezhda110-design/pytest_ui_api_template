import allure
import requests
from typing import Optional, Dict
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApiClient:
    """
    Базовый API клиент для работы с сайтом Читай-город.
    """

    BASE_URL = "https://www.chitai-gorod.ru/api"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.chitai-gorod.ru",
            "Referer": "https://www.chitai-gorod.ru/"
        })

    @allure.step("GET запрос к {endpoint}")
    def get(self, endpoint: str, params: Optional[Dict] = None) \
            -> requests.Response:
        """Выполняет GET запрос."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        # Логируем запрос
        logger.info(f"GET {url}")
        if params:
            logger.info(f"Params: {params}")

        # Выполняем запрос
        response = self.session.get(url, params=params)

        # Логируем ответ
        logger.info(f"Response status: {response.status_code}")

        # Прикрепляем информацию к отчету Allure
        allure.attach(
            f"URL: {url}\nParams: {params}\n\nResponse: {response.text[:500]}",
            name=f"GET {endpoint}",
            attachment_type=allure.attachment_type.TEXT
        )

        return response

    @allure.step("POST запрос к {endpoint}")
    def post(self, endpoint: str, data: Optional[Dict] = None) \
            -> requests.Response:
        """Выполняет POST запрос."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        logger.info(f"POST {url}")
        if data:
            logger.info(f"Data: {data}")

        response = self.session.post(url, json=data)

        logger.info(f"Response status: {response.status_code}")

        allure.attach(
            f"URL: {url}\nData: {data}\n\nResponse: {response.text[:500]}",
            name=f"POST {endpoint}",
            attachment_type=allure.attachment_type.TEXT
        )

        return response

    def close(self):
        """Закрывает сессию."""
        self.session.close()
