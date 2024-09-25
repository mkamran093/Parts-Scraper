from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def searchPart(driver, partNo, logger):

    url = 'https://buypgwautoglass.com/PartSearch/search.asp?REG=&UserType=F&ShipToNo=85605&PB=544'
    try:
        print("Searching part in PWG: " + partNo)
        driver.get(url)
        # Wait for the element to be present
        wait = WebDriverWait(driver, 10)  

        type_select = wait.until(EC.presence_of_element_located((By.ID, "PartTypeA")))
        type_select.click()
        part_no_input = wait.until(EC.presence_of_element_located((By.ID, "PartNo")))

        # Send keys to the input field
        part_no_input.send_keys(partNo + Keys.RETURN)
        
        quote = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='btnQuote']")))
        if (quote.text == "Quotes"):
            quote.click()
            pin = wait.until(EC.presence_of_element_located((By.ID, "PinNumber")))
            pin.send_keys("1313" + Keys.RETURN)

        parts = []
        location = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='b2btext']"))).text.split(":: ")[1].strip()
        
        products = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))[2].find_elements(By.TAG_NAME, "tr")[2:]
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[@class='button check']"))).click()
        for product in products:
            part = []
            try:
                partName = product.find_elements(By.TAG_NAME, 'font')[1].text
                if (partNo in partName):
                    part.append(partName)
                    description = product.find_element(By.XPATH, "//div[@class='options']").text.replace('»', '').strip()
                    part.append(description)
                    try:
                        availability = product.find_element(By.XPATH, "//td[@ref-qty]").text
                        part.append(availability)
                    except NoSuchElementException:
                        part.append("Not available")
                    part.append(product.find_elements(By.TAG_NAME, 'font')[2].text)
                    part.append(location)
                    parts.append(part)
                else:
                    break
            except:
                continue
        
        ## Perfect above this line

        wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Check Other Locations')]"))).click()

        try:
            matching_table = driver.find_element(By.XPATH, "//table[.//td//span[contains(text(), 'Branch:: MIAMI FL')]]")
        except:
            logger.info("Parts for Miami not found")
            return parts

        products = matching_table.find_elements(By.TAG_NAME, "tr")[2:]
        for product in products:
            part = []
            try:
                data = product.find_elements(By.TAG_NAME, 'font')
                partName = data[2].text
                if (partNo in partName):
                    part.append(partName)
                    description = product.find_element(By.XPATH, "//div[@class='options']").text.replace('»', '').strip()
                    part.append(description)
                    try:
                        availability = data[1].text
                        part.append(availability)
                    except NoSuchElementException:
                        part.append("Not available")
                    part.append(data[3].text)
                    part.append("Miami FL")
                    parts.append(part)
            except:
                continue
        return parts   # [partnumber, description, availability, price, location]

    except TimeoutException:
        logger.error("No results found for the part number: " + partNo + " on PWG.")
        return None

def PWGScraper(partNo, driver, logger):

    try:
        result = searchPart(driver, partNo, logger)
        return result
    except:
        return None

if __name__ == "__main__":
    PWGScraper("DW01256")
