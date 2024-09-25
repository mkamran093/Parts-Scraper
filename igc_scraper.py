from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def IGCScraper(partNo, driver, logger):

    print("Searching part in IGC: " + partNo)   
    url = 'https://importglasscorp.com/glass/' + partNo
    try:
        # Navigate to the URL
        driver.get(url)
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