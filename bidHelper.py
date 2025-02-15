from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
from datetime import datetime, timedelta
from pynput import keyboard
from multiprocessing import Process
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
            pass
            #print(f"find_element Failed to interact with element {by} = {value}")
        except NoSuchElementException:
            pass
            #print(f"find_element Failed to find element {by} = {value}")
        return None

    def element_text(self, by, value):
        try:
            element = self.find_element(by, value)
            if element is not None:
                text = element.text
                return text
        except StaleElementReferenceException:
            print(f"element_text Failed to interact with element {by} = {value}")
        except NoSuchElementException:
            print(f"element_text Failed to find element {by} = {value}")
        return None

    def element_value(self, by, value):
        try:
            element = self.find_element(by, value)
            if element is not None:
                value = element.get_attribute('value')
                return value
        except StaleElementReferenceException:
            print(f"element_value Failed to interact with element {by} = {value}")
        except NoSuchElementException:
            print(f"element_value Failed to find element {by} = {value}")
        return None

    def element_click(self, by, value, retries=3):
        for i in range(retries):
            try:
                element = self.find_element(by, value)
                if element is not None:
                    element.click()
                    return
            except StaleElementReferenceException:
                print(f"Attempt {i+1} of element_click failed to interact with element {by} = {value}. Retrying...")
            except NoSuchElementException:
                print(f"Attempt {i+1} of element_click Failed to find element {by} = {value}. Retrying...")
        #print(f"element_click: Failed to find and interact with element {by} = {value} after {retries} attempts")
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
    @property
    def confirm_time(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[2]/span[3]')
        if element is not None:
            confirm_time_str = element.split("：")[-1]
            return datetime.strptime(confirm_time_str, "%Y-%m-%d %H:%M:%S").time()
        return None
    def set_add_price(self, add_price):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div[2]/div/input')
        if element is not None:
            element.clear()
            element.send_keys(add_price)
    def increase_price(self):
        element = self.element_click(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[1]/div[3]/div/span')
        if element is not None:
            element.click()

    def bid(self):
        element = self.element_click(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[3]/div[3]/div/span')
        if element is not None:
            element.click()

    def first_bid(self):
        element = self.element_click(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[2]/div[2]/div[2]/span')
        if element is not None:
            element.click()

    @property
    def verification_code(self):
        element = self.element_value(By.XPATH, '//*[@id="bidprice"]')
        if element is not None:
            return element
        return None

    def edit_verification_code(self):
        element = self.element_click(By.XPATH, '//*[@id="bidprice"]')
        if element is not None:
            element.click()
    def confirm_verification_code(self):
        element = self.element_click(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[2]/div[3]/div[1]/span')
        if element is not None:
            element.click()
    def cancel_verification_code(self):
        element = self.element_click(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[2]/div[3]/div[2]/span')
        if element is not None:
            element.click()

    def confirm_bid(self):
        element = self.element_click(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[3]/div/span')
        if element is not None:
            element.click()

    @property
    def bid_price(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[1]/span/span')
        if element is not None:
            return element
        return None
    @property
    def max_price(self):
        element = self.element_text(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/span[5]/span/span[2]')
        if element is not None:
            return element
        return None

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
driver.switch_to.window(driver.window_handles[-1])

# Instantiate LoginPage
login_page = LoginPage(driver)

deadline_time = None
while deadline_time is None:
    deadline_time = login_page.deadline_time
    time.sleep(0.1)
print(f'deadline time: {deadline_time}')

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

def first_bid_help():
    login_page.first_bid()
    login_page.edit_verification_code()

def price_listener():
    print("price listener stop")
    while True:
        max_price = login_page.max_price
        bid_price = login_page.bid_price
        #print(f'max price: {max_price}')
        if max_price is not None and bid_price is not None:
            #print(f'bid price: {bid_price}')
            verification_code = login_page.verification_code
            price_difference = int(max_price) - int(bid_price)
            if 0 <= price_difference <= 300  and len(verification_code) == 4:
                print(f'verification code: {verification_code}')
                print(f'price listener stop {bid_price}')
                login_page.confirm_verification_code()
                confirm_time = datetime.now()
                formatted_time = confirm_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f'bid price {bid_price}, max price {max_price}, verification code {verification_code}, price confirm {formatted_time}')
            else:
                print(f'bid price {bid_price} is too bigger than max price {max_price}, or verification code {verification_code} not right')

def time_listener(seconds):
    print("time listener start")
    while True:
        current_time = login_page.current_time
        if current_time is not None:
            time_difference = datetime.combine(datetime.today(), deadline_time) - datetime.combine(datetime.today(), current_time)
            print(f'time difference: {time_difference}')
            if time_difference <= timedelta(seconds=seconds):
                print(f'time listener stop {current_time}')
                login_page.confirm_verification_code()
                #confirm_time = datetime.now()
                #formatted_time = confirm_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                #print(f'time confirm: {formatted_time}')
                print(f'confirm time: {current_time}')
            else:
                print(f'current time: {current_time}')

def sys_time_listener(sys_seconds):
    print("sys time listener start")
    while True:
        #current_time = login_page.current_time
        now = datetime.now()
        seconds = now.second
        microseconds = now.microsecond
        fractional_seconds = microseconds / 1_000_000
        total_seconds = seconds + fractional_seconds
        if abs(total_seconds - sys_seconds) < 0.05:
            login_page.confirm_verification_code()
            #print(f'time confirm: {current_time}')
            print(f'sys confirm time: {now}')
            confirm_time = login_page.confirm_time
            print(f'remote confirm time: {confirm_time}')
            time.sleep(0.5)
            login_page.confirm_bid()
        else:
            pass
            #print(f'current time: {now}')

def bid_time_listener(price, sys_seconds, bid):
    print("bid time listener start")
    while True:
        now = datetime.now()
        seconds = now.second
        microseconds = now.microsecond
        fractional_seconds = microseconds / 1_000_000
        total_seconds = seconds + fractional_seconds
        if abs(total_seconds - sys_seconds) < 0.05:
            if bid:
                bid_help(price)
            else:
                first_bid_help()
            #print(f'bid confirm time: {now}')
        else:
            pass
            #print(f'current time: {now}')

def main():
    production = 0
    bid = 0
    if production:
        #time_process = Process(target=time_listener, args=(1,))
        #time_process.start()
        sys_time_process = Process(target=sys_time_listener, args=(59.50,))
        sys_time_process.start()
        bid_price_process = Process(target=bid_time_listener, args=(700,50,bid,))
        bid_price_process.start()
        price_process = Process(target=price_listener)
        price_process.start()
        key_process = Process(target=key_listener)
        key_process.start()
    else:
        delta = 0.1
        for i in range(60, 0, -10):
            exec(f"bid_price_process_{i} = Process(target=bid_time_listener, args=(9000,{i-7},bid,))\nbid_price_process_{i}.start()")
            exec(f"sys_time_process_{i} = Process(target=sys_time_listener, args=({i-delta},))\nsys_time_process_{i}.start()")
            delta += 0.1

if __name__ == '__main__':
    main()
