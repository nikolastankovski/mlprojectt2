from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

BASE_URL = "https://skinsort.com/ingredients"

driver = webdriver.Chrome()
driver.get(BASE_URL)

last_page_item = driver.find_element(By.CSS_SELECTOR, ".page-item:last-child a")
no_of_pages = int(last_page_item.get_attribute("href").split("/")[-1])


with open('./Data/ingredient_scraping.csv', 'w', newline='') as file:
    file.truncate()
    writer = csv.writer(file)
    field = ["name"]
    
    writer.writerow(field)
    
    for i in range(no_of_pages):
        page_no = i+1
        url = BASE_URL + "/page/" + str(page_no)
        driver.get(url)
            
        page_elems = driver.find_elements(By.CSS_SELECTOR, "#ingredients-table div > a")

        for el in page_elems:
            ingredient = str(el.get_attribute("href").split("/")[-1])
            writer.writerow([ingredient])
                    
    driver.quit()


# try:
#     element = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/tutorials']"))
#     )
#     print(element.text)
# except:
#     driver.quit()
# searchBar = driver.find_element(By.CLASS_NAME, "eNunqU")


# class Browser:   
#     def __init__(self, driver: str):
#         self.service = Service(driver)
#         self.browser = webdriver.Chrome(self.service)
        
#     def open_page(self, url: str):
#         self.browser.get(url=url)
        
#     def close_browser(self):
#         self.browser.close()
        
#     def find_element(self, by: Identifier)
#         if by == Identifier.CLASS
#             self.browser.fine
#         self.browser.find_element()

# ingredient_name = driver.find_element(By.CSS_SELECTOR, "#content div > h1").text.strip()
#             ingredient_synonyms = "N/A"
            
#             try:
#                 synonym_container = driver.find_element(By.CSS_SELECTOR, ".ingredient-description + div + div")
#                 synonym_icon = synonym_container.find_element(By.CSS_SELECTOR, "div")
                
#                 print("KLASA: " + synonym_icon.get_attribute("class"))
                
#                 time.sleep(2)
#                 # if(synonym_icon.get_attribute("class"))
#             except:
#                 continue