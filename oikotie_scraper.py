from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests
import time
import os
import uuid
import json
import sys
import copy

from random import seed
from random import random

from datetime import datetime
from datetime import date

home_path = os.path.join(os.getcwd())

#if ((len(sys.argv) -1) > 0):
#    print("Being called with more than 0 arguments. Setting arguments.")
#    template_url = templateDict[sys.argv[2]]
#    #home_path = "C:\\Users\\orent\\Documents\\Asuntosijoittaminen\\webscraper\\{path}\\".replace("{path}", sys.argv[1])
#    home_path = os.path.join(os.getcwd(), sys.argv[1], sys.argv[2])
#    with open(os.path.join(home_path, "config.txt"), "w") as f:
#        f.write(templateDict[sys.argv[2]])
#else:
#    print("Usage: python.py rent/sale template_id")
#    exit()

### kolmio-nelio myytavat helsinki oma-tontti kerrostalo
#templateDict["2"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"

### yksio-kaksio-kolmio-nelio vuokrattavat helsingin/espoon/vantaan alueilta kerrostalo
#templateDict["3"] = "https://asunnot.oikotie.fi/vuokrattavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B1643,4,%22Punavuori,%20Helsinki%22%5D,%5B1641,4,%22Kaartinkaupunki,%20Helsinki%22%5D,%5B1639,4,%22Kruununhaka,%20Helsinki%22%5D,%5B335078,4,%22Ruoholahti,%20Helsinki%22%5D,%5B5695443,4,%22J%C3%A4tk%C3%A4saari,%20Helsinki%22%5D,%5B1642,4,%22Kamppi,%20Helsinki%22%5D,%5B1724,4,%22T%C3%B6%C3%B6l%C3%B6,%20Helsinki%22%5D,%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D,%5B11820666,4,%22Sompasaari,%20Helsinki%22%5D,%5B1648,4,%22S%C3%B6rn%C3%A4inen,%20Helsinki%22%5D,%5B335077,4,%22Pikku%20Huopalahti,%20Helsinki%22%5D,%5B789,4,%22Tapiola,%20Espoo%22%5D,%5B1667,4,%22Haaga,%20Helsinki%22%5D,%5B335093,4,%22Kannelm%C3%A4ki,%20Helsinki%22%5D,%5B11742,4,%22Str%C3%B6mbolstad,%20Sund%22%5D,%5B1684,4,%22Pit%C3%A4j%C3%A4nm%C3%A4ki,%20Helsinki%22%5D,%5B1666,4,%22Oulunkyl%C3%A4,%20Helsinki%22%5D,%5B335101,4,%22Pihlajisto,%20Helsinki%22%5D,%5B1674,4,%22Viikki,%20Helsinki%22%5D,%5B892,4,%22Kivenlahti,%20Espoo%22%5D,%5B803,4,%22Soukka,%20Espoo%22%5D,%5B804,4,%22Espoonlahti,%20Espoo%22%5D,%5B1669,4,%22Lauttasaari,%20Helsinki%22%5D,%5B11820654,4,%22Vattuniemi,%20Helsinki%22%5D,%5B1758,4,%22Tikkurila,%20Vantaa%22%5D,%5B335120,4,%22Mellunm%C3%A4ki,%20Helsinki%22%5D,%5B1676,4,%22Malmi,%20Helsinki%22%5D%5D&roomCount%5B%5D=1&roomCount%5B%5D=2&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=101"

### Yksio-kaksio myytavat espoo-helsinki-vantaa oma-tontti kerrostalo
#templateDict["1"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B39,6,%22Espoo%22%5D,%5B65,6,%22Vantaa%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=1&roomCount%5B%5D=2&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"

class House:
    def __init__(self, link, street, district, city, price, roomConfiguration, buildingYear, subType, additionalInfo, date):
        self.link = link
        self.street = street
        self.district = district
        self.city = city
        self.price = price
        self.roomConfiguration = roomConfiguration
        self.buildingYear = buildingYear
        self.subType = subType
        self.additionalInfo = additionalInfo
        self.date = date
        
def string_cleaner(input):
    return input.replace(u'\xa0', u' ')

