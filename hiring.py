import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# **Chrome Options**
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# **Initialize WebDriver**
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # **Login**
    driver.get("https://account.ycombinator.com/?continue=https%3A%2F%2Fwww.workatastartup.com%2Fapplication&defaults%5BsignUpActive%5D=true")
    time.sleep(5)

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "MuiTypography-root.MuiLink-root.MuiLink-underlineHover.MuiLink-button.MuiTypography-colorPrimary"))
    )
    login_button.click()
    time.sleep(5)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ycid-input"))).send_keys("username")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password-input"))).send_keys("password")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Log in')]"))).click()

    time.sleep(10)

    # Navigate to Companies Page
    driver.get("https://www.workatastartup.com/companies")
    time.sleep(5)  

    # **Auto-scroll to load all companies**
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    print("Scrolling done")

    # Extract Company Names + links
    companies_data = []
    company_elements = driver.find_elements(By.CSS_SELECTOR, "div.text-2xl.font-medium a")

    for company in company_elements:
        try:
            company_name = company.find_element(By.CSS_SELECTOR, "span.company-name").text.strip()
            company_link = company.get_attribute("href")
            companies_data.append([company_name, company_link, "N/A", "N/A"])
            print(f" Saved {company_name} - {company_link}")
        except Exception as e:
            print(f"Error : {e}")

        time.sleep(1)

    # Extract Hiring Details
    for company in companies_data:
        driver.get(company[1])
        time.sleep(3)

        try:
            founder_div = driver.find_element(By.CLASS_NAME, "mb-1.font-medium")
            founder_name = founder_div.text.strip()
            linkedin = founder_div.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            founder_name = "N/A"
            linkedin = "N/A"

        company[2] = founder_name
        company[3] = linkedin
        print(f" Processed {company[0]} - Founder: {founder_name}")

    # Generate Unique Filename 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"startup_jobs_{timestamp}.xlsx"

    # **Save to Excel**
    df = pd.DataFrame(companies_data, columns=["Company Name", "Company Link", "Founder Name", "LinkedIn"])
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f" Data saved!")

except Exception as e:
    print(f" Error: {e}")

finally:
    driver.quit()
