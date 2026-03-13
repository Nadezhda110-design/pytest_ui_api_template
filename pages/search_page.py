import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SearchPage:
    """
    Page Object для главной страницы и страницы результатов поиска.
    Актуальные локаторы для сайта Читай-город.
    """

    # --- Локаторы  ---
    _search_input_locator = (By.CSS_SELECTOR,
                             "input.search-form__input--search#app-search")
    _search_button_locator = (By.CSS_SELECTOR,
                            "button.search-form__button-search[type='submit']")

    # Локатор для карточки товара
    _product_card_locator = (By.CSS_SELECTOR,
                             "article.product-card, div.product-card")

    # Локатор для названия книги
    _product_title_locator = (By.CSS_SELECTOR,
                              "a.product-card__title")

    #  Альтернативный локатор для названия (если структура меняется)
    _product_title_alt_locator = (By.CSS_SELECTOR,
                                  "[class*='product-card__title']")

    #  Локатор для автора
    # В ссылке есть атрибут title с полным именем автора
    _product_author_locator = (By.CSS_SELECTOR,
                               "a.product-card__title")

    # Локатор для сообщения "Ничего не найдено"
    _no_results_message_locator = (By.CSS_SELECTOR,
                        ".catalog-empty-message, "
                        ".not-found-message, "
                        ".empty-results")

    # Локатор для пагинации (признак того, что результаты загружены)
    _pagination_locator = (By.CSS_SELECTOR,
                           ".pagination, .catalog-pagination")

    # Локатор для счетчика результатов
    _results_count_locator = (By.CSS_SELECTOR,
                    ".catalog-count, .products-count, .search-results-count")

    # -------------------------------------------------

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    URL = "https://www.chitai-gorod.ru"

    @allure.step("Открыть главную страницу")
    def open_main_page(self, url: str = URL):
        """Открывает главную страницу сайта."""
        self.driver.get(url)
        self.driver.maximize_window()
        # Ждем загрузки поисковой строки
        self.wait.until(EC.visibility_of_element_located
                        (self._search_input_locator))

    @allure.step("Ввести поисковый запрос: '{query}'")
    def enter_search_query(self, query: str):
        """Вводит текст в поле поиска."""
        search_input = self.wait.until(EC.element_to_be_clickable
                                       (self._search_input_locator))
        search_input.clear()
        search_input.send_keys(query)

        # Проверяем, что текст ввелся
        entered_value = search_input.get_attribute("value")
        assert entered_value == query, \
            f"Текст '{query}' не ввелся. В поле: '{entered_value}'"

        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=f"after_entering_{query}",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Нажать на кнопку 'Поиск' (иконка лупы)")
    def click_search_button(self):
        """Кликает по кнопке поиска."""
        search_button = self.wait.until(EC.element_to_be_clickable
                                        (self._search_button_locator))
        (self.driver.execute_script
         ("arguments[0].scrollIntoView(true);", search_button))
        search_button.click()

        allure.attach(
            self.driver.get_screenshot_as_png(),
            name="after_clicking_search",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Выполнить поиск по запросу: '{query}'")
    def perform_search(self, query: str):
        """Выполняет поиск и ждет загрузки результатов."""
        self.enter_search_query(query)
        self.click_search_button()

        # Ждем появления карточек товаров или сообщения об ошибке
        self._wait_for_search_results()

        return self

    def _wait_for_search_results(self, timeout: int = 15):
        """Ожидает загрузки результатов поиска."""
        try:
            # Ждем появления хотя бы одного из признаков загрузки результатов
            WebDriverWait(self.driver, timeout).until(
                EC.any_of(
                    EC.presence_of_element_located(self._product_card_locator),
                    EC.presence_of_element_located
                    (self._product_title_locator),
                    EC.presence_of_element_located
                    (self._pagination_locator),
                    EC.presence_of_element_located
                    (self._results_count_locator),
                    EC.presence_of_element_located
                    (self._no_results_message_locator)
                )
            )
        except TimeoutException:
            # Если ничего не появилось, делаем скриншот для диагностики
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="timeout_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(
                self.driver.page_source[:10000],
                name="timeout_page_source",
                attachment_type=allure.attachment_type.HTML
            )
            print("ВНИМАНИЕ: Таймаут при ожидании результатов поиска")

    @allure.step("Получить названия книг из результатов поиска")
    def get_product_titles(self) -> list[str]:
        """
        Собирает и возвращает список названий книг из выдачи.
        Использует актуальный локатор a.product-card__title
        """
        titles = []

        # Пробуем основной локатор
        try:
            # Ждем появления хотя бы одной ссылки с названием книги
            self.wait.until(EC.presence_of_element_located
                            (self._product_title_locator))
            title_elements = (self.driver.find_elements
                              (*self._product_title_locator))

            for element in title_elements:
                title_text = element.text.strip()
                if title_text:  # Добавляем только непустые названия
                    titles.append(title_text)

            allure.attach(
                f"Найдено элементов по основному локатору: "
                f"{len(title_elements)}",
                name="main_locator_count",
                attachment_type=allure.attachment_type.TEXT
            )

        except TimeoutException:
            allure.attach(
                "Основной локатор не сработал, пробуем альтернативный",
                name="main_locator_status",
                attachment_type=allure.attachment_type.TEXT
            )

            # Пробуем альтернативный локатор
            try:
                title_elements = (self.driver.find_elements
                                  (*self._product_title_alt_locator))
                for element in title_elements:
                    title_text = element.text.strip()
                    if title_text:
                        titles.append(title_text)

                allure.attach(
                    f"Найдено элементов по альтернативному локатору: "
                    f"{len(title_elements)}",
                    name="alt_locator_count",
                    attachment_type=allure.attachment_type.TEXT
                )
            except:
                pass

        # Если все еще нет результатов, ищем любые ссылки,
        # которые могут быть названиями книг
        if not titles:
            try:
                # Ищем все ссылки с путем /product/
                product_links = (self.driver.find_elements
                                 (By.CSS_SELECTOR,
                                  "a[href*='/product/']"))
                for link in product_links:
                    link_text = link.text.strip()
                    if link_text and len(link_text) > 3:
                        titles.append(link_text)

                allure.attach(
                    f"Найдено ссылок на товары: {len(product_links)}",
                    name="product_links_count",
                    attachment_type=allure.attachment_type.TEXT
                )
            except:
                pass

        # Сохраняем результат в отчет
        allure.attach(
            str(titles),
            name="found_titles",
            attachment_type=allure.attachment_type.TEXT
        )

        # Делаем скриншот результатов
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name="search_results_screenshot",
            attachment_type=allure.attachment_type.PNG
        )

        return titles

    @allure.step("Получить информацию об авторе из названия книги")
    def extract_author_from_title(self, title_text: str) -> str:
        """
        Извлекает имя автора из полного названия книги.
        В предоставленном HTML автор указан в атрибуте title ссылки.
        """
        try:
            # Ищем элемент с таким текстом названия
            elements = self.driver.find_elements(By.XPATH,
                f"//a[@class='product-card__title' and contains(text(), "
                f"'{title_text[:20]}')]")
            if elements:
                full_title = elements[0].get_attribute("title")
                if full_title and "(" in full_title and ")" in full_title:
                    # Извлекаем текст в скобках (обычно там автор)
                    import re
                    author_match = re.search(r'\((.*?)\)', full_title)
                    if author_match:
                        return author_match.group(1)
            return ""
        except:
            return ""

    @allure.step("Проверить наличие результатов поиска")
    def has_search_results(self) -> bool:
        """Проверяет, есть ли результаты поиска."""
        try:
            # Проверяем наличие карточек товаров или ссылок на товары
            cards = self.driver.find_elements(*self._product_card_locator)
            titles = self.driver.find_elements(*self._product_title_locator)
            links = self.driver.find_elements(By.CSS_SELECTOR,
                                              "a[href*='/product/']")

            has_results = len(cards) > 0 or len(titles) > 0 or len(links) > 0

            allure.attach(
                f"Карточки товаров: {len(cards)}, "
                f"Названия: {len(titles)}, "
                f"Ссылки: {len(links)}",
                name="results_check",
                attachment_type=allure.attachment_type.TEXT
            )

            return has_results

        except:
            return False

    @allure.step("Проверить наличие сообщения об отсутствии результатов")
    def is_no_results_message_displayed(self) -> bool:
        """Проверяет, отображается ли сообщение 'Ничего не найдено'."""
        try:
            message = (self.driver.find_element
                       (*self._no_results_message_locator))
            return message.is_displayed()
        except:
            return False

    @allure.step("Получить текущий URL")
    def get_current_url(self) -> str:
        """Возвращает текущий URL страницы."""
        return self.driver.current_url

    @allure.step("Проверить значение в поле поиска")
    def get_search_input_value(self) -> str:
        """Возвращает текущее значение в поле поиска."""
        search_input = (self.wait.until
                    (EC.presence_of_element_located
                     (self._search_input_locator)))
        return search_input.get_attribute("value")
