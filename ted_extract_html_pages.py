<<<<<<< HEAD
import time
import os
import re
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---

# !IMPORTANT! Set this to the path of your chromedriver.exe
# e.g., "chromedriver.exe" if it's in the same folder
CHROME_DRIVER_PATH = None 

# The search results page you provided
START_URL = "https://ted.europa.eu/en/search/result?FT=adalimumab&notice-type=can-standard%2Ccan-social%2Ccan-desg%2Ccan-tran&search-scope=ALL"

# Folder where all the HTML detail pages will be saved
OUTPUT_DIR = "ted_html_pages"

# Safety limit for pagination (961 results / 50 per page ≈ 20 pages)
MAX_PAGES_TO_SCRAPE = 30 
HEADLESS = True # Set to False to watch the browser work
PAGE_LOAD_TIMEOUT = 20 # seconds
DOWNLOAD_DELAY = 1.0 # seconds to pause between downloads

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Selenium Driver Helper ---

def make_driver(headless=HEADLESS):
    """
    Create Chrome webdriver with Selenium 4 syntax.
    """
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--log-level=3") # Suppress console noise

    try:
        if CHROME_DRIVER_PATH:
            service = Service(executable_path=CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=opts)
        else:
            logger.warning("CHROME_DRIVER_PATH is not set. Trying automatic driver.")
            driver = webdriver.Chrome(options=opts)
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        logger.error("Please ensure 'CHROME_DRIVER_PATH' is set correctly.")
        logger.error("And your 'chromedriver.exe' version matches your Chrome browser version.")
        return None
        
    driver.implicitly_wait(5)
    return driver

# --- File Saving Helper ---

