from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def IGCScraper(partNo, driver, logger):

    # if search_type == "Vehicle Type":
    #     parts = []
    #     driver.get('https://importglasscorp.com/lookup')
    #     wait = WebDriverWait(driver, 10)  # wait up to 10 seconds
    #     try:
    #         wait.until(EC.presence_of_element_located((By.ID, "make"))).send_keys(partNo["make"])
    #     except:
    #         logger.error("Make not found in IGC")
    #         return None
    #     try:
    #         wait.until(EC.presence_of_element_located((By.ID, "model"))).send_keys(partNo["model"])
    #     except:
    #         logger.error("Model not found in IGC")
    #         return None
    #     try:
    #         wait.until(EC.presence_of_element_located((By.ID, "data-year"))).click()
    #     except:
    #         logger.error("Year not found in IGC")
    #         return None
    #     try:
    #         links = wait.until(EC.presence_of_element_located((By.ID, "bodystyle_choices"))).find_elements(By.TAG_NAME, "a")
    #     except:
    #         logger.error("Body style not found in IGC")
    #         return None
        
    #     for link in links:
    #         link.click()
    #         all_items = wait.until(EC.presence_of_element_located((By.ID, "items")))
    #         types = all_items.find_element(By.TAG_NAME, "h4").text
    #         tables = all_items.find_elements(By.TAG_NAME, "table")
    #         for type, table in zip(types.split("\n"), tables):
    #             trs = tbody.find_elements(By.TAG_NAME, "tr")
    #             for tr in trs:
    #                 td_elements = tr.find_elements(By.TAG_NAME, 'td')
    #                 partNo = td_elements[0].text
    #                 description = td_elements[1].text
    #                 parts.append([partNo, description, type])

    #     print(parts)
    #     return parts

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
        return parts
    except:
        logger.error("Part number not found: " + partNo + " on IGC")
        return None