class Downloader:
    def __init__(self, name, driver_type):
        self.name = name
        self.driver = None
        self.templates = [] # contains dictionaries with template ID and type and url
        self.error_links = []
        self.driver_type = driver_type
        self.current_houses = []
        self.options = None
        #self.home_path = os.getcwd()
    
    def initialize_driver(self):
        if (self.driver_type == "Chrome"):
            self.chrome_options = webdriver.ChromeOptions()
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_argument("--ignore-certificate-errors")
            self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            self.driver = webdriver.Chrome(options=self.chrome_options)
            return True
        if (self.driver_type == "Firefox"):
            self.options = Options()
            self.options.headless = True
            self.driver = webdriver.Firefox(options=self.options)
            return True

        return False        

    def add_template(self, template):
        self.templates.append(template)
    
    def run_scraper(self):
        #templates_to_run = []
        #if (template_id == None):
        #    templates_to_run = templates
        #else:
        #    try:
        #        templates_to_run.append(templates[template_id])
        #    except:
        #        print("Error with selecting templates.")
        #        raise Exception("Problem with template selection.")
        
        for t in self.templates:
            print("Running template: " + t["name"] + ".")
            template_url = t["url"]
            date_today_str = datetime.now().strftime("%Y-%m-%d")
            current_base_path = os.path.join(home_path, "data", date_today_str, t["type"], t["name"])
            current_house_objects = []
            current_error_links = []

            houseObjects = []

            start_time = datetime.now()

            if not os.path.exists(current_base_path):
                os.makedirs(current_base_path)

            self.driver.get(template_url.replace("{PAGE_NUMBER}","1"))
            time.sleep(5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            maxPages = int(soup.find_all(attrs={"ng-bind":"$ctrl.page + ($ctrl.totalPages ? '/' + $ctrl.totalPages : '')"})[0].string.split('/')[1])
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(round((random() * 0.30) + 0.5,2)) + ");")

            for i in range(1, 1+1):
            #for i in range(1, maxPages+1):
                print("Currently at document number: " + str(i))
                seed(datetime.now().second)
                self.driver.get(template_url.replace("{PAGE_NUMBER}",str(i)))    
                #time.sleep(3)
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                

                
                #with open(os.path.join(write_dir, "pageSourceRoot_" + str(i) + ".txt"), "w", encoding="utf-8") as file:
                #    file.write(soup.prettify())
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(round((random() * 0.30) + 0.5,2)) + ");")
                sub_page_info_dict = {}

                allCards = soup.find_all(attrs={"ng-repeat":"card in $ctrl.parsedCards track by card.id"})

                for card in allCards:
                    error_with_current_link = False
                    
                    link = card.a.attrs['ng-href']
                    street = card.find_all(attrs={"ng-bind":"$ctrl.card.building.address"})
                    if (len(street) > 0):
                        street = string_cleaner(street[0].string)
                    else:
                        street = str(street)

                    district = card.find_all(attrs={"ng-bind":"$ctrl.card.building.district"})
                    if (len(district) > 0):
                        district = string_cleaner(district[0].string)
                    else:
                        district = str(district)

                    city = card.find_all(attrs={"ng-bind":"$ctrl.card.building.city"})
                    if (len(city) > 0):
                        city = string_cleaner(city[0].string)
                    else:
                        city = str(city)

                    price = card.find_all(attrs={"ng-bind":"$ctrl.card.price"})
                    if (len(price) > 0):
                        price = string_cleaner(price[0].string)
                    else:
                        price = str(price)

                    size = card.find_all(attrs={"ng-bind":"$ctrl.card.size"})
                    if (len(size) > 0):
                        size = string_cleaner(size[0].string)
                    else:
                        size = str(size)

                    roomConfiguration = card.find_all(attrs={"ng-bind":"$ctrl.card.roomConfiguration"})
                    if (len(roomConfiguration) > 0):
                        roomConfiguration = string_cleaner(roomConfiguration[0].string)
                    else:
                        roomConfiguration = str(roomConfiguration)

                    buildingYear = card.find_all(attrs={"ng-bind":"$ctrl.card.building.year"})
                    if (len(buildingYear) > 0):
                        buildingYear = string_cleaner(buildingYear[0].string)
                    else:
                        buildingYear = str(buildingYear)

                    subType = card.find_all(attrs={"ng-if":"$ctrl.card.subType"})
                    if (len(subType) > 0):
                        subType = string_cleaner(subType[0].string)
                    else:
                        subType = str(subType)
                    
                    try:
                        self.driver.get(link)
                        #time.sleep(1)
                        sub_page_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    except:
                        print("Error occurred while retrieving link: " + link)
                        error_with_current_link = True
                        
                    if (error_with_current_link == True):
                        try:
                            self.driver.get(link)
                            time.sleep(5)
                            sub_page_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        except:
                            print("Error occurred while re-retrieving link: " + link)
                            current_error_links.append(link)

                    #with open(os.path.join(home_path, "temp", datetime.now().strftime("%Y-%m-%d"), "pageSourceSubPage" + "_" + str(uuid.uuid4()) + ".txt"), "w", encoding="utf-8") as file:
                    #    file.write(soup.prettify())

                    all_info_table_rows = sub_page_soup.select("div.info-table__row")

                    for info in all_info_table_rows:
                        try:
                            metadata = info.select("div.info-table__title")
                            if (len(metadata) > 0):
                                metadata = string_cleaner(metadata[0].string)
                            
                            value = info.select("div.info-table__value")
                            if (len(value) > 0):
                                value = string_cleaner(value[0].string)

                            if (type(value) == str and type(metadata) == str):
                                sub_page_info_dict[metadata] = value
                        except:
                            #print("An error with all_info_tables, probably fine: " + str(info))
                            print("An error with all_info_tables, probably fine.")
                                
                    current_house_objects.append(House(link, street, district, city, price, roomConfiguration, buildingYear, subType, sub_page_info_dict, date_today_str))
            end_time = datetime.now()
            
            print("Had errors with the following links: " + str(current_error_links))
            
            print("Downloading finished in: " + str( (((end_time - start_time).seconds / 60)/60)) + " hours.")
            
            print("Writing output files.")
            output_dict = {}
            for j in range(0, len(current_house_objects)):
                output_dict[j] = json.dumps(current_house_objects[j].__dict__)

            json_output_file = os.path.join(current_base_path, "data.json")
            with open(json_output_file, 'w') as f:
                json.dump(output_dict, f, ensure_ascii=False, indent=4)            