def save_html_content(content: str, filepath: Path):
    """Saves string content to a file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved HTML: {filepath.name}")
    except Exception as e:
        logger.error(f"Failed to save file {filepath.name}: {e}")

# --- Main Scraper Function ---

def scrape_ted_website():
    """
    Main function to scrape the TED website.
    - Handles cookie banner
    - Paginates through results
    - Opens each detail link in a new tab
    - Saves the HTML of the detail page
    """
    
    # 1. Initialize Driver and Output Dir
    driver = make_driver(headless=HEADLESS)
    if not driver:
        return

    wait = WebDriverWait(driver, PAGE_LOAD_TIMEOUT)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    logger.info(f"WebDriver initialized. Output folder: {OUTPUT_DIR}")
    
    # 2. Go to Start URL and Handle Cookie Banner
    try:
        driver.get(START_URL)
        # Wait for the cookie banner and accept
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
        )
        cookie_button.click()
        logger.info("Cookie banner accepted.")
    except TimeoutException:
        logger.warning("Cookie banner not found or timed out. Continuing...")
    except Exception as e:
        logger.error(f"Error loading start page or handling cookies: {e}")
        driver.quit()
        return

    # 3. Pagination and Scraping Loop
    page_count = 1
    all_notice_ids = set()

    while page_count <= MAX_PAGES_TO_SCRAPE:
        logger.info(f"--- Processing Results Page {page_count} ---")
        
        try:
            # Wait for the result links to be present
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/notice/-/detail/']"))
            )
            time.sleep(1.0) # Give JS a moment to settle

            # Find all unique detail links on the current page
            links_on_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/notice/-/detail/']")
            hrefs = list(set([link.get_attribute("href") for link in links_on_page if link.get_attribute("href")]))
            
            if not hrefs:
                logger.warning("No detail links found on this page. Waiting...")
                time.sleep(5) # Wait longer, maybe page is slow
                links_on_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/notice/-/detail/']")
                hrefs = list(set([link.get_attribute("href") for link in links_on_page if link.get_attribute("href")]))
                if not hrefs:
                    logger.error("Still no links found. Breaking loop.")
                    break

            logger.info(f"Found {len(hrefs)} unique detail links on page {page_count}.")

            # 4. Loop through links and download HTML
            for href in hrefs:
                try:
                    # Extract notice ID for filename, e.g., "707393-2025"
                    match = re.search(r'/detail/([^/]+)', href)
                    if not match:
                        logger.warning(f"Could not parse notice ID from link: {href}")
                        continue
                    
                    notice_id = match.group(1)
                    
                    # Check if file already exists on disk (from previous runs)
                    filename = f"{notice_id}.html"
                    filepath = output_path / filename
                    if filepath.exists():
                        logger.info(f"File exists, skipping: {filename}")
                        all_notice_ids.add(notice_id) # Add to set to track for this run
                        continue

                    # Check if we've already seen this ID in *this* run (e.g., duplicate link on same page)
                    if notice_id in all_notice_ids:
                        logger.info(f"Already processed {notice_id} in this session, skipping.")
                        continue

                    # Open link in a new tab
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Wait for a key element on the detail page to load
                    wait.until(EC.presence_of_element_located((By.ID, "notice")))
                    
                    # Get page source and save
                    html_content = driver.page_source
                    save_html_content(html_content, filepath)
                    all_notice_ids.add(notice_id) # Add to set after successful save

                    time.sleep(DOWNLOAD_DELAY) # Be polite
                    
                    # Close the new tab and switch back
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    logger.error(f"Error processing detail page {href}: {e}")
                    # If something went wrong, close the extra tab if it's still open
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

            # 5. Find and click the "Next" button
            logger.info("Looking for 'Next Page' button...")
            # Updated selector based on user-provided HTML for the <button> element
            next_button_selector = (By.CSS_SELECTOR, "button[aria-label='Go to the next page']")
            next_button = wait.until(
                EC.element_to_be_clickable(next_button_selector)
            )
            
            # Check if the button is disabled (it will have a 'disabled' attribute)
            if next_button.get_attribute("disabled") is not None:
                logger.info("Next button is disabled. Reached the last page.")
                break
            
            # --- FIX for ElementClickInterceptedException ---
            # Scroll to the element and use JavaScript click to avoid interception
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5) # Wait for scroll
                driver.execute_script("arguments[0].click();", next_button)
                logger.info("Clicked 'Next Page' using JavaScript.")
            except Exception as click_err:
                logger.error(f"Failed to click 'Next Page' button even with JS: {click_err}")
                break
            # --- END FIX ---
                
            page_count += 1
            time.sleep(2.0) # Wait for page transition

        except (TimeoutException, NoSuchElementException):
            logger.info("No 'Next Page' button found or timed out. Assuming end of results.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred on page {page_count}: {e}")
            break

    # 6. Clean up
    driver.quit()
    logger.info(f"Scraping complete. Total pages: {page_count-1}. Total unique notices: {len(all_notice_ids)}.")

if __name__ == "__main__":
    scrape_ted_website()

=======
import time
import os
import re
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- Configuration ---

# !IMPORTANT! Set this to the path of your chromedriver.exe
# e.g., "chromedriver.exe" if it's in the same folder
CHROME_DRIVER_PATH = None 

# The search results page you provided
START_URL = "https://ted.europa.eu/en/search/result?FT=adalimumab&notice-type=can-standard%2Ccan-social%2Ccan-desg%2Ccan-tran&search-scope=ALL"

# Folder where all the HTML detail pages will be saved
OUTPUT_DIR = "ted_html_pages"

# Safety limit for pagination (961 results / 50 per page ≈ 20 pages)
MAX_PAGES_TO_SCRAPE = 30 
HEADLESS = True # Set to False to watch the browser work
PAGE_LOAD_TIMEOUT = 20 # seconds
DOWNLOAD_DELAY = 1.0 # seconds to pause between downloads

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- Selenium Driver Helper ---

def make_driver(headless=HEADLESS):
    """
    Create Chrome webdriver with Selenium 4 syntax.
    """
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--log-level=3") # Suppress console noise

    try:
        if CHROME_DRIVER_PATH:
            service = Service(executable_path=CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=opts)
        else:
            logger.warning("CHROME_DRIVER_PATH is not set. Trying automatic driver.")
            driver = webdriver.Chrome(options=opts)
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        logger.error("Please ensure 'CHROME_DRIVER_PATH' is set correctly.")
        logger.error("And your 'chromedriver.exe' version matches your Chrome browser version.")
        return None
        
    driver.implicitly_wait(5)
    return driver

# --- File Saving Helper ---

def save_html_content(content: str, filepath: Path):
    """Saves string content to a file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved HTML: {filepath.name}")
    except Exception as e:
        logger.error(f"Failed to save file {filepath.name}: {e}")

# --- Main Scraper Function ---

