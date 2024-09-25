import json
from igc_scraper import IGCScraper
from pwg_scraper import PWGScraper
from pilkington_scraper import PilkingtonScraper
from mygrant_scraper import MyGrantScraper
import psutil
import logging
import undetected_chromedriver as uc

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
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = uc.Chrome(options=options)
        logger.info("Chrome driver set up successfully")
        return driver
    except Exception as e:
        logger.error(f"Error setting up Chrome driver: {e}")
        raise


def runScraper(partNo):

    kill_chrome_processes()
    driver = setup_chrome_driver()

    igc_data = IGCScraper(partNo, driver, logger)   # returns a list of lists with this data [Part Number, Price, Availability,	Location, Add to Cart]
    pwg_data = PWGScraper(partNo, driver, logger)   # returns a list of lists with this data [partnumber, description, availability, price, location]
    pilkington_data = PilkingtonScraper(partNo, driver, logger)  # returns this list [[part_no, part_name, price, location]]
    mygrant_data = MyGrantScraper(partNo, driver, logger)  # returns a list of lists with this data [Part Number, Price, Availability,	Location]

    driver.quit()

    # Define keys for each type of data
    igc_keys = ["Part Number", "Price", "Availability", "Location"]
    pwg_keys = ["Part Number", "Description", "Availability", "Price", "Location"]
    pilkington_keys = ["Part Number", "Part Name", "Price", "Location"]
    mygrant_keys = ["Part Number", "Price", "Availability", "Location"]

    # Convert lists to dictionaries
    igc_data_dicts = [dict(zip(igc_keys, item)) for item in igc_data] if igc_data else {}
    pwg_data_dicts = [dict(zip(pwg_keys, item)) for item in pwg_data] if pwg_data else {}
    pilkington_data_dicts = [dict(zip(pilkington_keys, item)) for item in pilkington_data] if pilkington_data else {}
    mygrant_data_dicts = [dict(zip(mygrant_keys, item)) for item in mygrant_data] if mygrant_data else {}

    # Combine all data into a single dictionary
    combined_data = {
        "IGC": igc_data_dicts,
        "PWG": pwg_data_dicts,
        "Pilkington": pilkington_data_dicts,
        "MyGrant": mygrant_data_dicts
    }

    combined_json = json.dumps(combined_data, indent=4)

    return combined_json
    
# if __name__ == '__main__':
#     runScraper('DW01256')