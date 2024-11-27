from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
from datetime import datetime, timedelta
from pynput import keyboard
import threading
import os
import platform

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def find_element(self, by, value):
        try:
            element = self.driver.find_element(by, value)
            if element is not None:
                return element
        except StaleElementReferenceException:
            print(f"find_element Failed to interact with element {by} = {value}")
        except NoSuchElementException:
            print(f"find_element Failed to find element {by} = {value}")
        return None

    def element_text(self, by, value):
        try:
            element = self.find_element(by, value)
            if element is not None:
                text = element.text
                return text
        except StaleElementReferenceException:
            print(f"element_text Failed to interact with element {by} = {value}")
        return None
        
    @property
    def deadline_time(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[1]/span[4]/span[2]')
        if element is not None:
            deadline_time_str = element
            return datetime.strptime(deadline_time_str, "%H:%M").time()
        return None
    @property
    def current_time(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/span[2]/span')
        if element is not None:
            current_time_str = element
            return datetime.strptime(current_time_str, "%H:%M:%S").time()
        return None
    def set_add_price(self, add_price):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div[2]/div/input')
        if element is not None:
            element.clear()
            element.send_keys(add_price)
    def increase_price(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div[3]/div/span')
        if element is not None:
            element.click()

    def bid(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[3]/div[3]/div/span')
        if element is not None:
            element.click()

    def edit_verification_code(self):
        element = self.find_element(By.XPATH, '//*[@id="bidprice"]')
        if element is not None:
            element.click()
    def confirm_verification_code(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[2]/div[3]/div[1]/span')
        if element is not None:
            element.click()
    def cancel_verification_code(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[2]/div[3]/div[2]/span')
        if element is not None:
            element.click()

    def confirm_bid(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[3]/div/span')
        if element is not None:
            element.click()

    @property
    def bid_price(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[1]/span/span')
        if element is not None:
            return element
        return None
    @property
    def current_price(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/span[3]/span')
        if element is not None:
            return element
        return None

# init env
url = os.environ['URL']
architecture = platform.machine()
if architecture == 'x86_64':
    service = Service('/usr/local/bin/chromedriver')
elif architecture == 'arm64':
    service = Service('/opt/homebrew/bin/chromedriver')
else:
    print("Unknown architecture: " + architecture)

# Setup chrome options
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:8000")

# Choose Chrome Browser
driver = webdriver.Chrome(service=service, options=options)

# Open the webpage
#driver.get(url)
driver.switch_to.window(driver.window_handles[-1])

# Instantiate LoginPage
login_page = LoginPage(driver)

deadline_time = None
while deadline_time is None:
    deadline_time = login_page.deadline_time
    time.sleep(0.1)
print(deadline_time)

def on_press(key):
    try:
        if key == keyboard.Key.enter:
            login_page.confirm_verification_code()
        elif key == keyboard.Key.backspace:
            login_page.confirm_bid()
        elif key == keyboard.Key.esc:
            login_page.cancel_verification_code()
    except AttributeError:
        pass

def key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def bid_help(add_price):
    login_page.set_add_price(add_price)
    login_page.increase_price()
    login_page.bid()
    login_page.edit_verification_code()

def price_listener():
    while True:
        time.sleep(0.1)
        current_price = login_page.current_price
        bid_price = login_page.bid_price
        print(current_price)
        if current_price is None or bid_price is None:
            continue
        print(bid_price)
        price_difference = abs(int(bid_price) - int(current_price))
        print(price_difference)

        if price_difference <= 300:
            break
    print("price listener stop")
    print(current_price)

    time.sleep(0.1)
    login_page.confirm_verification_code()

def time_listener(seconds):
    while True:
        time.sleep(0.1)
        current_time = login_page.current_time
        if current_time is None:
            continue
        print(current_time)
        time_difference = datetime.combine(datetime.today(), deadline_time) - datetime.combine(datetime.today(), current_time)
        print(time_difference)

        if time_difference <= timedelta(seconds=seconds):
            break
    print("time listener stop")
    print(current_time)

    time.sleep(0.6)
    login_page.confirm_verification_code()


# Create and start a new thread for the time listener
#time_thread = threading.Thread(target=time_listener(2))
#time_thread.start()

price_thread = threading.Thread(target=price_listener())
price_thread.start()

key_thread = threading.Thread(target=key_listener())
key_thread.start()
