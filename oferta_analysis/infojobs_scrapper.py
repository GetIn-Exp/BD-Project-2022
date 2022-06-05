

from bs4 import BeautifulSoup
import pandas as pd
import json

from time import sleep
from datetime import date, datetime, timedelta
from termcolor import colored

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException

search_params = { 'keyword': "", 
                'normalizedJobTitleIds': "", 
                'provinceIds' : "",
                'cityIds' : "",
                'teleworkingIds': "",
                "categoryIds" : "",
                "workdayIds" : "",
                "educationIds" : "", 
                "segmentId" : "",
                "contractTypeIds": "",
                "page" : 1,
                "sortBy" : "PUBLICATION_DATE",
                "onlyForeignCountry": "false",
                "countryIds": "",
                "sinceDate": "ANY",
                "subcategoryIds": ""
                }

category_ids = { 
    #"Administración de empresas": 10,
    #"Administración Pública" : 20,
    #"Atención a clientes": 170,
    #"Calidad, producción e I+D": 30,
    #"Comercial y ventas": 190,
    #"Compras, logística y almacén": 40,
    #"Diseño y artes gráficas": 50,
    #"Educación y formación": 60,
    #"Finanzas y banca": 70,
    #"Informática y telecomunicaciones": 150,
    #"Ingenieros y técnicos": 80,
    #"Inmobiliario y construcción": 90,
    #"Legal": 100,
    #"Marketing y comunicación": 110,
    #"Otros": 180,
    #"Profesiones, artes y oficios": 120,
    #"Recursos humanos": 130,
    "Sanidad y salud": 140,
    "Sector Farmacéutico": 210,
    "Turismo y restauración": 160,
    "Ventas al detalle": 200,
}

# Education We're interested on
education_ids = {
    "Grado" : 125, 
#    "Educación Secundaria Obligatoria" : 20, 
#    "Ciclo Formativo Grado Superior" : 60, 
#    "Ciclo Formativo Grado Medio": 35,
#    "Batchillerato": 50,
#    "Sin estudios": 10,
}

# InfoJOBS base url
base_url = "https://www.infojobs.net/jobsearch/search-results/list.xhtml?"

infojobs_endpoints = [] # Infojobs Endpoints
param_combinations = [] # Infojobs Params (category + education)


def createURLS():
    # Procede to create all the URLS for scrapping. By now, only interested on category + education 
    # (this is not immediately scrapped)

    for category in category_ids:
        for education in education_ids:

            search_params['categoryIds'] = category_ids[category]
            search_params['educationIds'] = education_ids[education]
            endpoint = "&".join(["=".join([key, str(value)]) for key, value in search_params.items()])     
            param_combinations.append((category_ids[category], education_ids[education]))
            infojobs_endpoints.append(endpoint)

    # Create all the url's for searching
    return [base_url + endpoint for endpoint in infojobs_endpoints]


def click_by_id(driver, id, timeout = 2):
    # Click an element given its id.
    try:
        WebDriverWait(driver, timeout, ignored_exceptions= (NoSuchElementException,StaleElementReferenceException,))\
            .until(EC.element_to_be_clickable((By.ID, id))).click()

    except WebDriverException:
        input(colored(f"Please, click the element with id {id} to continue:", 'red'))

""" -------------------------------- DATE PARSING -----------------------------------

def getReleaseDate(input_date):
    # Given an entry of the form: "Hace x días", return the exact DateTime formatted 
    # as the text 'dd-mm-yyyy'
    import re

    output_date = date.today()

    date_expr = re.compile("\d(m|h|d)")

    for word in input_date.split(" "):
        if date_expr.math(word):
            
            if 'm' in word: output_date -= timedelta(minutes=int(word[0]))
            elif 'h' in word:  output_date -= timedelta(hours=word[0])
            else: output_date -= timedelta(days=int(word[0]))
            break

    else: output_date = 

    print("Date Parsed:", output_date)

from dateutil.parser import parserinfo

class CustomParserInfo(parserinfo):

    # three months in Spanish for illustration
    MONTHS = [("Enero", "Enero"), ("Feb", "Febrero"), ("Marzo", "Marzo")]
    
"""

