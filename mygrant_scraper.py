from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def login(driver):
    print("Logging in to MyGrant")
    load_dotenv()
    username = os.getenv('MYGRANT_USER')
    password = os.getenv('MYGRANT_PASS')
    try:
        wait = WebDriverWait(driver, 10)
        driver.get('https://www.mygrantglass.com/pages/login.aspx')
        wait.until(EC.presence_of_element_located((By.ID, 'ch_cus_LoginLink'))).click()
        user_input = wait.until(EC.presence_of_element_located((By.ID, 'clogin_TxtUsername')))
        pass_input = wait.until(EC.presence_of_element_located((By.ID, 'clogin_TxtPassword')))
        user_input.clear()
        pass_input.clear()
        user_input.send_keys(username)
        pass_input.send_keys(password)
        wait.until(EC.presence_of_element_located((By.ID, 'clogin_ButtonLogin'))).click()
    except Exception as e:
        print(f"Error: {e}")
        raise
    
def MyGrantScraper(partNo, driver, logger):

    url = 'https://www.mygrantglass.com/pages/search.aspx?q=' + partNo + '&sc=r&do=Search'
    parts = []
    try:
        logger.info("Searching part in MyGrant: " + partNo)
        driver.get(url)
        current_url = driver.current_url
        if current_url == 'https://www.mygrantglass.com/pages/login.aspx':
            login(driver)
            driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        try:
            div = soup.find('div', {'id': 'cpsr_DivParts'})
            locations = div.find_all('h3')[1:]
            tables = div.find_all('tbody')
            for table in tables:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    data = row.find_all('td')[1:]
                    part = [data[1].find('a').text.replace('\n', '').strip(), data[2].text.replace('\n', '').strip(), data[0].find('span').text.replace('\n', '').strip(), locations[0].text.split(' - ')[0].strip()]
                    parts.append(part)
                locations.pop(0)
            return parts    #[Part Number, Price, Availability, Location]
        except:
            print("not found")
            return None
    except:
        logger.error("Part number " + partNo + " not found on MyGrant")
        return None        
 