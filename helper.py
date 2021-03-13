from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def login(driver, email=None, password=None):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    email_elem = driver.find_element_by_id("username")
    email_elem.send_keys(email)

    password_elem = driver.find_element_by_id("password")
    password_elem.send_keys(password)
    password_elem.submit()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "profile-nav-item")))
