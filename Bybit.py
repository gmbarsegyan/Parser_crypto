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
options.add_argument(f"--proxy-server=194.26.207.51:8000")

rand0 = [0.8, 0.67, 0.82, 0.73, 0.7, 0.69]
rand1 = [1, 1.23, 1.36, 1.45, 1.12, 1.27]
rand2 = [2, 2.14, 2.19, 2.76, 2.31, 2.27]
rand3 = [3, 3.14, 3.19, 3.76, 3.31, 3.27]
rand4 = [4.01, 4.03, 3.94, 3.82, 4.11, 4.12, 4.22, 4.2]

def close_extra_tabs(driver, new_bank):
    time.sleep(0.4)
    # Получаем список идентификаторов открытых вкладок
    tabs = driver.window_handles

    # Если количество вкладок больше одной, значит, есть лишние вкладки
    while len(tabs) > 1:
        time.sleep(0.541)
        # Закрываем лишние вкладки, начиная с последней
        for tab in tabs[1:]:
            driver.switch_to.window(tab)
            driver.close()

        # Переключаемся обратно на активную вкладку
        driver.switch_to.window(tabs[0])

        # Открываем список банков
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "paywayAnchorList")]'))).click()

        # Выбираем нужный банк
        new_bank_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{new_bank}"]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)
        ActionChains(driver).move_to_element(new_bank_button).click().perform()

        time.sleep(2)

        tabs = driver.window_handles

    print("Закрыл окно")


# def close_extra_tabs(driver, new_bank):
#     time.sleep(0.4)
#     # Получаем список идентификаторов открытых вкладок
#     tabs = driver.window_handles
#
#     # Если количество вкладок больше одной, значит, есть лишние вкладки
#     if len(tabs) > 1:
#         time.sleep(0.541)
#         # Закрываем лишние вкладки, начиная с последней
#         for tab in tabs[1:]:
#             driver.switch_to.window(tab)
#             driver.close()
#
#         # Переключаемся обратно на активную вкладку
#         driver.switch_to.window(tabs[0])
#
#         # Открываем список банков
#         WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "paywayAnchorList")]'))).click()
#
#         # Выбираем нужный банк
#         new_bank_button = WebDriverWait(driver, 20).until(
#             EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{new_bank}"]')))
#         driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)
#         ActionChains(driver).move_to_element(new_bank_button).click().perform()
#
#         time.sleep(2)
#
#         tabs = driver.window_handles
#         if len(tabs) > 1:
#             time.sleep(0.544)
#             # Закрываем лишние вкладки, начиная с последней
#             for tab in tabs[1:]:
#                 driver.switch_to.window(tab)
#                 driver.close()
#
#             # Переключаемся обратно на активную вкладку
#             driver.switch_to.window(tabs[0])
#
#             # Открываем список банков
#             WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "paywayAnchorList")]'))).click()
#
#             # Выбираем нужный банк
#             new_bank_button = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.XPATH, f'//div[@class="content"]/span[@title="{new_bank}"]')))
#             driver.execute_script("arguments[0].scrollIntoView(true);", new_bank_button)
#             ActionChains(driver).move_to_element(new_bank_button).click().perform()
#
#         # Ждем несколько секунд
# #        time.sleep(3)  # Измените время ожидания по вашему усмотрению
#         print("Закрыл окно")


to_int_without_comma_by = lambda spisok: [float(limit.translate({ord(','): None})) for limit in spisok]
list_to_str = lambda x: ', '.join(x)

