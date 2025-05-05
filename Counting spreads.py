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
import pandas as pd
import numpy as np
import random

us_ag = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows; Windows NT 10.0; WOW64; en-US Trident/6.0)", "Mozilla/5.0 (Windows; Windows NT 10.0; x64) AppleWebKit/534.19 (KHTML, like Gecko) Chrome/50.0.2000.270 Safari/602", "Mozilla/5.0 (compatible; MSIE 9.0; Windows; Windows NT 6.1; WOW64; en-US Trident/5.0)", "Mozilla/5.0 (compatible; MSIE 9.0; Windows; Windows NT 10.3; x64; en-US Trident/5.0)", "Mozilla/5.0 (Windows; U; Windows NT 6.3; WOW64) AppleWebKit/534.41 (KHTML, like Gecko) Chrome/51.0.1755.323 Safari/534", "Mozilla/5.0 (Windows; U; Windows NT 6.0; x64) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/47.0.3902.150 Safari/534", "Mozilla/5.0 (compatible; MSIE 10.0; Windows; Windows NT 10.0; WOW64; en-US Trident/6.0)", "Mozilla/5.0 (Windows; U; Windows NT 10.2; Win64; x64; en-US) AppleWebKit/602.47 (KHTML, like Gecko) Chrome/48.0.3348.223 Safari/600", "Mozilla/5.0 (Windows; U; Windows NT 10.0;) AppleWebKit/535.13 (KHTML, like Gecko) Chrome/51.0.1383.284 Safari/601.8 Edge/8.80773", "Mozilla/5.0 (Windows NT 10.1; Win64; x64; en-US) AppleWebKit/602.40 (KHTML, like Gecko) Chrome/47.0.3126.111 Safari/600.4 Edge/12.86331"]

options = Options()

options.add_argument('--disable-blink-features=AutomationControlled')  # выключаю webserver mode(чтобы был как обычный комп)
options.add_argument(f"user-agent={random.choice(us_ag)}")
# options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("window-size=1900,1080")
# ToDo. Вставьте свой адрес и порт прокси сервера, а также логин и пароль от аккаунта Bybit
adress = '185.166.199.8'
port = '8000'
login = 'login'
password = 'password'
options.add_argument(f"--proxy-server={adress}:{port}")

rand0 = [0.8, 0.67, 0.82, 0.73, 0.7, 0.69]
rand1 = [1, 1.23, 1.36, 1.45, 1.12, 1.27]
rand2 = [2, 2.14, 2.19, 2.76, 2.31, 2.27]
rand3 = [3, 3.14, 3.19, 3.76, 3.31, 3.27]
rand4 = [4.01, 4.03, 3.94, 3.82, 4.11, 4.12, 4.22, 4.2]

buy_data = pd.DataFrame(columns=[
    'p2p_exchange_rate', 'low_bound', 'high_bound', 'volume', 'bank', 'exchange', 'crypto'
])

sell_data = pd.DataFrame(columns=[
    'p2p_exchange_rate', 'low_bound', 'high_bound', 'volume', 'bank', 'exchange', 'crypto'
])

def close_extra_tabs(driver, new_bank):
    time.sleep(0.4)
    # Получаем текущую ссылку
    url = driver.current_url

    while url == 'https://www.bybit.com/trading/ru-RU/trade-portal?utm_source=header_trade_portal':
        # Возвращаемся назад
        driver.back()

        # Открываем список банков
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "paywayAnchorList")]'))).click()

        # Выбираем нужный банк
        new_bank_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{new_bank}"]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)
        ActionChains(driver).move_to_element(new_bank_button).click().perform()

        time.sleep(2)

        url = driver.current_url

        print("Вернулся назад")
def wait_forever_for_element(driver, by, value, check_interval=1):
    while True:
        try:
            element = WebDriverWait(driver, check_interval).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            time.sleep(check_interval)  # Пауза между попытками
