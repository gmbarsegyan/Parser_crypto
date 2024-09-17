import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np

options = Options()

us_ag = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows; Windows NT 10.0; WOW64; en-US Trident/6.0)", "Mozilla/5.0 (Windows; Windows NT 10.0; x64) AppleWebKit/534.19 (KHTML, like Gecko) Chrome/50.0.2000.270 Safari/602", "Mozilla/5.0 (compatible; MSIE 9.0; Windows; Windows NT 6.1; WOW64; en-US Trident/5.0)", "Mozilla/5.0 (compatible; MSIE 9.0; Windows; Windows NT 10.3; x64; en-US Trident/5.0)", "Mozilla/5.0 (Windows; U; Windows NT 6.3; WOW64) AppleWebKit/534.41 (KHTML, like Gecko) Chrome/51.0.1755.323 Safari/534", "Mozilla/5.0 (Windows; U; Windows NT 6.0; x64) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/47.0.3902.150 Safari/534", "Mozilla/5.0 (compatible; MSIE 10.0; Windows; Windows NT 10.0; WOW64; en-US Trident/6.0)", "Mozilla/5.0 (Windows; U; Windows NT 10.2; Win64; x64; en-US) AppleWebKit/602.47 (KHTML, like Gecko) Chrome/48.0.3348.223 Safari/600", "Mozilla/5.0 (Windows; U; Windows NT 10.0;) AppleWebKit/535.13 (KHTML, like Gecko) Chrome/51.0.1383.284 Safari/601.8 Edge/8.80773", "Mozilla/5.0 (Windows NT 10.1; Win64; x64; en-US) AppleWebKit/602.40 (KHTML, like Gecko) Chrome/47.0.3126.111 Safari/600.4 Edge/12.86331"]
options.add_argument('--disable-blink-features=AutomationControlled')  # выключаю webserver mode(чтобы был как обычный комп)
options.add_argument(f"user-agent={random.choice(us_ag)}")
# options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("window-size=1900,1080")
# options.add_argument(f"--proxy-server=194.26.207.51:8000")

to_int_without_comma_by = lambda spisok: [float(limit.translate({ord(','): None})) for limit in spisok]
list_to_str = lambda x: ', '.join(x)

rand1 = [1, 1.23, 1.36, 1.45, 1.12, 1.27]
rand2 = [2, 2.14, 2.19, 2.76, 2.31, 2.27]
rand3 = [3, 3.14, 3.19, 3.76, 3.31, 3.27]

def get_data_bitget(driver, vremya, mode = 'Покупка'):
    traders_names = driver.find_elements(By.XPATH, '//a[@class="list-item__nickname"]')
    if not traders_names:
        time.sleep(0.7)
        traders_names = driver.find_elements(By.XPATH, '//a[@class="list-item__nickname"]')
        if not traders_names:
            if mode == 'Покупка':
                with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                    pd.DataFrame(['нет данных']).to_excel(writer, sheet_name='Sheet_5', index=False, header=False,
                                                          startrow=writer.sheets[
                                                              'Sheet_5'].max_row if 'Sheet_5' in writer.sheets else 0)
            else:
                with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                    pd.DataFrame(['нет данных']).to_excel(writer, sheet_name='Sheet_6', index=False, header=False,
                                                          startrow=writer.sheets[
                                                              'Sheet_6'].max_row if 'Sheet_6' in writer.sheets else 0)
            return None

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'hall-list-item-wrap.hall-list')))  #######
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="price-shower"]')))  #########
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="list-item__nickname"]')))  ##########

    traders_names = [trader.text.strip() for trader in traders_names][::2]
    price_elements = driver.find_elements(By.XPATH, '//span[@class="price-shower"]')
    buy_prices = [float(price_element.text.replace(',', '').strip().split()[0]) for index, price_element in enumerate(price_elements) if index % 2 == 0]  # Курс  и float

    lst = [quantity.text for quantity in driver.find_elements(By.XPATH, '//div[contains(@class, "list_limit")]/span[2]//span') if quantity.text.strip()]  # [::2]  # '218.4927 USDT', '10,500.00 ~ 19,860.98 RUB', '5,355.3127 USDT', '30,000.00 ~ 100,000.01 RUB', '2,058.9948 USDT'

    limits = np.array([lim.split()[0].split("–") for lim in lst[1::2]])  # Лимиты

    limits = np.array([to_int_without_comma_by(elements) for elements in limits])
    volume = list(map(float, [vol.translate({ord(','): None}) for vol in [lim.split()[0] for lim in lst[::2]]]))
    traders_elements = driver.find_elements(By.CLASS_NAME, 'hall-list-item-wrap.hall-list')

    paying_systems = []
    for trader_element in traders_elements:
        bank_elements = trader_element.find_elements(By.XPATH, './/div[contains(@class, "list-item-payment list-payment")]/span/span/img')
        banks_list = [bank_element.get_attribute('alt') for bank_element in bank_elements]
        paying_systems.append(banks_list)

    paying_systems = list(map(list_to_str, paying_systems))
    df = pd.DataFrame({'Имя трейдера': traders_names,
                       'Курс': buy_prices,
                       'Объём': volume,
                       'Нижний лимит': list(limits[:, 0]),
                       'Верхний лимит': list(limits[:, 1]),
                       'Платежные системы': paying_systems})
    df['Время парсинга'] = vremya
    df.loc[len(df)] = ['-' for _ in range(len(df.columns))]

    if mode == 'Покупка':
        with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet_5', index=False, header=False,
                        startrow=writer.sheets['Sheet_5'].max_row if 'Sheet_5' in writer.sheets else 0)
    else:
        with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet_6', index=False, header=False,
                        startrow=writer.sheets['Sheet_6'].max_row if 'Sheet_6' in writer.sheets else 0)
    return df

