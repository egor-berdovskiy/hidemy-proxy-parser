from selenium import webdriver
from selenium.webdriver.common.by import By

from datetime import datetime

import pandas as pd

from bs4 import BeautifulSoup

from loguru import logger

from typing import Optional

from uuid import uuid4

import os


class Printer:
    proxy_count: str
    save_dir: str
    file_marker: str

    def __init__(
            self,
            proxy_count: str = 'all',
            save_dir: str = './output/',
            file_marker: str = 'date',
    ) -> None:
        self.proxy_count = proxy_count if proxy_count == 'all' else int(proxy_count)
        self.save_dir = save_dir
        self.file_marker = file_marker

        self.file_name = f'output-{str(datetime.today()).split(" ")[0]}' if file_marker == 'date' else f'output-{str(uuid4().hex)[:12]}'

        self.check_dir()

    def check_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
            logger.info(f'[i] Создал папку для вывода {self.save_dir}')
        else:
            logger.info(f'[i] Результаты будут тут {self.save_dir}')


    def to_excel(self, table_data: list):
        df = pd.DataFrame(table_data, columns=["IP Address", "Port", "Country", "Response Time", "Protocol", "Encrypted", "Uptime"])
        df = df.head(self.proxy_count) if isinstance(self.proxy_count, int) else df
        file_name = f'{self.file_name}.xlsx'
        try:
            df.to_excel(self.save_dir + file_name, index=False)
            logger.info(f'[✨] Файл {file_name} сформирован.')
        except Exception as ex:
            logger.error(str(ex))

    def to_txt(self, table_data: list):
        file_name = f'{self.file_name}.txt'
        table_data = table_data[:self.proxy_count] if isinstance(self.proxy_count, int) else table_data

        with open(self.save_dir + file_name, 'w') as file:
            for row in table_data:
                complete_proxy = f'{str.lower(row[4])}://{row[0]}:{row[1]}\n'
                file.write(complete_proxy)
        logger.info(f'[⚙] Файл {file_name} сформирован.')


class Parser:
    options = webdriver.FirefoxOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

    driver = webdriver.Firefox(options=options)

    # Storage
    tables = []  # raw table data
    table_data = []  # ip, port, country, ping, protocol, uptime

    def __init__(
            self,
            url: str,
            ports: str,
            max_time: str,
            type: str,
            countries: str,
            proxy_count: str = 'all',
            save_dir: str = '/output',
            file_marker: str = 'date',
    ) -> None:
        self.url = url
        self.params = f'/?country={countries}&maxtime={max_time}&ports={ports}&type={type}#list'
        self.url_complete = self.url + self.params

        self.printer = Printer(proxy_count, save_dir, file_marker)

        self.result = []


    def wait_user(self, hint: Optional[bool] = False):
        response = input(f'{"для продолжения введи y" if hint else ""}: ')
        if response != 'y':
            self.wait_user()

    def proccess_page(self, current_page):
        tbody = self.driver.find_element(By.TAG_NAME, 'tbody')
        self.tables.append(tbody.get_attribute('outerHTML'))
        logger.info(
            f'[!] Жми на {current_page+1} страницу, как перейдешь, введи y')
        self.wait_user()

    def proccess_table(self):
        for table in self.tables:
            soup = BeautifulSoup(table, 'html.parser')
            tbody = soup.find('tbody')
            rows = tbody.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                row_values = [cell.get_text(strip=True) for cell in cells]
                self.table_data.append(row_values)
        self.printer.to_excel(self.table_data)
        self.printer.to_txt(self.table_data)

    

    def run(self):
        self.driver.get(self.url_complete)
        logger.info('[!] Как только капча будет решена, введи: y')
        self.wait_user()

        logger.info('[?] Введи количество страниц')
        pages = int(input(': '))
        for page in range(pages):
            self.proccess_page(page)

        self.driver.close()
        self.proccess_table()
        logger.info('[👌] Работа окончена.')