to_int_without_comma_by = lambda limit: float(limit)
def get_data_bybit(driver, mode='Покупка', bank=None, crypto=None):
    traders_names = driver.find_elements(By.XPATH, '//div[contains(@class, "advertiser-name")]')
    if not traders_names:
        time.sleep(0.7)
        traders_names = driver.find_elements(By.XPATH, '//div[contains(@class, "advertiser-name")]')
        if not traders_names:
            return None

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//tr')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'price-amount')))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "advertiser-name")]')))

    buy_price = float(
        ''.join(driver.find_element(By.CLASS_NAME, 'price-amount').text.split()).rstrip("RUB").replace(',',
                                                                                                       '.'))  # Курс
    lst = [quantity.text for quantity in driver.find_elements(By.CLASS_NAME,
                                                              'ql-value')]  # '218.4927 USDT', '10,500.00 ~ 19,860.98 RUB', '5,355.3127 USDT', '30,000.00 ~ 100,000.01 RUB', '2,058.9948 USDT'
    limits = lst[1].replace(' ', '').replace(',', '.').rstrip(" RUB").split('~')  # Лимиты
    limits = [to_int_without_comma_by(elements) for elements in limits]
    volume = lst[0].split()[0]  # Объем
    volume = float(volume.replace(' ', '').replace(',', '.'))
    new_row = {
        'p2p_exchange_rate': buy_price,
        'low_bound': limits[0],
        'high_bound': limits[1],
        'volume': volume,
        'bank': bank,
        'exchange': 'Bybit',
        'crypto': crypto
    }

    global buy_data, sell_data
    if mode == 'Покупка':
        buy_data = pd.concat([buy_data, pd.DataFrame([new_row])], ignore_index=True)
    else:
        sell_data = pd.concat([sell_data, pd.DataFrame([new_row])], ignore_index=True)

    return
def autorization():
    # Дождемся появления кнопки "Подтвердить"
    confirm_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "ant-btn-primary") and contains(., "Подтвердить")]')))
    confirm_button.click()

    # Авторизация
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'header-login')))
    time.sleep(random.choice(rand3))
    login_button.click()

    email_window = driver.find_element(By.XPATH, f'//input[contains(@placeholder, "Эл. почта")]')
    email_window.send_keys(login)  # Вставьте свой логин

    password_window = driver.find_element(By.XPATH, f'//input[contains(@placeholder, "Пароль")]')
    time.sleep(random.choice(rand1))
    password_window.send_keys(password)  # Вставьте свой пароль

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, "index_cht-by-button__MhPzO")]')))
    time.sleep(random.choice(rand4))
    login_button.click()

    time.sleep(random.choice([15.45, 12.03, 11.88, 13.12])) # На капчу и ввод кода двухфакторной аутентификации для входа

    verification_code = driver.find_elements(By.XPATH, f'//input[contains(@class, "by-safety-verification")]')
    for box in verification_code:
        box.send_keys(input())
def sell_buy_button_by(button): # Нажимает на кнопку покупки или продажи
    if button == 'buy':
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "by-switch__item") and contains(., "Покупка")]'))).click()
    else:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "by-switch__item") and contains(., "Продажа")]'))).click()
def choose_bank_by(mode, new_bank, crypto, risk = False):
    # Открываем список банков
    payway_list = wait_forever_for_element(driver, By.ID, 'paywayAnchorList')
    payway_list.click()

    if new_bank == "А-Банк":
        payway_list = wait_forever_for_element(driver, By.ID, 'paywayAnchorList')
        payway_list.click()

    # Выбираем нужный банк
    new_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{new_bank}"]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)
    ActionChains(driver).move_to_element(new_bank_button).click().perform()

    close_extra_tabs(driver, new_bank)
    # Подтверждаем
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, "by-button btn-confirm")]'))).click()
    time.sleep(random.choice(rand2))
    if mode == "Покупка-Продажа":
        # Покупка
        get_data_bybit(driver, mode='Покупка', bank = new_bank, crypto=crypto)
        time.sleep(random.choice(rand0))
        sell_buy_button_by('sell')
        if risk:
            accept_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//button[@class="by-button by-dialog__btn by-button--contained by-button--xx-large by-button--brand"]'
                                            )))
            accept_button.click()
            # time.sleep(random.choice([6.09, 4.12, 4.18, 5.07]))  # Это время дается чтобы закрыть всплывающее окно, предупреждающее о рисках при совершении сделок на продажу
        # Продажа
        time.sleep(random.choice(rand1))

        get_data_bybit(driver, mode='Продажа', bank = new_bank, crypto=crypto)
    else:
        # Продажа
        get_data_bybit(driver, mode='Продажа', bank = new_bank, crypto=crypto)
        time.sleep(random.choice(rand0))
        # Покупка
        sell_buy_button_by('buy')
        if risk:
            time.sleep(random.choice([5.88, 5.96, 6.14, 6.12, 6.01, 5.76]))  # Это время дается чтобы закрыть всплывающее окно, предупреждающее о рисках при совершении сделок на продажу
            risk_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'by-button__content')))
            risk_button.click()
        time.sleep(random.choice(rand1))

        get_data_bybit(driver, mode='Покупка', bank = new_bank, crypto=crypto)
