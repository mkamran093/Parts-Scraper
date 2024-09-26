import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def login(driver):
    print("Logging in to Pilkington website")
    load_dotenv()
    username = os.getenv('PIL_USER')
    password = os.getenv('PIL_PASS')
    try:
        wait = WebDriverWait(driver, 10)
        user_input = wait.until(EC.presence_of_element_located((By.ID, 'username')))
        pass_input = wait.until(EC.presence_of_element_located((By.ID, 'password')))
        driver.implicitly_wait(10)
        user_input.send_keys(username)
        pass_input.send_keys(password)
        wait.until(EC.presence_of_element_located((By.ID, 'cbTerms'))).click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'button'))).click()
    except Exception as e:
        raise
    
def PilkingtonScraper(partNo, driver, logger):

    url = 'https://shop.pilkington.com/ecomm/search/basic/?queryType=2&query=' + partNo + '&inRange=true&page=1&pageSize=30&sort=PopularityRankAsc'
    try:
        # Navigate to the URL
        logger.info("Searching part in Pilkington: " + partNo)
        driver.get(url)
        wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
        
        if ('https://identity.pilkington.com/identityexternal/login?signin=' in driver.current_url):
            login(driver)
            driver.get(url)

        try:
            window = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@uib-modal-window='modal-window']")))
            driver.implicitly_wait(10)
            cross = window.find_element(By.XPATH, "//button[@class='close']")
            cross.click()
        except:
            pass

        try:
            # Wait for the element to be present
            time.sleep(2)
            part_no = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-if='!perm.canViewProdDetails']"))).text
            part_name = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='description']"))).text
            price = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='amount']"))).text
            location = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-if='!allowChoosePlant']"))).text
            
            if partNo in part_no:
                return [[part_no, part_name, price, location]]
            return None
        except NoSuchElementException:
            logger.error("Part number not found: " + partNo + " on Pilkington")
            return None

    except:
        logger.error("Part number not found: " + partNo + " on Pilkington")
        return None