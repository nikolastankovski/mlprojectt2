from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime

import threading
import csv

class Browser:
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
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

class Arguments:
    def __init__(self) -> None:
        self.callbackFn = None
        self.base_url:str = None
        self.start_page:int = None
        self.end_page:int = None
        self.page_steps = None
        self.instance:int = None

def get_step_pages(no_of_pages, no_of_instances = 5):
    per_page = int(no_of_pages / no_of_instances)    
    
    if per_page == 0:
        per_page = no_of_pages

    pages = [i for i in range(0, no_of_pages, per_page)]

    groups = list()
    for i in range(len(pages)):
        current_page = pages[i] + 1
        next_page = None
        if i+1 >= len(pages):
            next_page = no_of_pages
        else:
            next_page = pages[i + 1]
        
        groups.append({"start_page": current_page, "end_page": next_page})
        
    return groups

def initiate_drivers(args:Arguments):
    scraper_arguments = []
    for item in args.page_steps:
        scraper_args = Arguments()
        scraper_args.start_page = item["start_page"]
        scraper_args.end_page = item["end_page"]
        scraper_args.base_url = args.base_url
        scraper_arguments.append(scraper_args)

    thread_list = []

    for i in range(len(scraper_arguments)):
        scraper_arguments[i].instance = i + 1
        thread_list.append(threading.Thread(target=args.callbackFn, args=[scraper_arguments[i]]))

    for i in range(len(thread_list)):
        thread_list[i].start()
        
def scrape_skinsort(args:Arguments):     
    browser = Browser()
    
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M")

    FILE_PATH = f'./Data/skinsort/ingredients_{current_datetime}_{args.start_page}_{args.end_page}.csv'
    
    with open(FILE_PATH, 'w', newline='', encoding="utf-8") as file:
        file.truncate()
        writer = csv.writer(file, delimiter=";")
        field = ["name", "synonym"]
        
        writer.writerow(field)
        
        for i in range(args.start_page, args.end_page + 1):
            page_no = i+1
            url = args.base_url + "/page/" + str(page_no)
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
    
    print(str(args.instance) + " end:", datetime.now())
    
    browser.quit()

def initiate_scraper_skinsort():
    BASE_ULR_SKINSORT = "https://skinsort.com/ingredients"
    
    browser = Browser()
    browser.go_to(BASE_ULR_SKINSORT)
    
    last_page_item = browser.find_element(".page-item:last-child a")
    no_of_pages = int(last_page_item.get_attribute("href").split("/")[-1])
    
    no_of_pages = 20
    
    browser.quit()

    print("Start: ", datetime.now())
    args = Arguments()
    args.callbackFn = scrape_skinsort
    args.page_steps = get_step_pages(no_of_pages)
    args.base_url = BASE_ULR_SKINSORT    
    
    initiate_drivers(args)

initiate_scraper_skinsort()