def change_bank_by(mode, old_bank, new_bank, crypto):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "paywayAnchorList")]'))).click()

    time.sleep(random.choice([0.8, 0.67, 0.82, 0.73, 0.7, 0.69]))
    # Убираем старый банк
    old_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{old_bank}"]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", old_bank_button)
    ActionChains(driver).move_to_element(old_bank_button).click().perform()

    # Выбираем новый банк
    new_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{new_bank}"]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", new_bank_button)
    ActionChains(driver).move_to_element(new_bank_button).click().perform()
    driver.execute_script("window.scrollTo(0, 0);")
    # Подтверждаем
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//button[contains(@class, "by-button btn-confirm")]'))).click()
    time.sleep(random.choice(rand2))

    if mode == "Продажа-Покупка":
        get_data_bybit(driver, mode='Продажа', bank = new_bank, crypto=crypto)
        time.sleep(random.choice(rand0))
        # Покупка
        sell_buy_button_by('buy')
        time.sleep(random.choice(rand1))
        get_data_bybit(driver, mode='Покупка', bank = new_bank, crypto=crypto)
    else:
        get_data_bybit(driver, mode='Покупка', bank = new_bank, crypto=crypto)
        time.sleep(random.choice(rand0))
        # Продажа
        sell_buy_button_by('sell')
        time.sleep(random.choice(rand1))
        get_data_bybit(driver, mode='Продажа', bank = new_bank, crypto=crypto)
def get_data_bybit_1_currency(driver, crypto, risk=False):
    # Считываем информацию по одной криптовалюте по разным банкам
    time.sleep(random.choice([5.04, 5.12, 4.78, 4.82])) # Дождемся пока все загрузится
    # Payeer
    time.sleep(random.choice(rand3))
    if risk:
        choose_bank_by(mode="Покупка-Продажа", new_bank="Payeer", crypto=crypto, risk=True)
    else:
        change_bank_by(mode="Покупка-Продажа", old_bank='Tinkoff', new_bank="Payeer", crypto=crypto)
    time.sleep(random.choice(rand2))
    # Райф
    change_bank_by(mode="Продажа-Покупка", old_bank="Payeer", new_bank="Raiffeisenbank", crypto=crypto)
    # Хоум кредит
    change_bank_by(mode="Покупка-Продажа", old_bank="Raiffeisenbank", new_bank="Home Credit Bank(Russia)", crypto=crypto)
    # Альфа-банк
    driver.refresh()
    time.sleep(random.choice(rand2))
    choose_bank_by(mode="Продажа-Покупка", new_bank="А-Банк", crypto=crypto)
    # Сбербанк
    time.sleep(random.choice(rand2))
    change_bank_by(mode="Покупка-Продажа", old_bank="А-Банк", new_bank="Sberbank", crypto=crypto)
    # Тинькофф
    change_bank_by(mode="Продажа-Покупка", old_bank="Sberbank", new_bank="Tinkoff", crypto=crypto)
def data_bybit():
    get_data_bybit_1_currency(driver, crypto='USDT', risk=True)
    time.sleep(random.choice(rand2))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//span[@class='trade-list-icon__item'][contains(text(), 'BTC')]"))).click()
    time.sleep(random.choice(rand1))
    get_data_bybit_1_currency(driver, crypto='BTC')
    time.sleep(random.choice(rand2))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//span[@class='trade-list-icon__item'][contains(text(), 'ETH')]"))).click()
    time.sleep(random.choice(rand2))
    get_data_bybit_1_currency(driver, crypto='ETH')