def getJobOffert(job_post, **search_params):
    # Given a job post of the class "sui-AtomCard-info", puts its information into the json.

    job_entry = {}
    job_entry['title'] = job_post.find_element(by=By.CLASS_NAME, value = "ij-OfferCardContent-description-title").text
    job_entry['company'] = job_post.find_element(by=By.CLASS_NAME, value = "ij-OfferCardContent-description-subtitle").text
    job_entry['description'] = job_post.find_element(by=By.CLASS_NAME, value = "ij-OfferCardContent-description-description").text
    job_entry['status'] = 'ACTIVE'
    

    # Retrieve list items elements: location, modality, release_date (first row), agreement, work_time, salary (second row)
    first_row_ul, second_row_ul, = job_post.find_elements(By.CLASS_NAME, "ij-OfferCardContent-description-list")
    first_row_li_items = first_row_ul.find_elements(By.CLASS_NAME, "ij-OfferCardContent-description-list-item")
    second_row_li_items = second_row_ul.find_elements(By.CLASS_NAME, "ij-OfferCardContent-description-list-item")
    
    # Consider whether there's modality
    if len(first_row_li_items) > 2: 
        job_entry['location'] = first_row_li_items[0].text
        job_entry['modality'] = first_row_li_items[1].text
        job_entry['release_date'] = first_row_li_items[2].text

    else:
        job_entry['location'] = first_row_li_items[0].text
        job_entry['modality'] = None
        job_entry['release_date'] = first_row_li_items[1].text

    if "\n" in job_entry['release_date']:
        job_entry['release_date'] = job_entry['release_date'].split("\n")[0]

    job_entry['agreement'] = second_row_li_items[0].text
    job_entry['work_time'] = second_row_li_items[1].text
    job_entry['salary'] = second_row_li_items[2].text

    # Copy job_entry params
    for key, val in search_params.items():
        job_entry[key] = val

    return job_entry


def scrapJobOfferts(driver, education, category, current_index):
    # Navigates to the corresponding InfoJobs Page by selecting the education and category checkboxes
    # Appends to the json_offerts all the possible json_offerts from that page

    for job_post in driver.find_elements(By.CLASS_NAME, "sui-AtomCard-info"):

        try:
            # Avoid advertising!
            if not len(job_post.find_elements(By.ID, value = "ij-AdvertisingNativeListing-CardContent-description-title")):

                json_offerts.append(getJobOffert(job_post, **{'id': current_index, 'education' : education, 'category' : category}))
                current_index += 1

        except WebDriverException:
            print(f"Skipping offert {current_index}")

    return current_index


def load_next_page(driver):
    try:
        # Loads next page
        pagination = driver.find_element(By.CLASS_NAME, value = "ij-ComponentPagination")
        last_button = pagination.find_elements(By.CLASS_NAME, value = "sui-AtomButton")[-1]
        
        if 'SIGUIENTE' in last_button.text:
            last_button.click()
            return True
    
    except NoSuchElementException:
        print("No more pages with this combination.")
        pass
    
    return False

    
# List of scrapped offerts
json_offerts = []

if __name__ == '__main__':
    
    # Create the URL's we need
    # infojobs_urls = createURLS()

    # Initiate seleniums webdriver connection with Firefox
    driver = webdriver.Firefox()
    driver.maximize_window()

    input("Press enter when you're ready to begin the scrapping")
    print("--------------- Beginning Scrapping ----------------")

    offerts_parsed_so_far = 42763 # Initial index
    filename = "infojobs_data_" + str(offerts_parsed_so_far) + ".json"

    for education in education_ids:

        # Selects the education checkbox
        click_by_id(driver, "check-education--" + str(education_ids[education]))

        for category in category_ids:

            # Selects the category checkbox
            click_by_id(driver, "check-category--" + str(category_ids[category]))

            print("\nTotal job offerts scrapped so far:", offerts_parsed_so_far)
            print("Scrapping the search results of (%s, %s)"%(education, category))

            new_page_loaded = True
            while new_page_loaded:
                
                sleep(2)

                # Scrap the page given by the education and category
                offerts_parsed_so_far = scrapJobOfferts(driver, education, category, offerts_parsed_so_far)

                # Load next page if possible
                new_page_loaded = load_next_page(driver)

            # Deselects the category checkbox
            click_by_id(driver, "check-category--" + str(category_ids[category]))

            # JSON Writing after each iteration  
            with open(filename, 'w',  encoding='utf8') as fout:
                json.dump(json_offerts , fout, ensure_ascii = False)

        # Deselects the education checkbox
        click_by_id(driver, "check-education--" + str(education_ids[education]))
        

    print("--------------- Scrapping complete! ----------------")
    print("Total job offerts scrapped:", offerts_parsed_so_far)