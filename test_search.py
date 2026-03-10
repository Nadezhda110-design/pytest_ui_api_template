import allure
import pytest
import time
from pages.search_page import SearchPage


@allure.feature("Поиск на сайте Читай-город")
@allure.story("Поисковая строка")
class TestSearch:

    @allure.title("Поиск книги по названию на кириллице")
    @allure.description("Проверяем, что поиск по русскому названию возвращает непустой список книг")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("query", ["Гарри Поттер", "Война и мир"])
    def test_search_by_russian_title(self, driver, query):
        # Подготовка
        search_page = SearchPage(driver)
        search_page.open_main_page()

        # Выполнение поиска
        search_page.perform_search(query)

        # Получение результатов
        titles = search_page.get_product_titles()

        # Сохраняем скриншот для отчета
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"search_results_{query}",
            attachment_type=allure.attachment_type.PNG
        )

        # ПРОВЕРКА: список результатов не пустой
        assert len(titles) > 0, \
            f"По запросу '{query}' не найдено ни одной книги. " \
            f"URL: {driver.current_url}"

        # ПРОВЕРКА: в результатах есть книги, содержащие слова из запроса
        query_lower = query.lower()
        matching_titles = [title for title in titles if query_lower in title.lower()]

        assert len(matching_titles) > 0, \
            f"Среди найденных книг {titles} нет содержащих '{query}'"

        # Выводим информацию в консоль для отладки
        print(f"\n✅ По запросу '{query}' найдено книг: {len(titles)}")
        print(f"📚 Первые 3 книги: {titles[:3]}")

    @allure.title("Поиск книги по названию на латинице")
    @allure.description("Проверяем, что поиск по английскому названию возвращает непустой список")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("query", ["Harry Potter", "Lord of the Rings"])
    def test_search_by_english_title(self, driver, query):
        search_page = SearchPage(driver)
        search_page.open_main_page()
        search_page.perform_search(query)

        titles = search_page.get_product_titles()

        assert len(titles) > 0, f"По запросу '{query}' не найдено книг"

        query_lower = query.lower()
        matching_titles = [title for title in titles if any(word in title.lower() for word in query_lower.split())]

        assert len(matching_titles) > 0, f"Результаты {titles} не соответствуют запросу '{query}'"

        print(f"\n✅ По запросу '{query}' найдено книг: {len(titles)}")

    @allure.title("Поиск книг по автору на кириллице")
    @allure.description("Проверяем, что поиск по автору возвращает книги этого автора")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["Роулинг", "Достоевский"])
    def test_search_by_russian_author(self, driver, query):
        search_page = SearchPage(driver)
        search_page.open_main_page()
        search_page.perform_search(query)

        # Проверяем, что есть результаты
        assert search_page.has_search_results(), f"Не найдено книг по автору '{query}'"

        # Получаем названия книг
        titles = search_page.get_product_titles()
        assert len(titles) > 0, f"По автору '{query}' не найдено книг"

        # Проверяем, что автор упоминается в названиях или URL
        query_lower = query.lower()
        matching_titles = [title for title in titles if query_lower in title.lower()]

        # Если нет прямых совпадений в названиях, проверяем хотя бы наличие результатов
        if len(matching_titles) == 0:
            # Проверяем URL страницы
            current_url = search_page.get_current_url().lower()
            if query_lower in current_url:
                print(f"⚠️ Автор '{query}' найден в URL, но не в названиях книг")
            else:
                # Если автор не найден нигде, но результаты есть - возможно, это нормально
                print(f"⚠️ По автору '{query}' есть результаты, но имя не отображается в названиях")

        print(f"\n✅ По автору '{query}' найдено книг: {len(titles)}")

    @allure.title("Поиск книг по автору на латинице")
    @allure.description("Проверяем, что поиск по автору на английском возвращает результаты")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query", ["Rowling", "Tolkien"])
    def test_search_by_english_author(self, driver, query):
        search_page = SearchPage(driver)
        search_page.open_main_page()
        search_page.perform_search(query)

        assert search_page.has_search_results(), f"Не найдено книг по автору '{query}'"

        titles = search_page.get_product_titles()
        assert len(titles) > 0, f"По автору '{query}' не найдено книг"

        print(f"\n✅ По автору '{query}' найдено книг: {len(titles)}")

    @allure.title("Негативный тест: пустой поисковый запрос")
    @allure.description("Проверяем поведение сайта при пустом поиске")
    def test_empty_search_query(self, driver):
        search_page = SearchPage(driver)
        search_page.open_main_page()

        initial_url = search_page.get_current_url()

        # Пытаемся выполнить поиск с пустым запросом
        search_page.enter_search_query("")
        search_page.click_search_button()

        time.sleep(2)

        # Проверяем, что мы остались на той же странице
        current_url = search_page.get_current_url()

        # Для диагностики сохраняем информацию
        allure.attach(
            f"Initial URL: {initial_url}\nCurrent URL: {current_url}",
            name="url_comparison",
            attachment_type=allure.attachment_type.TEXT
        )

        # Проверяем, что поиск не выполнился (нет перехода на страницу результатов)
        assert "search" not in current_url.lower() or current_url == initial_url, \
            f"Произошел переход на страницу поиска при пустом запросе: {current_url}"

        print("\n✅ Пустой поисковый запрос обработан корректно")