import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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

    driver.quit()
