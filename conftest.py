import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import allure
import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Теперь импортируем наш модуль
from api.client import ApiClient

@pytest.fixture
def driver():
    """Фикстура для создания и закрытия драйвера браузера."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    # Для запуска в CI/CD можно добавить headless режим
    # options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Добавляем ожидание для стабильности
    driver.implicitly_wait(5)

    yield driver

    # Прикрепляем скриншот в случае падения теста
    if hasattr(pytest, "current_test") and pytest.current_test.rep_call.failed:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="screenshot_on_failure",
            attachment_type=allure.attachment_type.PNG
        )

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для получения результата теста."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def api_client():
    """Фикстура для создания API клиента."""
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture
def search_endpoint(api_client):
    """Фикстура для создания эндпоинта поиска."""
    from api.endpoints import SearchEndpoint
    return SearchEndpoint(api_client)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для добавления информации в отчет при падении теста."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # При падении теста добавляем дополнительную информацию
        if hasattr(item, "funcargs"):
            if "api_client" in item.funcargs:
                client = item.funcargs["api_client"]
                allure.attach(
                    "API тест упал. Проверьте запросы выше.",
                    name="failure_info",
                    attachment_type=allure.attachment_type.TEXT
                )