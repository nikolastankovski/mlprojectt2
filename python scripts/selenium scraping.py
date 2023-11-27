from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time
import threading
import csv


class Browser:
    def __init__(self) -> None:
        self.browser = webdriver.Chrome()

    def go_to(self, url:str):
        self.browser.get(url)
        
    def quit(self):
        self.browser.quit()
        
    def find_element(self, selector: str, parent: WebElement = None):
        try:
            if parent == None:    
                return self.browser.find_element(By.CSS_SELECTOR, selector)
            else:
                return parent.find_element(By.CSS_SELECTOR, selector)
        except:
            return None
        
    def find_elements(self, selector: str, parent: WebElement = None):
        try:
            if parent == None:    
                return self.browser.find_elements(By.CSS_SELECTOR, selector)
            else:
                return parent.find_elements(By.CSS_SELECTOR, selector)
        except:
            return []


def scrape_Skinsort():
    BASE_ULR_SKINSORT = "https://skinsort.com/ingredients"
    
    browser = Browser()
    browser.go_to(BASE_ULR_SKINSORT)
    
    last_page_item = browser.find_element(".page-item:last-child a")
    no_of_pages = int(last_page_item.get_attribute("href").split("/")[-1])
    
    with open('./Data/ingredient_w_synonyms.csv', 'w', newline='',encoding="utf-8") as file:
        file.truncate()
        writer = csv.writer(file, delimiter=";")
        field = ["name", "synonym"]
        
        writer.writerow(field)
        
        for i in range(no_of_pages):
            page_no = i+1
            url = BASE_ULR_SKINSORT + "/page/" + str(page_no)
            browser.go_to(url)
                
            page_elems = browser.find_elements("#ingredients-table div > a")

            ingredient_urls = [el.get_attribute("href") for el in page_elems]

            for url in ingredient_urls:
                browser.go_to(url)
                
                ingredient_name = browser.find_element("#content div > h1").text.strip()
                ingredient_synonyms = "N/A"
                
                try:
                    synonym_container = browser.find_element(".ingredient-description + div + div")
                    synonym_icon = browser.find_element("div", synonym_container)
                    
                    el_classes = synonym_icon.get_attribute("class").split(" ")
                    
                    if("bg-emerald-100" in el_classes):
                        ingredient_synonyms = str(browser.find_element("p", synonym_container).text.split("\n")[1])
                finally:
                    writer.writerow([ingredient_name, ingredient_synonyms])
                        
        browser.quit()
   

def test():
    def test_logic():
        driver = webdriver.Chrome()
        url = 'https://www.google.co.in'
        driver.get(url)
        # Implement your test logic
        time.sleep(2)
        driver.quit()

    N = 5   # Number of browsers to spawn
    thread_list = list()

    # Start test
    for i in range(N):
        t = threading.Thread(name='Test {}'.format(i), target=test_logic)
        t.start()
        time.sleep(1)
        print(t.name + ' started!')
        thread_list.append(t)

    # Wait for all threads to complete
    for thread in thread_list:
        thread.join()

    print('Test completed!')


def test1():
    import pubchempy as pcp

    results = pcp.get_compounds('Niacinamide', 'name')

    if results:
        compound = results[0]
        synonyms = compound.synonyms
        print("Synonyms for Niacinamide ", synonyms)
    else:
        print("Compound not found in PubChem.")
        
test1()
#scrape_Skinsort()