def sell_buy_button_h(button, currency = "usdt"): # Нажимает на кнопку покупки или продажи
    if button == 'buy':
        driver.find_element(By.XPATH, f'//a[contains(@href, "buy-{currency}-rub")]').click()
    else:
        driver.find_element(By.XPATH, f'//a[contains(@href, "sell-{currency}-rub")]').click()
def get_data_huobi(driver, mode = 'Покупка', bank = None, crypto = None): # Собирает данные о пользователях

    traders_names = driver.find_elements(By.XPATH, f'//h3[contains(@class, "font14")]')
    if not traders_names:
        time.sleep(0.7)
        traders_names = driver.find_elements(By.XPATH, f'//h3[contains(@class, "font14")]')
        if not traders_names:
            return None

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "otc-trade-list")]')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//div[contains(@class, "price")]')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//h3[contains(@class, "font14")]')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//h3[contains(@class, "font14")]')))
    buy_price = driver.find_element(By.XPATH, f'//div[contains(@class, "price")]').text.split()[0].replace(',', '') # Курс
    limit_box = driver.find_element(By.CLASS_NAME, "limit-box")
    limits = [limit.text.replace(',', '').rstrip(' RUB').lstrip('-') for limit in limit_box.find_element(By.CLASS_NAME, "limit").find_elements(By.TAG_NAME, "span")]
    volume = limit_box.find_element(By.CLASS_NAME, "stock").text.replace(',', '').split()[0]

    new_row = {
        'p2p_exchange_rate': buy_price,
        'low_bound': limits[0],
        'high_bound': limits[1],
        'volume': volume,
        'bank': bank,
        'exchange': 'Huobi',
        'crypto': crypto
    }

    global buy_data, sell_data

    if mode == 'Покупка':
        buy_data = pd.concat([buy_data, pd.DataFrame([new_row])], ignore_index=True)
    else:
        sell_data = pd.concat([sell_data, pd.DataFrame([new_row])], ignore_index=True)

    return
def choose_bank_h(mode, new_bank, currency): # Если сброшены настройки платежных систем, то выбирает нужный нам банк
    # Клик на список банков
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway
    time.sleep(random.choice([0.54, 0.68, 0.62, 0.45]))
    # Находим нужный нам банк и кликаем на него
    new_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{new_bank}")]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)

    # driver.execute_script("window.scrollTo(0, 0);")

    ActionChains(driver).move_to_element(new_bank_button).click().perform()
    time.sleep(random.choice([0.54, 0.68, 0.62, 0.45]))
    driver.execute_script("window.scrollTo(0, 0);")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway подтверждаем
    time.sleep(random.choice(rand2))
    if mode == 'Продажа_Покупка': # Сначала записываем продажу, потом покупку
        get_data_huobi(driver, mode='Продажа', bank = new_bank, crypto = currency)

        # Продажа новый банк
        sell_buy_button_h('buy', currency)
        time.sleep(random.choice(rand2))
        get_data_huobi(driver, mode='Покупка', bank = new_bank, crypto = currency)
    else: # Наоборот
        get_data_huobi(driver, mode='Покупка', bank = new_bank, crypto = currency)
        # Продажа новый банк
        sell_buy_button_h('sell', currency)
        time.sleep(random.choice(rand2))
        get_data_huobi(driver, mode='Продажа', bank = new_bank, crypto = currency)
