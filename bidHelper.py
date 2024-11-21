from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
from datetime import datetime, timedelta
from pynput import keyboard
import threading
import os

url = os.environ['URL']

class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def find_element(self, by, value):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                return self.driver.find_element(by, value)
            except (NoSuchElementException, StaleElementReferenceException):
                print(f"Attempt {attempt+1}: Failed to find or interact with element {by} = {value}")
                if attempt < max_attempts - 1:  # Don't sleep after the last attempt
                    time.sleep(0.1)  # Wait for 1 second
                else:
                    return None

    @property
    def deadline_time(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[1]/span[4]/span[2]')
        if element is not None:
            deadline_time_str = element.text # "14:38"
            return datetime.strptime(deadline_time_str, "%H:%M").time()
        return None
    @property
    def current_time(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/span[2]/span')
        if element is not None:
            current_time_str = element.text # "13:01:55"
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
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[1]/div[1]/span/span')
        if element is not None:
            return element.text
        return None
    @property
    def current_price(self):
        element = self.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div/div[2]/span[3]/span')
        if element is not None:
            return element.text
        return None

# Setup chrome options
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:8000")

# Choose Chrome Browser
driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get(url)

# Instantiate LoginPage
login_page = LoginPage(driver)

# Extract the deadline
deadline_time = None
while deadline_time is None:
    deadline_time = login_page.deadline_time
print(deadline_time)

# 定义键盘监听事件
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

def time_listener(start_seconds, end_seconds, add_price):
    while True:
        current_time = login_page.current_time
        print(current_time)
        if current_time is None:
            continue
        # Calculate the difference between deadline and current time
        time_difference = datetime.combine(datetime.today(), deadline_time) - datetime.combine(datetime.today(), current_time)
        print(time_difference)
    
        if time_difference <= timedelta(seconds=start_seconds):
            print("time listener start 1")
            break
    
        # Sleep for a while before checking the time again
        time.sleep(0.1)

    print("time listener start 2")

    # Set add price
    login_page.set_add_price(add_price)

    # Increase price
    login_page.increase_price()

    # Bid
    login_page.bid()

    # Edit verification code
    login_page.edit_verification_code()

    # Print bid price
    bid_price = None
    while bid_price is None:
        bid_price = login_page.bid_price
    print(bid_price)

    while True:
        time.sleep(0.1)
        current_time = login_page.current_time
        print(current_time)
        if current_time is None:
            continue
        # Calculate the difference between deadline and current time
        time_difference = datetime.combine(datetime.today(), deadline_time) - datetime.combine(datetime.today(), current_time)
        print(time_difference)

        current_price = login_page.current_price
        print(current_price)
        if current_price is None:
            continue

        if time_difference <= timedelta(seconds=end_seconds):
            time.sleep(0.6)
            print("time listener stop 1")
            print(current_time)
            break

        if (abs(int(bid_price) - int(current_price))) <= 300:
            print("price listener stop 1")
            break

    print("listener stop")
    # Confirm verification code
    login_page.confirm_verification_code()


# Create and start a new thread for the time listener
time_thread = threading.Thread(target=time_listener, args=(10, 2, 700))
time_thread.start()

key_thread = threading.Thread(target=key_listener)
key_thread.start()
