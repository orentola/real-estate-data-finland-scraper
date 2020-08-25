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

"""
TODO:
- Fix exception handling
- Change the overall design more into object-oriented approach
- Separate classes from the main file into separate files
- Create a configuration file / somehow manage the templates in a better fashion
"""

home_path = os.path.join(os.getcwd())
USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G570Y Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/44.0.2403.133 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.0; SAMSUNG SM-N900 Build/LRX21V) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.1 Chrome/34.0.1847.76 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android-4.0.3; en-us; Galaxy Nexus Build/IML74K) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7",
    "Mozilla/5.0 (Linux; Android 7.0; HTC 10 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"
]
BROWSER_TO_USE = "Chrome"

def string_cleaner(input):
    if (input == None):
        return ""
    return input.replace(u'\xa0', u' ')

class House:
    def __init__(self, link, street, district, city, price, size, roomConfiguration, buildingYear, subType, additionalInfo, date):
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
        self.size = size

class Downloader:
    def __init__(self, name, driver_type):
        self.name = name
        self.driver = None
        self.templates = [] # contains dictionaries with template ID and type and url
        self.error_links = []
        self.driver_type = driver_type
        self.current_houses = []
        self.options = None
        self.current_user_agent = ""
        #self.home_path = os.getcwd()
        self.driver_profile = ""

    def initialize_driver(self):
        if (self.driver_type == "Chrome"):
            self.chrome_options = webdriver.ChromeOptions()
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_argument("--ignore-certificate-errors")
            self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            self.chrome_options.add_argument("--user-agent=" + USER_AGENT_LIST[int(round(random() * len(USER_AGENT_LIST), 1))])

            prefs = {"profile.managed_default_content_settings.images": 2} # Disable images
            self.chrome_options.add_experimental_option("prefs", prefs)

            self.driver = webdriver.Chrome(options=self.chrome_options)
            return True
        if (self.driver_type == "Firefox"):
            self.options = Options()
            self.options.headless = True
            self.driver_profile = webdriver.FirefoxProfile()
            self.driver_profile.set_preference("general.useragent.override", USER_AGENT_LIST[int(round(random() * len(USER_AGENT_LIST), 1))])            
            self.driver_profile.set_preference("permissions.default.image", 2) # Disable images
            self.driver = webdriver.Firefox(options=self.options, firefox_profile=self.driver_profile)
            return True
        return False   

    def quit_driver(self):
        try:
            self.driver.quit()
        except:
            print("Exception in quitting driver, probably closed already.")

    def add_template(self, template):
        self.templates.append(template)

    def run_scraper(self):
        for t in self.templates:
            print("Running template: " + t["name"] + ".")
            template_url = t["url"]
            date_today_str = datetime.now().strftime("%Y-%m-%d")
            current_base_path = os.path.join(home_path, "data", date_today_str, t["type"], t["name"])
            current_house_objects = []
            current_error_links = []
            houseObjects = []

            self.initialize_driver()

            start_time = datetime.now()

            if not os.path.exists(current_base_path):
                os.makedirs(current_base_path)
            
            self.driver.get(template_url.replace("{PAGE_NUMBER}","1"))
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(0.5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(round((random() * 0.30) + 0.5,2)) + ");")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            try:
                maxPages = int(soup.find_all(attrs={"ng-bind":"$ctrl.page + ($ctrl.totalPages ? '/' + $ctrl.totalPages : '')"})[0].string.split('/')[1])
            except IndexError:
                print("Probably an issue with the page. Sleep a while and re-load the page.")
                sleep(30)
                self.driver.get(template_url.replace("{PAGE_NUMBER}","1"))
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                maxPages = int(soup.find_all(attrs={"ng-bind":"$ctrl.page + ($ctrl.totalPages ? '/' + $ctrl.totalPages : '')"})[0].string.split('/')[1])

            #for i in range(1, 1+1):
            for i in range(1, maxPages+1):
                print("Currently at document number: " + str(i))
                # Clear cookies
                self.driver.delete_all_cookies()
                
                seed(datetime.now().second)
                self.driver.get(template_url.replace("{PAGE_NUMBER}",str(i)))    
                #time.sleep(3)
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                #with open(os.path.join(write_dir, "pageSourceRoot_" + str(i) + ".txt"), "w", encoding="utf-8") as file:
                #    file.write(soup.prettify())
                
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(round((random() * 0.30) + 0.5,2)) + ");")
                
                allCards = soup.find_all(attrs={"ng-repeat":"card in $ctrl.parsedCards track by card.id"})
                
                for card in allCards:
                    sub_page_info_dict = {}
                    error_with_current_link = False
                    
                    link = card.a.attrs['ng-href']
                    try:
                        print("Currently processing link: " + link)
                    except:
                        print("Exception occurred at printing the current link to be processed.")
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
                    except KeyError:
                        raise
                    except TimeoutException:
                        print("Timeout error, skipping.")
                        continue
                        #self.driver.get(link)
                        #time.sleep(1)
                        sub_page_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    except Exception as e:
                        print(e.message)
                        print(e.args)
                        print("Error occurred while retrieving link: " + link)
                        #error_with_current_link = True
                    
                    #if (error_with_current_link == True):
                    #    try:
                    #        self.driver.get(link)
                    #        time.sleep(15)
                    #        sub_page_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    #    except KeyError:
                    #        raise
                    #    except Exception as e:
                    #        print(e.message)
                    #        print(e.args)
                    #        print("Error occurred while re-retrieving link: " + link)
                    #        current_error_links.append(link)

                    #with open(os.path.join(home_path, "temp", datetime.now().strftime("%Y-%m-%d"), "pageSourceSubPage" + "_" + str(uuid.uuid4()) + ".txt"), "w", encoding="utf-8") as file:
                    #    file.write(soup.prettify())

                    all_info_table_rows = sub_page_soup.select("div.info-table__row")

                    for info in all_info_table_rows:
                        try:
                            metadata = info.select("dt.info-table__title")
                            if (len(metadata) > 0):
                                metadata = string_cleaner(metadata[0].string)
                            
                            value = info.select("dd.info-table__value")
                            if (len(value) > 0):
                                value = string_cleaner(value[0].string)

                            if (type(value) == str and type(metadata) == str):
                                sub_page_info_dict[metadata] = value
                        except KeyError:
                            raise
                        except:
                            #print("An error with all_info_tables, probably fine: " + str(info))
                            #print("An error with all_info_tables, probably fine.")
                            pass
                    
                    # TODO
                    # if len(current_house_objects) == 0: -> rerun latest download
                    current_house_objects.append(House(link, street, district, city, price, size, roomConfiguration, buildingYear, subType, copy.deepcopy(sub_page_info_dict), date_today_str))        
            end_time = datetime.now()
            self.driver.quit()
            
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
    downloader = Downloader("main", BROWSER_TO_USE)
    templateDict = {}

    templateDict["name"] = "yksio-kaksio-myytavat-espoo-helsinki-vantaa-omatontti-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B39,6,%22Espoo%22%5D,%5B65,6,%22Vantaa%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=1&roomCount%5B%5D=2&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"
    templateDict["type"] = "sale"
    downloader.add_template(copy.deepcopy(templateDict))

    templateDict["name"] = "kolmio-nelio-myytavat-helsinki-oma-tontti-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"
    templateDict["type"] = "sale"
    downloader.add_template(copy.deepcopy(templateDict))

    templateDict["name"] = "yksio-kaksio-vuokrattavat-helsinki-espoo-vantaa-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/vuokrattavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B39,6,%22Espoo%22%5D,%5B65,6,%22Vantaa%22%5D%5D&roomCount%5B%5D=1&roomCount%5B%5D=2&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=101"
    templateDict["type"] = "rent"
    downloader.add_template(copy.deepcopy(templateDict))

    templateDict["name"] = "omakotitalot-rakennettu-2012-jalkeen-pk-seutu"
    templateDict["url"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B65,6,%22Vantaa%22%5D,%5B39,6,%22Espoo%22%5D,%5B130,6,%22Kauniainen%22%5D,%5B147,6,%22Kirkkonummi%22%5D,%5B359,6,%22Sipoo%22%5D%5D&lotOwnershipType%5B%5D=1&size%5Bmin%5D=120&newDevelopment=0&buildingType%5B%5D=4&buildingType%5B%5D=8&buildingType%5B%5D=32&buildingType%5B%5D=128&constructionYear%5Bmin%5D=2012&cardType=100"
    templateDict["type"] = "sale"
    downloader.add_template(copy.deepcopy(templateDict))

    templateDict["name"] = "nelio-viisio-kerrostalo-helsinki-espoo-vantaa-kerrostalo"
    templateDict["url"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B65,6,%22Vantaa%22%5D,%5B39,6,%22Espoo%22%5D%5D&cardType=100&roomCount%5B%5D=4&roomCount%5B%5D=5&buildingType%5B%5D=1&buildingType%5B%5D=256"
    templateDict["type"] = "sale"
    downloader.add_template(copy.deepcopy(templateDict))

    print("Downloader initialized.")
    
    print("Starting the downloader loop.")
    try:
        while True:
            time_start = datetime.now()
            downloader.run_scraper()
            time_end = datetime.now()

            total_run_time = ((time_end - time_start).seconds)/60/60

            print("Last runs took: " + str(round(total_run_time)) + " hours.")

            latest_run_date = datetime.strptime(str(time_start.year) + "-" + str(time_start.month) + "-" + str(time_start.day), "%Y-%m-%d").date()
            date_now = date.today()

            # Sleep for 24 - runtime hours
            time_to_sleep = max(0, 24 - total_run_time) * 60 * 60

            # if a day has passed, sleep for 16 hours
            # otherwise sleep for 24 hours
            #if (latest_run_date < date_now):
            #    time_to_sleep = 60 * 60 * 16
            #else:
            #    time_to_sleep = 60 * 60 * 24

            print("Sleeping for " + str(round(time_to_sleep/60/60, 2)) + " hours.")

            time.sleep(time_to_sleep)
        downloader.quit_driver()
    except KeyError:
        downloader.quit_driver()
        raise
    except Exception as e:
        print(e.message)
        print(e.args)
        print("Unhandled exception.")
        downloader.quit_driver()
    finally:
        downloader.quit_driver()

main()
