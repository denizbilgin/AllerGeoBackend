from places.services.vegetation_collector import IVegetationCollector
from typing import List, Dict, AnyStr, Union, TYPE_CHECKING
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
if TYPE_CHECKING:
    from places.models import Place


class PlantNet(IVegetationCollector):
    def __init__(self):
        super().__init__()

        # Driver settings
        self.plantnet_link = 'https://identify.plantnet.org/tr/prediction'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=Service("chromedriver/chromedriver.exe"), options=options)

    def get_data(self, place: "Place"):
        species = []

        self.driver.get(self.plantnet_link)
        # Search bar
        wait = WebDriverWait(self.driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.glass')))

        from ..models import District, City
        if isinstance(place, District):
            search_query = f"{place.name},{place.city.name},Türkiye"
        elif isinstance(place, City):
            search_query = f"{place.name},Türkiye"
        else:
            return {"TypeError": "Place can only be of type District or City."}

        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)

        time.sleep(1)

        # Search button
        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__nuxt"]/div/div/main/div[2]/div[1]/div/div/div/button')))
        search_button.click()

        # Species
        species_articles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article.species-card')))
        for article in species_articles:
            species_name = article.find_element(By.CSS_SELECTOR, 'h1.pn-species-name').text
            common_name_element = article.find_element(By.CLASS_NAME, "text-muted")
            common_name = common_name_element.text
            family_element = common_name_element.find_element(By.XPATH, "..").find_element(By.TAG_NAME, "a")
            family_link = family_element.get_attribute("href")
            family = family_element.text

            images = []
            image_elements = article.find_elements(By.TAG_NAME, "img")
            for image_element in image_elements:
                images.append(image_element.get_attribute("src"))

            gbif_link_element = article.find_element(By.XPATH, ".//a[contains(text(), 'GBIF')]")
            gbif_link = gbif_link_element.get_attribute("href")
            gbif_number_element = article.find_element(By.XPATH, ".//a[contains(text(), 'GBIF')]/following-sibling::*")
            gbif_number = int(gbif_number_element.text)

            species_data = {
                "species_name": species_name,
                "common_name": common_name,
                "family": {
                    "name": family,
                    "link": family_link
                },
                "images": images,
                "GBIF": {
                    "number": gbif_number,
                    "link": gbif_link
                }
            }
            species.append(species_data)
        return species

    def save(self, data: Union[List[Dict], Dict], filename: AnyStr):
        pass
