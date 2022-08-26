import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import json

url = 'https://krasnodar.zoon.ru/trainings/?search_query_form=1&m%5B5200e522a0f302f066000061%5D=1&center%5B%5D=45.02387700001942&center%5B%5D=38.97015699999998&zoom=12'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'
}


# <----------- Получаем html всей страницы. Используем ActionChains, чтобы прокрутить страницу до конца.
def get_html(url):
    driver = webdriver.Firefox()
    driver.maximize_window()
    try:
        driver.get(url=url)
        time.sleep(3)
        while True:
            find_catalog_button = driver.find_element(
                By.CLASS_NAME, 'catalog-button-showMore')
            if driver.find_elements(By. CLASS_NAME, 'hasmore-text'):
                with open('source-page.html', 'w', encoding="utf-8") as file:
                    file.write(driver.page_source)
                break
            else:
                actions = ActionChains(driver)
                actions.move_to_element(find_catalog_button).perform()
                time.sleep(3)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


# <----------- Получаем и записываем ссылки в текстовый файл
def get_items_urls(file_path):
    with open(file_path, encoding="utf-8") as file:
        src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        items_divs = soup.find_all('div', class_='minicard-item__info')
        urls_organizations = []

        for item in items_divs:
            item_url = item.find(
                'h2', class_='minicard-item__title').find('a').get('href')
            urls_organizations.append(item_url)
        with open('link.txt', 'w', encoding="utf-8") as file:
            for url in urls_organizations:
                file.write(f'{url}\n')
        return 'all done'


def get_data(file_path):     # <----------- Переходим по ссылкам и извлекаем нужную информацию
    with open(file_path) as file:

        # uril_list = file.readlines()
        # clear_urls = []
        # for url in uril_list:
        #     url = url.strip()
        #     clear_urls.append(url)
        # print(clear_urls)

        # Вместо цикла используем comprehensions для читабильности
        url_list = [url.strip() for url in file.readlines()]
        results = []
        for url in url_list:
            response = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')

            try:      # <----------- Получаем название
                org_name = soup.find('span', {'itemprop': 'name'}).text.strip()
            except:
                org_name = None

            phones = []
            try:    # <----------- Получаем телефоны. Их может быть несколько, поэтому создаём список
                org_phone = soup.find(
                    'div', class_='service-phones-list').find_all('a', class_='js-phone-number')
                for phone in org_phone:
                    org_phone = phone.get('href').split(':')[-1].strip()
                    phones.append(org_phone)
            except:
                org_phone = None

            try:     # <----------- Получаем адреса
                org_address = soup.find(
                    'address', {'itemprop': 'address'}).text
            except:
                org_address = None

            results.append(        # <----------- Добавлением результат в лист и записываем всё это в json
                {
                    'название': org_name,
                    'телефон': org_phone,
                    'адрес': org_address
                }
            )

        with open('parsed_date.json', 'w', encoding="utf-8") as file:
            json.dump(results, file, indent=4, ensure_ascii=False)
        return 'all done'


def main():
    # get_html(url=url)
    # print(get_items_urls(file_path='C:/Users/79384/Desktop/zoon/source-page.html'))
    get_data(file_path='C:/Users/79384/Desktop/zoon/link.txt')


if __name__ == '__main__':
    main()
