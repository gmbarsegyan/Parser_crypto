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

us_ag = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows; Windows NT 10.0; WOW64; en-US Trident/6.0)", "Mozilla/5.0 (Windows; Windows NT 10.0; x64) AppleWebKit/534.19 (KHTML, like Gecko) Chrome/50.0.2000.270 Safari/602", "Mozilla/5.0 (compatible; MSIE 9.0; Windows; Windows NT 6.1; WOW64; en-US Trident/5.0)", "Mozilla/5.0 (compatible; MSIE 9.0; Windows; Windows NT 10.3; x64; en-US Trident/5.0)", "Mozilla/5.0 (Windows; U; Windows NT 6.3; WOW64) AppleWebKit/534.41 (KHTML, like Gecko) Chrome/51.0.1755.323 Safari/534", "Mozilla/5.0 (Windows; U; Windows NT 6.0; x64) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/47.0.3902.150 Safari/534", "Mozilla/5.0 (compatible; MSIE 10.0; Windows; Windows NT 10.0; WOW64; en-US Trident/6.0)", "Mozilla/5.0 (Windows; U; Windows NT 10.2; Win64; x64; en-US) AppleWebKit/602.47 (KHTML, like Gecko) Chrome/48.0.3348.223 Safari/600", "Mozilla/5.0 (Windows; U; Windows NT 10.0;) AppleWebKit/535.13 (KHTML, like Gecko) Chrome/51.0.1383.284 Safari/601.8 Edge/8.80773", "Mozilla/5.0 (Windows NT 10.1; Win64; x64; en-US) AppleWebKit/602.40 (KHTML, like Gecko) Chrome/47.0.3126.111 Safari/600.4 Edge/12.86331"]

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')  # выключаю webserver mode(чтобы был как обычный комп)
options.add_argument(f"user-agent=Mozilla/5.0 (Windows; Windows NT 10.0; x64) AppleWebKit/534.19 (KHTML, like Gecko) Chrome/50.0.2000.270 Safari/602") # {random.choice(us_ag)}
# options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("window-size=1900,1080")
options.add_argument(f"--proxy-server=194.26.207.51:8000")

list_to_str = lambda x: ', '.join(x)
to_int_without_comma_h = lambda number: float(number.translate({ord(','): None}))

rand1 = [1, 1.23, 1.36, 1.45, 1.12, 1.27]
rand2 = [2, 2.14, 2.19, 2.76, 2.31, 2.27, 2.11, 2.26, 2.18, 2.09, 2.04]
rand3 = [3, 3.14, 3.19, 3.76, 3.31, 3.27]

def sell_buy_button_h(button, currency = "usdt"): # Нажимает на кнопку покупки или продажи
    if button == 'buy':
        driver.find_element(By.XPATH, f'//a[contains(@href, "buy-{currency}-rub")]').click()
    else:
        driver.find_element(By.XPATH, f'//a[contains(@href, "sell-{currency}-rub")]').click()

def get_data_huobi(driver, vremya, mode = 'Покупка'): # Собирает данные о пользователях

    traders_names = driver.find_elements(By.XPATH, f'//h3[contains(@class, "font14")]')
    if not traders_names:
        time.sleep(0.7)
        traders_names = driver.find_elements(By.XPATH, f'//h3[contains(@class, "font14")]')
        if not traders_names:
            if mode == 'Покупка':
                with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                    pd.DataFrame(['нет данных']).to_excel(writer, sheet_name='Sheet_3', index=False, header=False,
                                                          startrow=writer.sheets[
                                                              'Sheet_3'].max_row if 'Sheet_3' in writer.sheets else 0)
            else:
                with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                    pd.DataFrame(['нет данных']).to_excel(writer, sheet_name='Sheet_4', index=False, header=False,
                                                          startrow=writer.sheets[
                                                              'Sheet_4'].max_row if 'Sheet_4' in writer.sheets else 0)
            return None

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "otc-trade-list")]')))  #######
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//div[contains(@class, "price")]')))  #########
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//h3[contains(@class, "font14")]')))  ##########
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//h3[contains(@class, "font14")]')))  ##########

    traders_names = [trader.text for trader in traders_names]
    buy_prices = [float(price.text.split()[0].replace(',', '')) for price in
                  driver.find_elements(By.XPATH, f'//div[contains(@class, "price")]')]  # Курс
    limits = np.array([list(map(float, map(to_int_without_comma_h, limit.text.split()[0].split('-')))) for limit in
                       driver.find_elements(By.CLASS_NAME, "limit")])
    volume = [float(vol.text.split()[0]) for vol in driver.find_elements(By.CLASS_NAME, "stock")]

    traders_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "otc-trade-list")]')
    paying_systems = []
    for trader_element in traders_elements:
        banks_elements = trader_element.find_elements(By.CLASS_NAME, "new-block")
        banks_list = [bank_element.text for bank_element in banks_elements]
        paying_systems.append(banks_list)

    paying_systems = list(map(list_to_str, paying_systems))

    df = pd.DataFrame({'Имя трейдера': traders_names,
                       'Курс': buy_prices,
                       'Объём': volume,
                       'Нижний лимит': limits[:, 0],
                       'Верхний лимит': limits[:, 1],
                       'Платежные системы': paying_systems})
    df['Время парсинга'] = vremya
    df.loc[len(df)] = ['-' for _ in range(len(df.columns))]

    if mode == 'Покупка':
        with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet_3', index=False, header=False,
                        startrow=writer.sheets['Sheet_3'].max_row if 'Sheet_3' in writer.sheets else 0)
    else:
        with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet_4', index=False, header=False,
                        startrow=writer.sheets['Sheet_4'].max_row if 'Sheet_4' in writer.sheets else 0)
    return df