def scrape_ted_website():
    """
    Main function to scrape the TED website.
    - Handles cookie banner
    - Paginates through results
    - Opens each detail link in a new tab
    - Saves the HTML of the detail page
    """
    
    # 1. Initialize Driver and Output Dir
    driver = make_driver(headless=HEADLESS)
    if not driver:
        return

    wait = WebDriverWait(driver, PAGE_LOAD_TIMEOUT)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    logger.info(f"WebDriver initialized. Output folder: {OUTPUT_DIR}")
    
    # 2. Go to Start URL and Handle Cookie Banner
    try:
        driver.get(START_URL)
        # Wait for the cookie banner and accept
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
        )
        cookie_button.click()
        logger.info("Cookie banner accepted.")
    except TimeoutException:
        logger.warning("Cookie banner not found or timed out. Continuing...")
    except Exception as e:
        logger.error(f"Error loading start page or handling cookies: {e}")
        driver.quit()
        return

    # 3. Pagination and Scraping Loop
    page_count = 1
    all_notice_ids = set()

    while page_count <= MAX_PAGES_TO_SCRAPE:
        logger.info(f"--- Processing Results Page {page_count} ---")
        
        try:
            # Wait for the result links to be present
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/notice/-/detail/']"))
            )
            time.sleep(1.0) # Give JS a moment to settle

            # Find all unique detail links on the current page
            links_on_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/notice/-/detail/']")
            hrefs = list(set([link.get_attribute("href") for link in links_on_page if link.get_attribute("href")]))
            
            if not hrefs:
                logger.warning("No detail links found on this page. Waiting...")
                time.sleep(5) # Wait longer, maybe page is slow
                links_on_page = driver.find_elements(By.CSS_SELECTOR, "a[href*='/notice/-/detail/']")
                hrefs = list(set([link.get_attribute("href") for link in links_on_page if link.get_attribute("href")]))
                if not hrefs:
                    logger.error("Still no links found. Breaking loop.")
                    break

            logger.info(f"Found {len(hrefs)} unique detail links on page {page_count}.")

            # 4. Loop through links and download HTML
            for href in hrefs:
                try:
                    # Extract notice ID for filename, e.g., "707393-2025"
                    match = re.search(r'/detail/([^/]+)', href)
                    if not match:
                        logger.warning(f"Could not parse notice ID from link: {href}")
                        continue
                    
                    notice_id = match.group(1)
                    
                    # Check if file already exists on disk (from previous runs)
                    filename = f"{notice_id}.html"
                    filepath = output_path / filename
                    if filepath.exists():
                        logger.info(f"File exists, skipping: {filename}")
                        all_notice_ids.add(notice_id) # Add to set to track for this run
                        continue

                    # Check if we've already seen this ID in *this* run (e.g., duplicate link on same page)
                    if notice_id in all_notice_ids:
                        logger.info(f"Already processed {notice_id} in this session, skipping.")
                        continue

                    # Open link in a new tab
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Wait for a key element on the detail page to load
                    wait.until(EC.presence_of_element_located((By.ID, "notice")))
                    
                    # Get page source and save
                    html_content = driver.page_source
                    save_html_content(html_content, filepath)
                    all_notice_ids.add(notice_id) # Add to set after successful save

                    time.sleep(DOWNLOAD_DELAY) # Be polite
                    
                    # Close the new tab and switch back
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    logger.error(f"Error processing detail page {href}: {e}")
                    # If something went wrong, close the extra tab if it's still open
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

            # 5. Find and click the "Next" button
            logger.info("Looking for 'Next Page' button...")
            # Updated selector based on user-provided HTML for the <button> element
            next_button_selector = (By.CSS_SELECTOR, "button[aria-label='Go to the next page']")
            next_button = wait.until(
                EC.element_to_be_clickable(next_button_selector)
            )
            
            # Check if the button is disabled (it will have a 'disabled' attribute)
            if next_button.get_attribute("disabled") is not None:
                logger.info("Next button is disabled. Reached the last page.")
                break
            
            # --- FIX for ElementClickInterceptedException ---
            # Scroll to the element and use JavaScript click to avoid interception
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5) # Wait for scroll
                driver.execute_script("arguments[0].click();", next_button)
                logger.info("Clicked 'Next Page' using JavaScript.")
            except Exception as click_err:
                logger.error(f"Failed to click 'Next Page' button even with JS: {click_err}")
                break
            # --- END FIX ---
                
            page_count += 1
            time.sleep(2.0) # Wait for page transition

        except (TimeoutException, NoSuchElementException):
            logger.info("No 'Next Page' button found or timed out. Assuming end of results.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred on page {page_count}: {e}")
            break

    # 6. Clean up
    driver.quit()
    logger.info(f"Scraping complete. Total pages: {page_count-1}. Total unique notices: {len(all_notice_ids)}.")

if __name__ == "__main__":
    scrape_ted_website()

>>>>>>> 5b89986e5e996b4c2c9a202facdcdf6dd203f83b