def main():
    print("Initializing Downloader.")
    downloader = Downloader("main", "Chrome")
    templateDict = {}

    templateDict["name"] = "yksio-kaksio-myytavat-espoo-helsinki-vantaa-omatontti-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B39,6,%22Espoo%22%5D,%5B65,6,%22Vantaa%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=1&roomCount%5B%5D=2&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"
    templateDict["type"] = "sale"
    downloader.add_template(copy.deepcopy(templateDict))

    templateDict["name"] = "kolmio-nelio-myytavat-helsinki-oma-tontti-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"
    templateDict["type"] = "sale"
    downloader.add_template(copy.deepcopy(templateDict))

    templateDict["name"] = "yksio-kaksio-kolmio-nelio-vuokrattavat-helsinki-espoo-vantaa-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/vuokrattavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B1643,4,%22Punavuori,%20Helsinki%22%5D,%5B1641,4,%22Kaartinkaupunki,%20Helsinki%22%5D,%5B1639,4,%22Kruununhaka,%20Helsinki%22%5D,%5B335078,4,%22Ruoholahti,%20Helsinki%22%5D,%5B5695443,4,%22J%C3%A4tk%C3%A4saari,%20Helsinki%22%5D,%5B1642,4,%22Kamppi,%20Helsinki%22%5D,%5B1724,4,%22T%C3%B6%C3%B6l%C3%B6,%20Helsinki%22%5D,%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D,%5B11820666,4,%22Sompasaari,%20Helsinki%22%5D,%5B1648,4,%22S%C3%B6rn%C3%A4inen,%20Helsinki%22%5D,%5B335077,4,%22Pikku%20Huopalahti,%20Helsinki%22%5D,%5B789,4,%22Tapiola,%20Espoo%22%5D,%5B1667,4,%22Haaga,%20Helsinki%22%5D,%5B335093,4,%22Kannelm%C3%A4ki,%20Helsinki%22%5D,%5B11742,4,%22Str%C3%B6mbolstad,%20Sund%22%5D,%5B1684,4,%22Pit%C3%A4j%C3%A4nm%C3%A4ki,%20Helsinki%22%5D,%5B1666,4,%22Oulunkyl%C3%A4,%20Helsinki%22%5D,%5B335101,4,%22Pihlajisto,%20Helsinki%22%5D,%5B1674,4,%22Viikki,%20Helsinki%22%5D,%5B892,4,%22Kivenlahti,%20Espoo%22%5D,%5B803,4,%22Soukka,%20Espoo%22%5D,%5B804,4,%22Espoonlahti,%20Espoo%22%5D,%5B1669,4,%22Lauttasaari,%20Helsinki%22%5D,%5B11820654,4,%22Vattuniemi,%20Helsinki%22%5D,%5B1758,4,%22Tikkurila,%20Vantaa%22%5D,%5B335120,4,%22Mellunm%C3%A4ki,%20Helsinki%22%5D,%5B1676,4,%22Malmi,%20Helsinki%22%5D%5D&roomCount%5B%5D=1&roomCount%5B%5D=2&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=101"
    templateDict["type"] = "rent"
    downloader.add_template(copy.deepcopy(templateDict))

    downloader.initialize_driver()

    print("Downloader initialized.")
    
    print("Starting the downloader loop.")
    while True:
        time_start = datetime.now()
        downloader.run_scraper()
        time_end = datetime.now()

        print("Last runs took: " + str(round(((time_end - time_start).seconds)/60/60)) + " hours.")

        latest_run_date = datetime.strptime(str(time_start.year) + "-" + str(time_start.month) + "-" + str(time_start.day), "%Y-%m-%d").date()
        date_now = date.today()

        # if a day has passed, sleep for 16 hours
        # otherwise sleep for 24 hours
        if (latest_run_date < date_now):
            time_to_sleep = 60 * 60 * 16
        else:
            time_to_sleep = 60 * 60 * 24

        print("Sleeping for " + str(round(time_to_sleep/60/60, 2)) + " hours.")
        time.sleep(time_to_sleep)

main()