def choose_bank_h(mode, new_bank, currency): # Если сброшены настройки платежных систем, то выбирает нужный нам банк
    # Клик на список банков
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway
    time.sleep(random.choice([0.54, 0.68, 0.62, 0.45]))
    # Находим нужный нам банк и кликаем на него
    new_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{new_bank}")]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)
    ActionChains(driver).move_to_element(new_bank_button).click().perform()
    time.sleep(random.choice([0.54, 0.68, 0.62, 0.45]))
    driver.execute_script("window.scrollTo(0, 0);")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway подтверждаем
    time.sleep(random.choice(rand2))
    if mode == 'Продажа_Покупка': # Сначала записываем продажу, потом покупку
        get_data_huobi(driver, vremya, mode='Продажа')

        # Продажа новый банк
        sell_buy_button_h('buy', currency)
        time.sleep(random.choice(rand2))
        get_data_huobi(driver, vremya, mode='Покупка')
    else: # Наоборот
        get_data_huobi(driver, vremya, mode='Покупка')
        # Продажа новый банк
        sell_buy_button_h('sell', currency)
        time.sleep(random.choice(rand2))
        get_data_huobi(driver, vremya, mode='Продажа')

def change_bank_h(mode, old_bank, new_bank, currency): # Убирает метку со старого банка, чтобы перейти на новый банк
    # Клик на список банков
    # time.sleep(random.choice(rand1))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway
    time.sleep(random.choice([0.6, 0.7])) #####
    # клик на старый банк
    old_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{old_bank}")]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", old_bank_button)
    ActionChains(driver).move_to_element(old_bank_button).click().perform()
    time.sleep(random.choice(rand1))  ##### 2
    # клик на новый банк
    new_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{new_bank}")]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", new_bank_button)
    ActionChains(driver).move_to_element(new_bank_button).click().perform()

    driver.execute_script("window.scrollTo(0, 0);")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway подтверждаем
    time.sleep(random.choice(rand2))
    if mode == 'Продажа_Покупка':
        get_data_huobi(driver, vremya, mode='Продажа')

        # Покупка новый банк
        sell_buy_button_h('buy', currency)
        time.sleep(random.choice(rand3))
        get_data_huobi(driver, vremya, mode='Покупка')
    else:
        get_data_huobi(driver, vremya, mode='Покупка')

        # Продажа новый банк
        sell_buy_button_h('sell', currency)
        time.sleep(random.choice(rand3))
        get_data_huobi(driver, vremya, mode='Продажа')

def get_data_huobi_1_currency(currency):
    time.sleep(random.choice(rand2))
    # PAYEER
    choose_bank_h(mode='Покупка_Продажа', new_bank="RNCB", currency=currency)
    # Райффайзен
    change_bank_h(mode='Продажа_Покупка', old_bank="PAYEER", new_bank="Raiffeisenbank", currency=currency)
    # Хоум
    change_bank_h(mode='Покупка_Продажа', old_bank="Raiffeisenbank", new_bank="Home Credit Bank (Russia)", currency=currency)
    # Альфа
    change_bank_h(mode='Продажа_Покупка', old_bank="Home Credit Bank (Russia)", new_bank="Alfa-bank", currency=currency)
    # Сбер
    # time.sleep(random.choice(rand2))
    change_bank_h(mode='Покупка_Продажа', old_bank="Alfa-bank", new_bank="Sberbank", currency=currency)
    # time.sleep(random.choice(rand2))
    # Тинькофф
    change_bank_h(mode='Продажа_Покупка', old_bank="Sberbank", new_bank="Tinkoff", currency=currency)
    # Сбрасываем, возвращаем к исходному состоянию
    time.sleep(random.choice(rand1))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway
    time.sleep(random.choice(rand1))  #####
    # клик на старый банк
    old_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "Tinkoff")]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", old_bank_button)
    ActionChains(driver).move_to_element(old_bank_button).pause(1).click().perform()
    time.sleep(random.choice(rand1))  #####
    driver.execute_script("window.scrollTo(0, 0);")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway подтверждаем
    time.sleep(random.choice(rand1))


def data_huobi():
    time.sleep(random.choice(rand1))
    get_data_huobi_1_currency(currency="usdt")
    time.sleep(random.choice(rand1))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "re-left") and .//span[text()="USDT"]]'))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="currency-text" and normalize-space()="BTC"]'))).click()
    get_data_huobi_1_currency(currency="btc")
    time.sleep(random.choice(rand3))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "re-left") and .//span[text()="BTC"]]'))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="currency-text" and normalize-space()="ETH"]'))).click()
    get_data_huobi_1_currency(currency="eth")
    time.sleep(random.choice(rand3))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "re-left") and .//span[text()="ETH"]]'))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="currency-text" and normalize-space()="USDT"]'))).click()
    time.sleep(random.choice([3.64, 4.12, 5.16, 6.21]))

vremya = time.strftime("%H:%M:%S", time.localtime())  # берем время
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

driver.get(url='https://www.htx.com/en-us/fiat-crypto/trade/buy-usdt-rub')
time.sleep(3.124)
video_close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//i[contains(@class, "video-close")]'))).click()


data_huobi()