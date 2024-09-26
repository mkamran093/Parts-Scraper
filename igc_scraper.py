from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

def login(driver):
    print("Logging in to Import Glass Corp")
    load_dotenv()
    username = os.getenv('IGC_USER')
    password = os.getenv('IGC_PASS')
    cn = os.getenv('IGC_CN')
    try:
        wait = WebDriverWait(driver, 10)
        driver.get('https://importglasscorp.com')
        user_input = wait.until(EC.presence_of_element_located((By.ID, 'email-address')))
        cn_input = wait.until(EC.presence_of_element_located((By.ID, 'customer-number')))
        pass_input = wait.until(EC.presence_of_element_located((By.ID, 'password')))
        user_input.clear()
        cn_input.clear()
        pass_input.clear()
        user_input.send_keys(username)
        cn_input.send_keys(cn)
        pass_input.send_keys(password)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'button'))).click()
    except Exception as e:
        print(f"Error: {e}")
        raise
    
def IGCScraper(partNo, driver, logger):

    print("Searching part in IGC: " + partNo)   
    url = 'https://importglasscorp.com/glass/' + partNo
    try:
        # Navigate to the URL
        driver.get(url)
        try:
            driver.find_element(By.ID, "banner")
            login(driver)
            driver.get(url)
        except:
            pass
        parts = []
        # Wait for the tables to be present
        wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        location = table.find_element(By.XPATH, "./preceding-sibling::*[1]").find_element(By.TAG_NAME, 'b').text
        if location != "Opa-Locka":
            logger.info("Part not available in Opa-Locka")
            return None

        tbody = table.find_element(By.TAG_NAME, "tbody")
        try:
            trs = tbody.find_elements(By.TAG_NAME, "tr")
        except:
            return None

        for tr in trs:
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            first_value = td_elements[0].find_element(By.TAG_NAME, 'a').text  # 1st value
            if (partNo not in first_value):
                continue
            fourth_value = td_elements[3].find_element(By.TAG_NAME, 'b').text  # 4th value
            if td_elements[4].text == "In Stock":
                fifth_value = "Yes"
            else:
                fifth_value = "No"  
            parts.append([first_value, fourth_value, fifth_value, location])
        return parts   # [Part Number, Price, Availability,	Location]
    except:
        logger.error("Part number not found: " + partNo + " on IGC")
        return None