def change_bank_h(mode, old_bank, new_bank, currency): # Убирает метку со старого банка, чтобы перейти на новый банк
    # Клик на список банков
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway
    time.sleep(random.choice([0.6, 0.7]))
    # клик на старый банк
    old_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{old_bank}")]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", old_bank_button)
    ActionChains(driver).move_to_element(old_bank_button).click().perform()
    time.sleep(random.choice(rand1))
    # клик на новый банк
    new_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{new_bank}")]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", new_bank_button)
    # driver.execute_script("window.scrollTo(0, 0);")
    ActionChains(driver).move_to_element(new_bank_button).click().perform()

    driver.execute_script("window.scrollTo(0, 0);")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway подтверждаем
    time.sleep(random.choice(rand2))
    if mode == 'Продажа_Покупка':
        get_data_huobi(driver, mode='Продажа', bank = new_bank, crypto = currency)

        # Покупка новый банк
        sell_buy_button_h('buy', currency)
        time.sleep(random.choice(rand3))
        get_data_huobi(driver, mode='Покупка', bank = new_bank, crypto = currency)
    else:
        get_data_huobi(driver, mode='Покупка', bank = new_bank, crypto = currency)

        # Продажа новый банк
        sell_buy_button_h('sell', currency)
        time.sleep(random.choice(rand3))
        get_data_huobi(driver, mode='Продажа', bank = new_bank, crypto = currency)
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
    change_bank_h(mode='Покупка_Продажа', old_bank="Alfa-bank", new_bank="Sberbank", currency=currency)
    # Тинькофф
    change_bank_h(mode='Продажа_Покупка', old_bank="Sberbank", new_bank="Tinkoff", currency=currency)
    # Сбрасываем, возвращаем к исходному состоянию
    time.sleep(random.choice(rand1))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'//span[contains(@class, "over-text") and contains(., "Filter")]'))).click()  # payway
    time.sleep(random.choice(rand1))
    # клик на старый банк
    old_bank_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "Tinkoff")]')))
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", old_bank_button)
    ActionChains(driver).move_to_element(old_bank_button).pause(1).click().perform()
    time.sleep(random.choice(rand1))
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


def get_data_bitget(driver, mode = 'Покупка', bank=None, crypto=None):
    traders_names = driver.find_elements(By.XPATH, '//a[@class="list-item__nickname"]')
    if not traders_names:
        time.sleep(0.7)
        traders_names = driver.find_elements(By.XPATH, '//a[@class="list-item__nickname"]')
        if not traders_names:
            return None

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'hall-list-item-wrap.hall-list')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="price-shower"]')))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="list-item__nickname"]')))
    buy_price = float(driver.find_element(By.XPATH, '//span[@class="price-shower"]').text.replace(',', '').strip().split()[0])
    lst = [quantity.text for quantity in driver.find_elements(By.XPATH, '//div[contains(@class, "list_limit")]/span[2]//span') if quantity.text.strip()]  # [::2]  # '218.4927 USDT', '10,500.00 ~ 19,860.98 RUB', '5,355.3127 USDT', '30,000.00 ~ 100,000.01 RUB', '2,058.9948 USDT'
    limits = lst[1].split()[0].split("–")
    limits = [float(element.replace(',', '')) for element in limits]
    volume = float(lst[0].split()[0].replace(',', ''))

    new_row = {
        'p2p_exchange_rate': buy_price,
        'low_bound': limits[0],
        'high_bound': limits[1],
        'volume': volume,
        'bank': bank,
        'exchange': 'Bitget',
        'crypto': crypto
    }

    global buy_data, sell_data
    if mode == 'Покупка':
        buy_data = pd.concat([buy_data, pd.DataFrame([new_row])], ignore_index=True)
    else:
        sell_data = pd.concat([sell_data, pd.DataFrame([new_row])], ignore_index=True)

    return
def choose_bank_bi(mode, new_bank, crypto):
    # payway click
    payway_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//dl[contains(@class, "ml-8px")]//span[contains(@class, "bit-input__suffix")]')))
    payway_dropdown.click()
    time.sleep(random.choice([0.5, 0.48, 0.54, 0.52, 0.56]))

    if new_bank == 'Payeer':
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, f'//span[contains(., "Ozon банк")]'))))
    else:
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f'//span[contains(., "{new_bank}")]'))))

    # Choose bank
    payeer_option = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//span[contains(., "{new_bank}")]')))
    payeer_option.click()

    time.sleep(random.choice(rand2))
    if mode == "Покупка-Продажа":
        get_data_bitget(driver, mode='Покупка', bank=new_bank, crypto=crypto)
        # Продажа новый банк
        sell_buy_button_bi('sell')
        time.sleep(random.choice(rand2))
        get_data_bitget(driver, mode='Продажа', bank=new_bank, crypto=crypto)
    else:
        get_data_bitget(driver, mode='Продажа', bank=new_bank, crypto=crypto)

        # Продажа новый банк
        sell_buy_button_bi('buy')
        time.sleep(random.choice(rand2))
        get_data_bitget(driver, mode='Покупка', bank=new_bank, crypto=crypto)
