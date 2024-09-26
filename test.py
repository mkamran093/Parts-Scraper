import os
import time
import psutil
import logging
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to kill Chrome processes
def kill_chrome_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                proc.kill()
                logger.info(f"Killed Chrome process: {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.error(f"Error killing Chrome process: {e}")

# Set up Chrome driver
def setup_chrome_driver():
    try:
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-data-dir=C:\\Users\\NeXbit\\AppData\\Local\\Google\\Chrome\\User Data")
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = uc.Chrome(options=options)
        logger.info("Chrome driver set up successfully")
        return driver
    except Exception as e:
        logger.error(f"Error setting up Chrome driver: {e}")
        raise

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
        logger.error(f"Error: {e}")
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
            driver.implicitly_wait(10)
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

if __name__ == "__main__":
    kill_chrome_processes()
    driver = setup_chrome_driver()
    try:
        parts = PilkingtonScraper("DW01256", driver, logger)
        print(parts)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        driver.quit()
        kill_chrome_processes()