from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def PilkingtonScraper(partNo, driver, logger):

    url = 'https://shop.pilkington.com/ecomm/search/basic/?queryType=2&query=' + partNo + '&inRange=true&page=1&pageSize=30&sort=PopularityRankAsc'
    try:
        # Navigate to the URL
        logger.info("Searching part in Pilkington: " + partNo)
        driver.get(url)
        
        try:
            # Wait for the element to be present
            wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
            part_no = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-if='!perm.canViewProdDetails']"))).text
            part_name = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='description']"))).text
            price = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='amount']"))).text
            location = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-if='!allowChoosePlant']"))).text
            
            return [[part_no, part_name, price, location]]
        except NoSuchElementException:
            logger.error("Part number not found: " + partNo + " on Pilkington")
            return None

    except:
        logger.error("Part number not found: " + partNo + " on Pilkington")
        return None