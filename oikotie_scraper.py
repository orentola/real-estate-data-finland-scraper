from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import requests
import time
import os
import uuid
import json
import sys

from random import seed
from random import random

from datetime import datetime

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

options = Options()
options.headless = True 
driver = webdriver.Firefox(options=options)
templateDict = {}
sleep_time = 24 * 60 * 60 # 24 hours sleepy sleep

### Yksio-kaksio myytavat espoo-helsinki-vantaa oma-tontti kerrostalo
templateDict["1"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B39,6,%22Espoo%22%5D,%5B65,6,%22Vantaa%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=1&roomCount%5B%5D=2&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"

### kolmio-nelio myytavat helsinki oma-tontti kerrostalo
templateDict["2"] = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"

### yksio-kaksio-kolmio-nelio vuokrattavat helsingin/espoon/vantaan alueilta kerrostalo
templateDict["3"] = "https://asunnot.oikotie.fi/vuokrattavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B1643,4,%22Punavuori,%20Helsinki%22%5D,%5B1641,4,%22Kaartinkaupunki,%20Helsinki%22%5D,%5B1639,4,%22Kruununhaka,%20Helsinki%22%5D,%5B335078,4,%22Ruoholahti,%20Helsinki%22%5D,%5B5695443,4,%22J%C3%A4tk%C3%A4saari,%20Helsinki%22%5D,%5B1642,4,%22Kamppi,%20Helsinki%22%5D,%5B1724,4,%22T%C3%B6%C3%B6l%C3%B6,%20Helsinki%22%5D,%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D,%5B11820666,4,%22Sompasaari,%20Helsinki%22%5D,%5B1648,4,%22S%C3%B6rn%C3%A4inen,%20Helsinki%22%5D,%5B335077,4,%22Pikku%20Huopalahti,%20Helsinki%22%5D,%5B789,4,%22Tapiola,%20Espoo%22%5D,%5B1667,4,%22Haaga,%20Helsinki%22%5D,%5B335093,4,%22Kannelm%C3%A4ki,%20Helsinki%22%5D,%5B11742,4,%22Str%C3%B6mbolstad,%20Sund%22%5D,%5B1684,4,%22Pit%C3%A4j%C3%A4nm%C3%A4ki,%20Helsinki%22%5D,%5B1666,4,%22Oulunkyl%C3%A4,%20Helsinki%22%5D,%5B335101,4,%22Pihlajisto,%20Helsinki%22%5D,%5B1674,4,%22Viikki,%20Helsinki%22%5D,%5B892,4,%22Kivenlahti,%20Espoo%22%5D,%5B803,4,%22Soukka,%20Espoo%22%5D,%5B804,4,%22Espoonlahti,%20Espoo%22%5D,%5B1669,4,%22Lauttasaari,%20Helsinki%22%5D,%5B11820654,4,%22Vattuniemi,%20Helsinki%22%5D,%5B1758,4,%22Tikkurila,%20Vantaa%22%5D,%5B335120,4,%22Mellunm%C3%A4ki,%20Helsinki%22%5D,%5B1676,4,%22Malmi,%20Helsinki%22%5D%5D&roomCount%5B%5D=1&roomCount%5B%5D=2&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=101"

if ((len(sys.argv) -1) > 0):
    print("Being called with more than 0 arguments. Setting arguments.")
    template_url = templateDict[sys.argv[2]]
    home_path = "C:\\Users\\orent\\Documents\\Asuntosijoittaminen\\webscraper\\{path}\\".replace("{path}", sys.argv[1])
else:
    print("Usage: python.py rent/sale template_id")
    exit()



##########################################
# Templates

### Yksio-kaksio myytavat espoo-helsinki-vantaa oma-tontti kerrostalo
#template_url = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D,%5B39,6,%22Espoo%22%5D,%5B65,6,%22Vantaa%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=1&roomCount%5B%5D=2&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"

### kolmio-nelio myytavat helsinki oma-tontti kerrostalo
#template_url = "https://asunnot.oikotie.fi/myytavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B64,6,%22Helsinki%22%5D%5D&lotOwnershipType%5B%5D=1&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=100"

### yksio-kaksio-kolmio-nelio vuokrattavat helsingin/espoon/vantaan alueilta kerrostalo
#template_url = "https://asunnot.oikotie.fi/vuokrattavat-asunnot?pagination={PAGE_NUMBER}&locations=%5B%5B1643,4,%22Punavuori,%20Helsinki%22%5D,%5B1641,4,%22Kaartinkaupunki,%20Helsinki%22%5D,%5B1639,4,%22Kruununhaka,%20Helsinki%22%5D,%5B335078,4,%22Ruoholahti,%20Helsinki%22%5D,%5B5695443,4,%22J%C3%A4tk%C3%A4saari,%20Helsinki%22%5D,%5B1642,4,%22Kamppi,%20Helsinki%22%5D,%5B1724,4,%22T%C3%B6%C3%B6l%C3%B6,%20Helsinki%22%5D,%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D,%5B11820666,4,%22Sompasaari,%20Helsinki%22%5D,%5B1648,4,%22S%C3%B6rn%C3%A4inen,%20Helsinki%22%5D,%5B335077,4,%22Pikku%20Huopalahti,%20Helsinki%22%5D,%5B789,4,%22Tapiola,%20Espoo%22%5D,%5B1667,4,%22Haaga,%20Helsinki%22%5D,%5B335093,4,%22Kannelm%C3%A4ki,%20Helsinki%22%5D,%5B11742,4,%22Str%C3%B6mbolstad,%20Sund%22%5D,%5B1684,4,%22Pit%C3%A4j%C3%A4nm%C3%A4ki,%20Helsinki%22%5D,%5B1666,4,%22Oulunkyl%C3%A4,%20Helsinki%22%5D,%5B335101,4,%22Pihlajisto,%20Helsinki%22%5D,%5B1674,4,%22Viikki,%20Helsinki%22%5D,%5B892,4,%22Kivenlahti,%20Espoo%22%5D,%5B803,4,%22Soukka,%20Espoo%22%5D,%5B804,4,%22Espoonlahti,%20Espoo%22%5D,%5B1669,4,%22Lauttasaari,%20Helsinki%22%5D,%5B11820654,4,%22Vattuniemi,%20Helsinki%22%5D,%5B1758,4,%22Tikkurila,%20Vantaa%22%5D,%5B335120,4,%22Mellunm%C3%A4ki,%20Helsinki%22%5D,%5B1676,4,%22Malmi,%20Helsinki%22%5D%5D&roomCount%5B%5D=1&roomCount%5B%5D=2&roomCount%5B%5D=3&roomCount%5B%5D=4&buildingType%5B%5D=1&buildingType%5B%5D=256&cardType=101"


#with open(home_path + "pageSource3subpage.txt", "w", encoding="utf-8") as file:
#    file.write(sub_page_soup.prettify())

#next_page_click = driver.find_element_by_xpath("//button[@ng-click='$ctrl.togglePage($ctrl.page + 1)']")

while True:
    print("Starting to scrape.")
    date_today_str = datetime.now().strftime("%Y-%m-%d")

    driver.get(template_url.replace("{PAGE_NUMBER}","1"))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    maxPages = int(soup.find_all(attrs={"ng-bind":"$ctrl.page + ($ctrl.totalPages ? '/' + $ctrl.totalPages : '')"})[0].string.split('/')[1])
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(round((random() * 0.30) + 0.5,2)) + ");")

    houseObjects = []

    #for i in range(1, 1+1):
    for i in range(1, maxPages+1):
        print("Currently at document number: " + str(i))
        seed(datetime.now().second)
        driver.get(template_url.replace("{PAGE_NUMBER}",str(i)))    
        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        write_dir = os.path.join(home_path, "temp", date_today_str)
        if not os.path.exists(write_dir):
            os.makedirs(write_dir)
        
        #with open(os.path.join(write_dir, "pageSourceRoot_" + str(i) + ".txt"), "w", encoding="utf-8") as file:
        #    file.write(soup.prettify())
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*" + str(round((random() * 0.30) + 0.5,2)) + ");")
        sub_page_info_dict = {}

        allCards = soup.find_all(attrs={"ng-repeat":"card in $ctrl.parsedCards track by card.id"})

        for card in allCards:
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

            driver.get(link)
            time.sleep(0.7)
            sub_page_soup = BeautifulSoup(driver.page_source, 'html.parser')

            with open(os.path.join(home_path, "temp", datetime.now().strftime("%Y-%m-%d"), "pageSourceSubPage" + "_" + str(uuid.uuid4()) + ".txt"), "w", encoding="utf-8") as file:
                file.write(soup.prettify())

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
                    print("An error with all_info_tables, probably fine: " + str(info))
                        
            houseObjects.append(House(link, street, district, city, price, roomConfiguration, buildingYear, subType, sub_page_info_dict, date_today_str))
    print("Writing output files.")
    output_dict = {}
    for j in range(0, len(houseObjects)):
        output_dict[j] = json.dumps(houseObjects[j].__dict__)

    json_output_file = os.path.join(write_dir, "json_dump_data.json")
    with open(json_output_file, 'w') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=4)
    
    print("Sleeping for " + str(sleep_time) ".")
    time.sleep(sleep_time)


