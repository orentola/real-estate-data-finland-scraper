from datetime import datetime
from datetime import timedelta
from os import path
from pathlib import Path

import os
import json



input_path = "C:\\Users\\orent\\Documents\\Asuntosijoittaminen\\webscraper\\latest\\data\\"

DELIMITER = '#'

# This should be implemented in a smart way
# now this is quite awful.
columns = ["link", "type", "street", "district", "city", "roomConfiguration", "subType", "is_forenom", "prices", "time_in_market", "first_seen", "last_seen"]
first_line = ','.join(columns) + "\n"

scraper_data_to_read = {}
scraper_data_to_read["yksio-kaksio-vuokrattavat-helsinki-espoo-vantaa-kerrostalo"] = "rent"
scraper_data_to_read["kolmio-nelio-myytavat-helsinki-oma-tontti-kerrostalo"] = "sale"
scraper_data_to_read["yksio-kaksio-myytavat-espoo-helsinki-vantaa-omatontti-kerrostalo"] = "sale"

start_date = datetime(2019, 12, 16)
end_date = datetime(2020, 5, 18)

print("Starting to loop through scrapers' data.")

class Apartment:
	def __init__(self, link, type, street, district, city, roomConfiguration, subType, is_forenom, date = None, price = None):
		self.link = link
		self.type = type
		self.street = street
		self.district = district
		self.city = city
		self.roomConfiguration = roomConfiguration
		self.subType = subType
		self.last_price_guess = price.replace("\u20ac", "").replace(" ","").replace("/", "").replace("kk","").replace(",",".")
		self.is_forenom = is_forenom

		self.first_seen = date
		self.last_seen = date

		self.time_in_market = None

		self.prices = [(date, price.replace("\u20ac", "").replace(" ","").replace("/", "").replace("kk","").replace(",","."))]

	@classmethod
	def from_dict(cls, dict, type):
		c = cls(dict["link"], type, dict["street"], dict["district"], dict["city"], dict["roomConfiguration"], dict["subType"], str(dict["is_forenom"]) if 'is_forenom' in dict else "None", dict["date"], dict["price"])
		return c

	def update_time_in_market(self):
		self.time_in_market = (datetime.strptime(self.last_seen, "%Y-%m-%d") - datetime.strptime(self.first_seen, "%Y-%m-%d")).days

	def update_first_and_last_seen(self, date):
		# If param: date is earlier than existing value, update first seen value
		if (datetime.strptime(date, "%Y-%m-%d") < datetime.strptime(self.first_seen, "%Y-%m-%d")):
			self.first_seen = date
		if (datetime.strptime(date, "%Y-%m-%d") > datetime.strptime(self.last_seen, "%Y-%m-%d")):
			self.last_seen = date

	def to_string(self, order, delimiter = DELIMITER):
		output_string = ""
		for o in order:
			#print(o)
			output_string = output_string + str(self.__dict__[o]) + delimiter
		
		output_string = output_string + self.last_price_guess
		# Remove last delimiter
		#output_string = output_string[:-1]
		output_string = output_string + "\n"
		
		# There can be unicode euro characters
		#output_string = output_string.encode('utf8')

		return output_string

for scraper, type in scraper_data_to_read.items():
	output_string = first_line
	base_path = os.path.join(input_path, "#DATE_TEMPLATE#", type, scraper, "data.json")
	current_run_dict = {}

	dates_to_run_list = []
	for i in range(0, (end_date - start_date).days):
		temp_date = (start_date + timedelta(i)).strftime("%Y-%m-%d")
		dates_to_run_list.append(temp_date)

	for date in dates_to_run_list:
		print("Now running date: " + date)
		current_path = base_path.replace("#DATE_TEMPLATE#", date)

		# The data might not exist btw.

		if (path.exists(current_path) is not True):
			print("This path does not exist, continuing.")
			continue

		with open(current_path, "r") as f:
			current_data = json.load(f)

		for k, v in current_data.items():
			current_data_per_item = json.loads(v)
			current_link = current_data_per_item["link"]

			if current_link not in current_run_dict:
				# Initialize new Apartment class
				#print("Initializing new Apartment class.")
				current_run_dict[current_link] = Apartment.from_dict(current_data_per_item, type)
			else:
				# Update data
				#print("Updating existing Apartment class data.")
				current_run_dict[current_link].prices.append((current_data_per_item["date"], current_data_per_item["price"]))
				current_run_dict[current_link].last_price_guess = current_data_per_item["price"]
				current_run_dict[current_link].update_first_and_last_seen(current_data_per_item["date"])
	
	for k, v in current_run_dict.items():
		v.update_time_in_market()

	print("Writing the loaded data into a file.")
	output_path = os.path.join(input_path, type, scraper)
	Path(output_path).mkdir(parents=True, exist_ok=True)

	with open(os.path.join(output_path, "all_data.csv"), encoding="utf-8", mode="w") as f:
		for k, v in current_run_dict.items():
			# UnicodeEncodeError: 'charmap' codec can't encode character '\u0308' in position 78: character maps to <undefined>
			f.write(v.to_string(columns))

print("Done.")