def choose_bank_bi(mode, new_bank):
    # payway click
    payway_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//dl[contains(@class, "ml-8px")]//span[contains(@class, "bit-input__suffix")]')))
    payway_dropdown.click()
    time.sleep(random.choice([0.5, 0.48, 0.54, 0.52, 0.56]))

    # Execute JavaScript to scroll to Payeer
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f'//li[contains(., "{new_bank}")]'))))

    # Choose Payeer
    payeer_option = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//li[contains(., "{new_bank}")]')))
    payeer_option.click()

    time.sleep(random.choice(rand2))
    if mode == "Покупка-Продажа":
        get_data_bitget(driver, vremya, mode='Покупка')
        # Продажа новый банк
        sell_buy_button_bi('sell')
        time.sleep(random.choice(rand2))
        get_data_bitget(driver, vremya, mode='Продажа')
    else:
        get_data_bitget(driver, vremya, mode='Продажа')

        # Продажа новый банк
        sell_buy_button_bi('buy')
        time.sleep(random.choice(rand2))
        get_data_bitget(driver, vremya, mode='Покупка')

def sell_buy_button_bi(button):
    if button == 'buy':
        driver.find_element(By.XPATH, '//span[contains(text(), "Покупка")]').click()
    else:
        driver.find_element(By.XPATH, '//span[contains(text(), "Продажа")]').click()

def get_data_1_currency_bi():
    time.sleep(random.choice(rand2))
    # Райффайзен
    choose_bank_bi(mode = "Покупка-Продажа", new_bank="Райффайзен")
    # PAYEER
    choose_bank_bi(mode = "Продажа-Покупка", new_bank="Payeer")
    # Хоум
    choose_bank_bi(mode = "Покупка-Продажа", new_bank="Хоум Кредит Банк")
    # Альфа
    choose_bank_bi(mode = "Продажа-Покупка", new_bank="Альфа-Банк")
    # Сбер
    choose_bank_bi(mode = "Покупка-Продажа", new_bank="Local Card-Green")
    # Тинькофф
    choose_bank_bi(mode = "Продажа-Покупка", new_bank="Local Card-Yellow")

def data_bitget():
    time.sleep(1)
    get_data_1_currency_bi()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="bit-input__suffix"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "BTC")]'))).click()
    get_data_1_currency_bi()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="bit-input__suffix"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "ETH")]'))).click()
    get_data_1_currency_bi()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="bit-input__suffix"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "USDT")]'))).click()
    time.sleep(random.choice([3, 4.23, 4.41, 5.21, 6.12]))

vremya = time.strftime("%H:%M:%S", time.localtime())  # берем время
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

driver.get(url='https://www.bitget.com/ru/p2p-trade?fiatName=RUB')
time.sleep(3)
close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//i[contains(@class, "bit-dialog__close bit-icon bit-icon-close")]'))).click()

data_bitget()