def sell_buy_button_bi(button):
    if button == 'buy':
        driver.find_element(By.XPATH, '//span[contains(text(), "Покупка")]').click()
    else:
        driver.find_element(By.XPATH, '//span[contains(text(), "Продажа")]').click()
def get_data_1_currency_bi(crypto):
    time.sleep(random.choice(rand2))
    # Райффайзен
    choose_bank_bi(mode = "Покупка-Продажа", new_bank="Райффайзен", crypto=crypto)
    # PAYEER
    choose_bank_bi(mode = "Продажа-Покупка", new_bank="Payeer", crypto=crypto)
    # Хоум
    choose_bank_bi(mode = "Покупка-Продажа", new_bank="Хоум Кредит Банк", crypto=crypto)
    # Альфа
    choose_bank_bi(mode = "Продажа-Покупка", new_bank="Альфа-Банк", crypto=crypto)
    # Сбер
    choose_bank_bi(mode = "Покупка-Продажа", new_bank="Local Card-Green", crypto=crypto)
    # Тинькофф
    choose_bank_bi(mode = "Продажа-Покупка", new_bank="Local Card-Yellow", crypto=crypto)
def data_bitget():
    time.sleep(1)
    get_data_1_currency_bi(crypto = 'USDT')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="bit-input__suffix"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "BTC")]'))).click()
    get_data_1_currency_bi(crypto = 'BTC')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="bit-input__suffix"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "ETH")]'))).click()
    get_data_1_currency_bi(crypto = 'ETH')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="bit-input__suffix"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "USDT")]'))).click()
    time.sleep(random.choice([3, 4.23, 4.41, 5.21, 6.12]))


# Bybit
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url='https://www.bybit.com/fiat/trade/otc/?actionType=1&token=USDT&fiat=RUB&paymentMethod=')
time.sleep(random.choice([9.84, 9.76, 9.92, 10.11, 10.21, 10.19]))
autorization()
data_bybit()
driver.quit()
time.sleep(random.choice(rand2))
# Huobi
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)
driver.get(url='https://www.htx.com/en-us/fiat-crypto/c2c-common/buy-usdt-rub/')
time.sleep(random.choice(rand3))
video_close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//i[contains(@class, "video-close")]'))).click()
data_huobi()
driver.quit()
time.sleep(random.choice(rand3))
# Bitget
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)
driver.get(url='https://xdreampay.com/ru?path=b1b646718ab73f54ad94&og=https%3A%2F%2Fwww.bitget.com&userType=0')
data_bitget()

# Расчет связок
bank_name_mapping = {
    'Райффайзен': 'Raiffeisenbank',
    'Alfa-bank': 'A-Bank',
    'Альфа-Банк': 'A-Bank',
    'А-Банк': 'A-Bank',
    'RNCB': 'Payeer',
    'Хоум Кредит Банк': 'Home Credit Bank(Russia)',
    'Home Credit Bank (Russia)': 'Home Credit Bank(Russia)',
    'Local Card-Green': 'Sberbank',
    'Local Card-Yellow': 'Tinkoff'
}
crypto_mapping = {'usdt': 'USDT',
                  'btc': 'BTC',
                  'eth': 'ETH'}

buy_data['bank'] = buy_data['bank'].replace(bank_name_mapping)
sell_data['bank'] = sell_data['bank'].replace(bank_name_mapping)
buy_data['crypto'] = buy_data['crypto'].replace(crypto_mapping)
sell_data['crypto'] = sell_data['crypto'].replace(crypto_mapping)

buy_data.to_excel("_Покупка_.xlsx", index = False)
sell_data.to_excel("_Продажа_.xlsx", index = False)

buy_data[['p2p_exchange_rate', 'low_bound', 'high_bound', 'volume']] = buy_data[['p2p_exchange_rate', 'low_bound', 'high_bound', 'volume']].astype('float64')
sell_data[['p2p_exchange_rate', 'low_bound', 'high_bound', 'volume']] = sell_data[['p2p_exchange_rate', 'low_bound', 'high_bound', 'volume']].astype('float64')