def get_data_bybit(driver, vremya, mode = 'Покупка'):
    traders_names = driver.find_elements(By.XPATH, '//div[contains(@class, "advertiser-name")]')
    if not traders_names:
        time.sleep(0.7)
        traders_names = driver.find_elements(By.XPATH, '//div[contains(@class, "advertiser-name")]')
        if not traders_names:
            if mode == 'Покупка':
                with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                    pd.DataFrame(['нет данных']).to_excel(writer, sheet_name='Sheet_1', index=False, header=False,
                                                          startrow=writer.sheets[
                                                              'Sheet_1'].max_row if 'Sheet_1' in writer.sheets else 0)
            else:
                with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                    pd.DataFrame(['нет данных']).to_excel(writer, sheet_name='Sheet_2', index=False, header=False,
                                                          startrow=writer.sheets[
                                                              'Sheet_2'].max_row if 'Sheet_2' in writer.sheets else 0)
            return None

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//tr'))) #######
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'price-amount'))) #########
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "advertiser-name")]'))) ##########

    traders_names = [trader.text for trader in
                     traders_names]
    buy_prices = [float(price.text.replace(',', '').rstrip("RUB")) for price in driver.find_elements(By.CLASS_NAME, 'price-amount')]  # Курс
    lst = [quantity.text for quantity in driver.find_elements(By.CLASS_NAME,
                                                              'ql-value')]  # '218.4927 USDT', '10,500.00 ~ 19,860.98 RUB', '5,355.3127 USDT', '30,000.00 ~ 100,000.01 RUB', '2,058.9948 USDT'
    limits = np.char.strip(
        np.array([[lst[qnt_idx].split()[i] for i in [0, 2]] for qnt_idx in range(1, len(lst), 2)]))  # Лимиты
    limits = np.array([to_int_without_comma_by(elements) for elements in limits])
    volume = [lst[qnt_idx].split()[0] for qnt_idx in range(0, len(lst), 2)]  # Объем
    volume = list(map(float, [vol.translate({ord(','): None}) for vol in volume]))

    traders_elements = driver.find_elements(By.XPATH, '//tr')
    paying_systems = []
    for trader_element in traders_elements[2:]:
        banks_elements = trader_element.find_elements(By.XPATH, './/div[@class="trade-list-tag"]')
        banks_list = [bank_element.text for bank_element in banks_elements]
        paying_systems.append(banks_list)

    paying_systems = list(map(list_to_str, paying_systems))
    df = pd.DataFrame({'Имя трейдера': traders_names,
                       'Курс': buy_prices,
                       'Объём': volume,
                       'Нижний лимит': list(limits[:, 0]),
                       'Верхний лимит': list(limits[:, 1]),
                       'Платежные системы': paying_systems})
    df['Время парсинга'] = vremya
    # Добавляем строку из прочерков в конец DataFrame
    df.loc[len(df)] = ['-' for _ in range(len(df.columns))]

    if mode == 'Покупка':
        with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet_1', index=False, header=False,
                        startrow=writer.sheets['Sheet_1'].max_row if 'Sheet_1' in writer.sheets else 0)
    else:
        with pd.ExcelWriter('Данные для ИПС.xlsx', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet_2', index=False, header=False,
                        startrow=writer.sheets['Sheet_2'].max_row if 'Sheet_2' in writer.sheets else 0)
    return df


def autorization():
    # Дождемся появления кнопки "Подтвердить"
    confirm_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "ant-btn-primary") and contains(., "Подтвердить")]')))
    confirm_button.click()

    # Авторизация
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'header-login')))
    time.sleep(random.choice(rand3))
    login_button.click()

    email_window = driver.find_element(By.XPATH, f'//input[contains(@placeholder, "Эл. почта")]')
    email_window.send_keys("login")  # Вставьте свой логин

    password_window = driver.find_element(By.XPATH, f'//input[contains(@placeholder, "Пароль")]')
    time.sleep(random.choice(rand1))
    password_window.send_keys("password")  # Вставьте свой пароль

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

