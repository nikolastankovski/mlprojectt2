from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

from datetime import datetime as dt
import threading
import csv
import os
import logging
import re

#region FOLDERS
CURRENT_DIR = os.getcwd()
SKINSORT_SAVE_FOLDER = os.path.join(CURRENT_DIR, "Data\skinsort")  
SCRAPING_LOGS = os.path.join(CURRENT_DIR, "Scraping\logs")

try:
    os.makedirs(SKINSORT_SAVE_FOLDER)
except:
    None
    
try:
    os.makedirs(SCRAPING_LOGS)
except:
    None
#endregion

#region LOGGER
current_date = dt.now().strftime("%Y%m%d")
LOG_FILE_PATH = os.path.join(SCRAPING_LOGS, f"log_{current_date}.log")

logging.basicConfig(filename=LOG_FILE_PATH, format='%(asctime)s;%(message)s', filemode='w')
logger = logging.getLogger()
#endregion

class Browser:
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.browser = webdriver.Chrome(options=options)

    def go_to(self, url:str):
        self.browser.get(url)
        
    def quit(self):
        self.browser.quit()
        
    def find_element(self, selector: str, parent: WebElement = None):
        try:
            if parent == None:   
                return WebDriverWait(self.browser, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
            else:
                return parent.find_element(By.CSS_SELECTOR, selector)
        except:
            return None
        
    def find_elements(self, selector: str, parent: WebElement = None):
        try:
            if parent == None:    
                #return self.browser.find_elements(By.CSS_SELECTOR, selector)
                return WebDriverWait(self.browser, 10).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
            else:
                return parent.find_elements(By.CSS_SELECTOR, selector)
        except:
            return []

class Arguments:
    def __init__(self, callbackFn = None, base_url:str = None, start_page:int = None, end_page:int = None, page_steps = None, instance:int = None, folder_path:str = None) -> None:
        self.callbackFn = callbackFn
        self.base_url:str = base_url
        self.start_page:int = start_page
        self.end_page:int = end_page
        self.page_steps = page_steps
        self.instance:int = instance
        self.folder_path:str = folder_path
        
def merge_files(folder_path:str):     
    files_to_merge = os.listdir(folder_path)
    
    df_concat = pd.concat([pd.read_csv(f'{folder_path}/{file}', sep=";") for file in files_to_merge])
            
    df_concat.to_csv(f"{folder_path}/merged_ingredients.csv", index=False, sep=";") 

def get_step_pages(no_of_pages, no_of_instances = 6):
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
    print("Start: ", dt.now())
    
    scraper_arguments = []
    for item in args.page_steps:
        scraper_arguments.append(Arguments(
            start_page = item["start_page"],
            end_page = item["end_page"],
            base_url = args.base_url,
            folder_path = args.folder_path,
        ))
        
    thread_list = []

    instance = 0
    for s_args in scraper_arguments:
        s_args.instance = (instance + 1)
        thread_list.append(threading.Thread(target=args.callbackFn, args=[s_args]))

    for t in thread_list:
       t.start()
    
    for t in thread_list:
       t.join()
    
    merge_files(args.folder_path)
    print("End: ", dt.now())
        
def scrape_skinsort(args:Arguments):     
    browser = Browser()
    
    FILE_PATH = os.path.join(args.folder_path, f"ingredients_{args.start_page}_{args.end_page}.csv")
    
    with open(FILE_PATH, 'w', newline='', encoding="utf-8") as file:
        file.truncate()
        writer = csv.writer(file, delimiter=";")
        field = ["page_number", "name", "synonym"]
        
        writer.writerow(field)
        
        for page_no in range(args.start_page, args.end_page + 1):
            url = args.base_url + "/page/" + str(page_no)
            browser.go_to(url)
                
            page_elems = browser.find_elements("#ingredients-table div > a")

            ingredient_urls = [el.get_attribute("href") for el in page_elems]

            for url in ingredient_urls:
                browser.go_to(url)
                
                ingredient_name = None if browser.find_element("#content div > h1") == None else browser.find_element("#content div > h1").text.strip()
                ingredient_synonyms = None
                
                try:                    
                    synonym_container = browser.find_element(".ingredient-description + div + div")
                    synonym_icon = browser.find_element("div", synonym_container)
                    
                    el_classes = synonym_icon.get_attribute("class").split(" ")
                    
                    if("bg-emerald-100" in el_classes):
                        ingredient_synonyms = str(browser.find_element("p", synonym_container).text.split("\n")[1])
                        ingredient_synonyms = re.sub(r'(?<=\d),\s+(?=\d)', ",", ingredient_synonyms)
                        ingredient_synonyms = ingredient_synonyms.replace(", ","|").replace(" and ", "|").replace("and ", "")
                    else:
                        ingredient_synonyms = ingredient_name                 
                    
                except Exception as e:
                    logger.error(f"Exception: {e}. Page number: {page_no}. URL: {url}")
                finally:
                    writer.writerow([page_no, ingredient_name, ingredient_synonyms])
        
    browser.quit()

def initiate_scraper_skinsort():
    BASE_ULR_SKINSORT = "https://skinsort.com/ingredients"

    browser = Browser()
    browser.go_to(BASE_ULR_SKINSORT)
    
    current_dt = dt.now().strftime("%Y%m%d_%H%M")
    
    SAVE_IN_FOLDER = os.path.join(SKINSORT_SAVE_FOLDER, f"scrape_{current_dt}")
    
    try:
        os.makedirs(SAVE_IN_FOLDER)
    except:
        logger.log("Cannot create folder!")
        return
    
    last_page_item = browser.find_element(".page-item:last-child a")
    no_of_pages = int(last_page_item.get_attribute("href").split("/")[-1])
           
    #no_of_pages = 1
    
    browser.quit()
        
    args = Arguments(
        callbackFn = scrape_skinsort, 
        page_steps = get_step_pages(no_of_pages), 
        base_url = BASE_ULR_SKINSORT,
        folder_path = SAVE_IN_FOLDER
    )
    
    initiate_drivers(args)
    
initiate_scraper_skinsort()