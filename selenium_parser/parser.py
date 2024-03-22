from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from datetime import datetime

import pandas as pd

from bs4 import BeautifulSoup

from loguru import logger

from typing import Optional

from uuid import uuid4

import time

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
            logger.info(f'[i] Created a folder for the output files {self.save_dir}')
        else:
            logger.info(f'[i] The results will be here {self.save_dir}')


    def to_excel(self, table_data: list):
        df = pd.DataFrame(table_data, columns=["IP Address", "Port", "Country", "Response Time", "Protocol", "Encrypted", "Uptime"])
        df = df.head(self.proxy_count) if isinstance(self.proxy_count, int) else df
        file_name = f'{self.file_name}.xlsx'
        try:
            df.to_excel(self.save_dir + file_name, index=False)
            logger.info(f'[✨] The {file_name} file was created.')
        except Exception as ex:
            logger.error(str(ex))

    def to_txt(self, table_data: list):
        file_name = f'{self.file_name}.txt'
        table_data = table_data[:self.proxy_count] if isinstance(self.proxy_count, int) else table_data

        with open(self.save_dir + file_name, 'w') as file:
            for row in table_data:
                complete_proxy = f'{str.lower(row[4])}://{row[0]}:{row[1]}\n'
                file.write(complete_proxy)
        logger.info(f'[⚙] The {file_name} file was created.')


class Parser:
    # Random user agent
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value] 
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    user_agent = user_agent_rotator.get_random_user_agent()

    # Driver
    options = webdriver.FirefoxOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument(f"--disable-blink-features=AutomationControlled")

    driver = webdriver.Firefox(options=options)

    # Storage
    tables = []  # raw table data
    table_data = []  # ip, port, country, ping, protocol, uptime

    # Options
    silent_mode: bool
    next_page_delay: float

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
            silent_mode: bool = False,
            next_page_delay: float = 5,
    ) -> None:
        self.url = url
        self.params = f'/?country={countries}&maxtime={max_time}&ports={ports}&type={type}#list'
        self.url_complete = self.url + self.params

        self.silent_mode = silent_mode
        self.next_page_delay = next_page_delay

        self.printer = Printer(proxy_count, save_dir, file_marker)

        self.result = []


    def wait_user(self, hint: Optional[bool] = False):
        response = input(f'{"To continue, type y" if hint else ""}: ')
        if response != 'y':
            self.wait_user()

    
    def get_max_page(self, last_page: int):
        answer = input('[run/max_page]: ')
        if answer == 'run':
            return int(last_page)
        else:
            return int(answer)
            


    def goto_next_page(self):
        pagination = self.driver.find_element(By.CLASS_NAME, 'pagination')
        try:
            next_page_btn = pagination.find_element(By.CLASS_NAME, 'next_array')
            next_page_btn.click()
            logger.info(f'[i] Wait {self.next_page_delay} sec')
            time.sleep(self.next_page_delay)
        except NoSuchElementException as ex:
            logger.info('[!] All pages done.')
        except Exception as ex:
            logger.error(ex)
        
        

    def proccess_page(self, current_page):
        tbody = self.driver.find_element(By.TAG_NAME, 'tbody')
        self.tables.append(tbody.get_attribute('outerHTML'))
        self.goto_next_page()

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
        logger.info('[!] Once the captcha is solved, type: y')
        self.wait_user()

        last_page = int(self.driver.find_element(By.CLASS_NAME, 'pagination').text.split('\n')[-1])

        time_start = time.time()
        if self.silent_mode:
            logger.info(f'[i] Last page: {last_page}.')
            for i, page in enumerate(range(last_page)):
                self.proccess_page(page)
                logger.info(f'[{i+1}/{last_page}] Done.')
        else:
            logger.info(f'[i] Last page: {last_page}, run or enter max page?')
            logger.info(f'[i] To skip this dialog, enable silent mode in the settings.')
            answer = self.get_max_page(last_page)

        self.driver.close()
        self.proccess_table()

        logger.info(f"[👌] The job's over. {(time.time() - time_start):.1f} sec.")