def choose_bank_by(mode, new_bank, risk = False):
    # Открываем список банков
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//div[contains(@class, "paywayAnchorList")]'))).click()

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
        get_data_bybit(driver, vremya, mode='Покупка')
        time.sleep(random.choice(rand0))
        sell_buy_button_by('sell')
        if risk:
            time.sleep(random.choice([6.09, 4.12, 4.18, 5.07]))  # Это время дается чтобы закрыть всплывающее окно, предупреждающее о рисках при совершении сделок на продажу
        # Продажа
        time.sleep(random.choice(rand1))

        get_data_bybit(driver, vremya, mode='Продажа')
    else:
        # Продажа
        get_data_bybit(driver, vremya, mode='Продажа')
        time.sleep(random.choice(rand0))
        # Покупка
        sell_buy_button_by('buy')
        if risk:
            time.sleep(random.choice([5.88, 5.96, 6.14, 6.12, 6.01, 5.76]))  # Это время дается чтобы закрыть всплывающее окно, предупреждающее о рисках при совершении сделок на продажу
            risk_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'by-button__content')))
            risk_button.click()
        time.sleep(random.choice(rand1))

        get_data_bybit(driver, vremya, mode='Покупка')

def change_bank_by(mode, old_bank, new_bank):
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
        get_data_bybit(driver, vremya, mode='Продажа')
        time.sleep(random.choice(rand0))
        # Покупка
        sell_buy_button_by('buy')
        time.sleep(random.choice(rand1))
        get_data_bybit(driver, vremya, mode='Покупка')
    else:
        get_data_bybit(driver, vremya, mode='Покупка')
        time.sleep(random.choice(rand0))
        # Продажа
        sell_buy_button_by('sell')
        time.sleep(random.choice(rand1))
        get_data_bybit(driver, vremya, mode='Продажа')

def get_data_bybit_1_currency(driver, risk=False):
    # Считываем информацию по одной криптовалюте по разным банкам
    time.sleep(random.choice([5.04, 5.12, 4.78, 4.82])) # Дождемся пока все загрузится
    # Payeer
    time.sleep(random.choice(rand3))
    if risk:
        choose_bank_by(mode="Покупка-Продажа", new_bank="Payeer", risk=True) ######
    else:
        choose_bank_by(mode="Покупка-Продажа", new_bank="Payeer") ##########
    time.sleep(random.choice(rand2))
    # Райф
    change_bank_by(mode="Продажа-Покупка", old_bank="Payeer", new_bank="Raiffeisenbank")
    # Хоум кредит
    change_bank_by(mode="Покупка-Продажа", old_bank="Raiffeisenbank", new_bank="Home Credit Bank(Russia)")
    # Альфа-банк
    driver.refresh()
    choose_bank_by(mode="Продажа-Покупка", new_bank="A-Bank")
    # Сбербанк
    time.sleep(random.choice(rand2))
    change_bank_by(mode="Покупка-Продажа", old_bank="A-Bank", new_bank="Sberbank")
    # Тинькофф
    change_bank_by(mode="Продажа-Покупка", old_bank="Sberbank", new_bank="Tinkoff")

def data_bybit():
    get_data_bybit_1_currency(driver, risk=True)
    time.sleep(random.choice(rand2))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@class='fiat-otc-option-flex'][contains(text(), 'USDT')]"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@class='fiat-otc-option-flex'][contains(text(), 'BTC')]"))).click()
    time.sleep(random.choice(rand1))
    get_data_bybit_1_currency(driver)
    time.sleep(random.choice(rand2))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@class='fiat-otc-option-flex'][contains(text(), 'BTC')]"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[@class='fiat-otc-option-flex'][contains(text(), 'ETH')]"))).click()
    time.sleep(random.choice(rand2))
    get_data_bybit_1_currency(driver)

# Берем время в самом начале и переходим по ссылке
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url='https://www.bybit.com/fiat/trade/otc/?actionType=1&token=USDT&fiat=RUB&paymentMethod=')
vremya = time.strftime("%H:%M:%S", time.localtime())  # берем время
time.sleep(random.choice([9.84, 9.76, 9.92, 10.11, 10.21, 10.19]))

autorization()

data_bybit()



# except Exception as ex:
#     print(ex)
# finally:
#     driver.close()
#     driver.quit()
