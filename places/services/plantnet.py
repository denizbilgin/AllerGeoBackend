from places.services.vegetation_collector import IVegetationCollector
from typing import List, Dict, TYPE_CHECKING, cast
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils.timezone import now

if TYPE_CHECKING:
    from places.models import Place, Vegetation


class PlantNet(IVegetationCollector):
    def __init__(self, vegetation_durability_days: int = 60, selenium_timeout_time: int = 15):
        super().__init__()
        self.vegetation_durability_days = vegetation_durability_days
        self.selenium_timeout_time = selenium_timeout_time

        # Driver settings
        self.plantnet_link = 'https://identify.plantnet.org/tr/prediction'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=Service("chromedriver/chromedriver.exe"), options=options)

    def get_data(self, place: "Place") -> List["Vegetation"]:
        from ..models import District, City, DistrictVegetation, CityVegetation
        is_city = isinstance(place, City)
        model = CityVegetation if is_city else DistrictVegetation
        filter_kwargs = {"city" if is_city else "district": place}

        # Looking for old data
        vegetation: Vegetation = model.objects.filter(**filter_kwargs).first()
        if vegetation:
            if vegetation.last_update_date + timedelta(days=self.vegetation_durability_days) >= now():
                return model.objects.filter(**filter_kwargs).values()

            # Deleting old values
            model.objects.filter(**filter_kwargs).delete()

        species = []

        self.driver.get(self.plantnet_link)

        # Search bar
        wait = WebDriverWait(self.driver, self.selenium_timeout_time)
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.glass')))

        # Defining search query
        if is_city:
            search_query = f"{place.name},Türkiye"
        else:
            place = cast(District, place)
            search_query = f"{place.name},{place.city.name},Türkiye"

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

        self.save(species, is_city, place)
        return model.objects.filter(**filter_kwargs).values()

    def save(self, data: List[Dict], is_city: bool, place: "Place"):
        from ..models import DistrictVegetation, CityVegetation
        model = CityVegetation if is_city else DistrictVegetation
        instances = []
        place_field = "city" if is_city else "district"

        for item in data:
            instances.append(model(
                species_name=item["species_name"],
                common_name=item["common_name"],
                family_name=item["family"]["name"],
                family_link=item["family"]["link"],
                images=";".join(item["images"]),
                gbif_number=item["GBIF"]["number"],
                gbif_link=item["GBIF"]["link"],
                last_update_date=now(),
                **{place_field: place}
            ))
        model.objects.bulk_create(instances, ignore_conflicts=True)

# TODO: Alerjenler ile Vegetation şuan aynı şeyi yapıyor neredeyse