import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from abc import ABC, abstractmethod
import requests


class Data(ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def download():
        """Abstract static download method. Subclasses should implement this."""
        pass

    @staticmethod
    @abstractmethod
    def clean():
        """Abstract static clean method. Subclasses should implement this."""
        pass

class ContributionSearchResults(Data):
    # Class attribute for the download directory
    download_dir = "/workspaces/codespaces-jupyter/raw_data/contribution-search-results/2022/"

    @classmethod
    def download(cls):
        # Set up the download directory
        os.makedirs(ContributionSearchResults.download_dir, exist_ok=True)

        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": ContributionSearchResults.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
        })

        # Set up ChromeDriver
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=chrome_options)

        # Navigate to the page
        driver.get('http://app.toronto.ca/EFD/jsf/main/main.xhtml?campaign=17')
        wait = WebDriverWait(driver, 10)

        # Click 'Search Contributions'
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Search Contributions"]'))).click()

        # Click 'Submit' by ID
        wait.until(EC.element_to_be_clickable((By.ID, 'j_id_2h'))).click()

        # Click 'Export' by ID
        wait.until(EC.element_to_be_clickable((By.ID, 'exportLink'))).click()

        # Wait for the file to download
        file_path = wait_for_download(ContributionSearchResults.download_dir)
        if file_path is None:
            print("Download failed or timed out.")
            driver.quit()
            return

        # Close the browser
        driver.quit()
        return file_path

    @classmethod
    def clean(cls):
        df = pd.read_excel(ContributionSearchResults.download_dir,usecols="A:L", skiprows=range(7), engine="xlrd")
        df.columns = (
            df.columns.str.replace("\n", " ", regex=False)
            .str.replace("\s+", " ", regex=True)
            .str.replace(" */ *", "/", regex=True)
            .str.strip()
        )
        return df

class ElectionsResults(Data):

    @classmethod
    def download(cls):
        API_BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
        API_PACKAGE_SHOW_URL = API_BASE_URL + "/api/3/action/package_show"
        API_PACKAGE_ID = "election-results-official"

        def get_package():
            """Returns response from Toronto Open Data CKAN API"""

            params = {"id": API_PACKAGE_ID}
            package = requests.get(API_PACKAGE_SHOW_URL, params=params).json()

            return package
    
        package = get_package()

        resource_response = {}
        for resource in package["result"]["resources"]:
            resource_response[
                f"{resource['name']}.{resource['format'].lower()}"
            ] = requests.get(resource["url"])

        for resource, response in resource_response.items():
            with open(resource, "wb") as f:
                f.write(response.content)


    @classmethod
    def clean(cls):
        pass

def wait_for_download(directory, timeout=120):
    """
    Wait for a file to appear in the directory within the timeout period.
    Returns the path of the first file found in the directory.
    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        files = os.listdir(directory)
        if files:  # if there are files in the directory
            dl_wait = False
        seconds += 1
    if seconds == timeout:
        return None
    return os.path.join(directory, files[0])

# Run the download and clean methods
#downloaded_file_path = ContributionSearchResults.download()
#cleaned_data = ContributionSearchResults.clean()
#print(cleaned_data)

ElectionsResults.download()