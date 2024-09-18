import streamlit as st
from igc_scraper import IGCScraper
from pwg_scraper import PWGScraper
from pilkington_scraper import PilkingtonScraper
from mygrant_scraper import MyGrantScraper
import psutil
import pandas as pd
import logging
import undetected_chromedriver as uc
import traceback

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

def create_table_with_cart_button(data, headers):
    try:
        df = pd.DataFrame(data, columns=headers)
        df['Add to Cart'] = ['Add' for _ in range(len(df))]
        
        html = df.to_html(escape=False, index=False)
        html = html.replace('<td>Add</td>', '<td><button style="background-color: #4CAF50; color: white; border: none; padding: 5px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 12px; margin: 4px 2px; cursor: pointer;">Add to Cart</button></td>')
        
        return html
    except Exception as e:
        logger.error(f"Error creating table with cart button: {e}")
        return f"<p>Error creating table: {str(e)}</p>"

def run_scraper(scraper_func, input_text, driver, scraper_name):
    try:
        logger.info(f"Starting {scraper_name} scraper")
        data = scraper_func(input_text, driver, logger)
        logger.info(f"{scraper_name} scraper completed successfully")
        return data
    except Exception as e:
        logger.error(f"Error in {scraper_name} scraper: {e}")
        logger.error(traceback.format_exc())
        return [["Error", f"Failed to fetch data from {scraper_name}: {str(e)}"]]

def main():
    st.title("Parts Scraper")

    try:
        kill_chrome_processes()
        driver = setup_chrome_driver()

        with st.form(key='my_form'):
            user_input = st.text_input(label='Enter part number')
            submit_button = st.form_submit_button(label='Search')

        if submit_button:
            with st.spinner("Fetching data..."):
                scrapers = [
                    (PWGScraper, "PWG", ["Part Name", "Description", "Availability", "Price", "Location"]),
                    (IGCScraper, "IGC", ["Part Number", "Price", "Availability", "Location"]),
                    (PilkingtonScraper, "Pilkington", ["Part Number", "Description", "Price", "Location"]),
                    (MyGrantScraper, "MyGrant", ["Part Number", "Price", "Availability", "Location"])
                ]

                for scraper_func, name, headers in scrapers:
                    data = run_scraper(scraper_func, user_input, driver, name)
                    st.subheader(f"{name} Results")
                    html = create_table_with_cart_button(data, headers)
                    st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Unexpected error in main function: {e}")
        logger.error(traceback.format_exc())
        st.error(f"An unexpected error occurred: {str(e)}")

    finally:
        if 'driver' in locals():
            driver.quit()
            logger.info("Chrome driver closed")

if __name__ == "__main__":
    main()