# Тейк-мейк: покупаем с buy_data (по чужой заявке), продаем с buy_data (по своей заявке)
def create_take_make_inside_buy(df):
    result = []
    for crypto, group in df.groupby('crypto'):
        if group.shape[0] < 2:
            continue
        # Декартово произведение внутри одной группы
        combined = group.merge(group, how='cross', suffixes=('_покупка', '_продажа'))

        # Убираем все записи, где неположительные спреды (они нас не интересуют)
        combined = combined[combined['p2p_exchange_rate_покупка'] < combined['p2p_exchange_rate_продажа']]

        # Вычисляем спред и доходность
        combined['spread'] = combined['p2p_exchange_rate_продажа'] - combined['p2p_exchange_rate_покупка']
        combined['return_pct'] = (combined['spread'] / combined['p2p_exchange_rate_покупка']) * 100

        # Флаги мейкерства: покупка по тейку (0), продажа по мейку (1)
        combined['покупка_по_мейку'] = 0
        combined['продажа_по_мейку'] = 1
        result.append(combined)

    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()
# Мейк-тейк: покупаем с sell_data (по своей заявке), продаем с sell_data (по чужой заявке)
def create_make_take_inside_sell(df):
    result = []
    for crypto, group in df.groupby('crypto'):
        if group.shape[0] < 2:
            continue
        combined = group.merge(group, how='cross', suffixes=('_покупка', '_продажа'))
        combined = combined[combined['p2p_exchange_rate_покупка'] < combined['p2p_exchange_rate_продажа']]
        combined['spread'] = combined['p2p_exchange_rate_продажа'] - combined['p2p_exchange_rate_покупка']
        combined['return_pct'] = (combined['spread'] / combined['p2p_exchange_rate_покупка']) * 100
        combined['покупка_по_мейку'] = 1
        combined['продажа_по_мейку'] = 0
        result.append(combined)
    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()
# Тейк-тейк: покупаем с buy_data (по чужой заявке), продаем с sell_data (по чужой заявке) | Мейк-мейк: покупаем с sell_data (по своей заявке), продаем с buy_data (по своей заявке)
def create_take_take_deals(buy_df, sell_df, take_take = True):
    results = []
    for crypto, buy_group in buy_df.groupby('crypto'):
        sell_group = sell_df[sell_df['crypto'] == crypto]
        if sell_group.empty or buy_group.empty:
            continue
        combined = buy_group.merge(sell_group, how='cross', suffixes=('_покупка', '_продажа'))
        combined = combined[combined['p2p_exchange_rate_покупка'] < combined['p2p_exchange_rate_продажа']]
        combined['spread'] = combined['p2p_exchange_rate_продажа'] - combined['p2p_exchange_rate_покупка']
        combined['return_pct'] = (combined['spread'] / combined['p2p_exchange_rate_покупка']) * 100
        if take_take:
            combined['покупка_по_мейку'] = 0
            combined['продажа_по_мейку'] = 0
        else:
            combined['покупка_по_мейку'] = 1
            combined['продажа_по_мейку'] = 1
        results.append(combined)
    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()


take_make_internal_df = create_take_make_inside_buy(buy_data)
make_take_internal_df = create_make_take_inside_sell(sell_data)
take_take_internal_df = create_take_take_deals(buy_data, sell_data)
make_make_internal_df = create_take_take_deals(sell_data, buy_data, take_take = False)

df = pd.concat([take_make_internal_df, make_take_internal_df, take_take_internal_df, make_make_internal_df])

df.drop(columns=['p2p_exchange_rate_покупка', 'p2p_exchange_rate_продажа', 'crypto_продажа'], inplace = True)
df.rename(columns = {'crypto_покупка': 'crypto'}, inplace = True)

crypto_order = ['USDT', 'BTC', 'ETH']
df['crypto'] = pd.Categorical(df['crypto'], categories=crypto_order, ordered=True)
df.sort_values(['crypto', 'return_pct'], ascending=[True, False], inplace = True)

df.to_excel('spread.xlsx', index = False)