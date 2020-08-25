from datetime import datetime
from datetime import timedelta
from os import path
from pathlib import Path
from time import sleep

import requests
import os
import json
import re
import copy

ENABLE_GEOCODER = False

INPUT_PATH = "C:\\Users\\orent\\Documents\\Asuntosijoittaminen\\webscraper\\latest\\data\\"

DELIMITER = '#'

class Geocoder:
	"""
	This class serves as the interface for geocoding addresses.
	Supports: Azure Maps, OSM

	Does not support asynchronity at the moment.

	TODO:
	- Write override method to take the to_str of the Apartment class into account.
	"""
	def __init__(self, Geocoder):
		self.session_obj = requests.Session()

		if (Geocoder == "OSM"):
			self.type = "OSM"
			self.geocoding_endpoint = "https://nominatim.openstreetmap.org/search?street=#STREET#&city=#CITY#&county=#COUNTY#&country=Finland&format=json"
			
		elif (Geocoder == "Azure Maps"):
			self.type = "Azure Maps"
			self.api_key = os.getenv("AZURE_MAPS_API_KEY")
			self.client_id = os.getenv("AZURE_MAPS_CLIENT_ID")
			self.session_obj.params = request_params_dict = {
				"subscription-key":os.getenv("AZURE_MAPS_API_KEY"),
				"api-version":"1.0",
				"x-ms-client-id":os.getenv("AZURE_MAPS_CLIENT_ID")
				}
			self.geocoding_endpoint = "https://atlas.microsoft.com/search/address/json"
		else:
			raise Exception("Undefined Geocoder class.")

	def geocode_address(self, street, district, city):
		if (self.type == "OSM"):
			return self.geocode_address_OSM(street, district, city)
		elif (self.type == "Azure Maps"):
			return self.geocode_address_azure_maps(street, district, city)
		return ""

	def geocode_address_azure_maps(street, district, city):
		geocodes_output = GeocodedData(address)
		geocodes_output.geocoder = "Azure Maps"
		try:
			session_obj.params.update({"query": address})
			response = session_obj.get(self.geocoding_endpoint)

			if (response.status_code == requests.codes.ok):
				# Parse lat and lon
				response_json = json.loads(response.text)
				
				geocodes_output.lat = float(response_json["results"][0]["position"]["lat"])
				geocodes_output.lon = float(response_json["results"][0]["position"]["lon"])

				if "entityType" in response_json["results"][0].keys():
					geocodes_output.lat_lon_type = response_json["results"][0]["entityType"]
				elif "type" in response_json["results"][0].keys():
					geocodes_output.lat_lon_type = response_json["results"][0]["type"]
			else:
				print("Response not ok, problem at: " + self.link)
				# Problem
		except KeyError:
			print("Problem accessing json element at: " + self.link)
			print("response dump: " + response.text)
		except IndexError:
			print("Problem accessing json element at: " + self.link)
			print("response dump: " + response.text)
		return geocodes_output

	def geocode_address_OSM(self, street, district, city):
		geocodes_output = GeocodedData(street, district, city)
		geocodes_output.geocoder = "OSM"
		try:
			#url = self.geocoding_endpoint.replace("{ADDRESS}", address)
			url = self.geocoding_endpoint.replace("#CITY#", city)
			url = url.replace("#STREET#", street)
			url = url.replace("#COUNTY#", district)

			sleep(0.5)
			response = self.session_obj.get(url)

			if (response.status_code == requests.codes.ok):
				response_json = json.loads(response.text)
				geocodes_output.lat = response_json[0]["lat"]
				geocodes_output.lon = response_json[0]["lon"]
				if "display_name" in response_json[0].keys():
					geocodes_output.additional_info = response_json[0]["display_name"]
				if "type" in response_json[0].keys():
					geocodes_output.lat_lon_type = response_json[0]["type"]
				
				postal_code_pattern = "\d{5}"
				#r1 = re.findall(postal_code_pattern, address)
				#geocodes_output.postal_code = r1[0] if len(r1) > 0 else None
				geocodes_output.status = True

		except KeyError:
			print("Problem accessing json element at: " + street + " " + district + " " + city)
			print("response dump: " + response.text)
		except IndexError:
			print("Problem accessing json element at: " + street + " " + district + " " + city)
			print("response dump: " + response.text)
		
		return geocodes_output

class GeocodedData:
	def __init__(self, street = "", district = "", city = ""):
		self.lat = ""
		self.lon = ""
		self.lat_lon_type = ""
		self.additional_info = ""
		self.postal_code = ""
		self.status = False
		self.original_address = street + " " + district + " " + city
		self.geocoder = ""

class Apartment:
	if ENABLE_GEOCODER is True:
		geocoder = Geocoder("OSM")
	else:
		geocoder = None

	def __init__(self, link, type, street, district, city, roomConfiguration, subType, is_forenom, date = None, price = None, size = "", additionalInfo = ""):
		self.link = link
		self.type = type
		self.street = street
		self.district = district
		self.city = city
		self.roomConfiguration = roomConfiguration
		self.size = size
		self.subType = subType
		self.last_price_guess = price.replace("\u20ac", "").replace(" ","").replace("/", "").replace("kk","").replace(",",".")
		self.is_forenom = is_forenom
		self.additionalInfo = additionalInfo
		self.first_seen = date
		self.last_seen = date
		self.time_in_market = None
		self.prices = [(date, price.replace("\u20ac", "").replace(" ","").replace("/", "").replace("kk","").replace(",","."))]
		
		if ENABLE_GEOCODER is True:
			self.geocoded_data = self.geocode_address(street, district, city)
			print("The address was geocoded to: " + str(self.geocoded_data.__dict__))
		else:
			self.geocoded_data = ""

	@classmethod
	def from_dict(cls, dict, type):
		c = cls(
			dict["link"], 
			type, 
			dict["street"], 
			dict["district"], 
			dict["city"], 
			dict["roomConfiguration"], 
			dict["subType"], 
			str(dict["is_forenom"]) if 'is_forenom' in dict else "None", 
			dict["date"], 
			dict["price"], 
			dict["additionalInfo"]["Asuinpinta-ala"] if 'Asuinpinta-ala' in dict["additionalInfo"] else "None",
			dict["additionalInfo"] if 'additionalInfo' in dict else "None"
			)
		return c
	
	def geocode_address(self, street, district, city):
		print("Geocoding address for: " + self.link + " " + street + " " + district + " " + city)
		geocode_temp = self.geocoder.geocode_address(street, district, city)
		return geocode_temp

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
			if isinstance(self.__dict__[o], GeocodedData):
				output_string = output_string + str(self.__dict__[o].__dict__) + delimiter
			else:
				output_string = output_string + str(self.__dict__[o]) + delimiter
		
		output_string = output_string + self.last_price_guess
		# Remove last delimiter
		#output_string = output_string[:-1]
		output_string = output_string + "\n"
		
		# There can be unicode euro characters
		#output_string = output_string.encode('utf8')

		return output_string



def main():
	columns = ["link", "type", "street", "district", "city", "roomConfiguration", "subType", "is_forenom", "prices", "time_in_market", "first_seen", "last_seen", "size", "additionalInfo", "geocoded_data"]
	first_line = ','.join(columns) + "\n"

	scraper_data_to_read = {}
	scraper_data_to_read["yksio-kaksio-vuokrattavat-helsinki-espoo-vantaa-kerrostalo"] = "rent"
	#scraper_data_to_read["kolmio-nelio-myytavat-helsinki-oma-tontti-kerrostalo"] = "sale"
	#scraper_data_to_read["yksio-kaksio-myytavat-espoo-helsinki-vantaa-omatontti-kerrostalo"] = "sale"

	counter = 0
	counter_max = 10

	start_date = datetime(2019, 12, 16)
	end_date = datetime(2020, 6, 6)
	#end_date = datetime(2019, 12, 17)

	print("Starting to loop through scrapers' data.")

	for scraper, type in scraper_data_to_read.items():
		output_string = first_line
		base_path = os.path.join(INPUT_PATH, "#DATE_TEMPLATE#", type, scraper, "data.json")
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
				counter = counter + 1
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
				
				#if counter > counter_max:
				#	break

		for k, v in current_run_dict.items():
			v.update_time_in_market()

		print("Writing the loaded data into a file.")
		output_path = os.path.join(INPUT_PATH, type, scraper)
		Path(output_path).mkdir(parents=True, exist_ok=True)

		with open(os.path.join(output_path, "all_data.csv"), encoding="utf-8", mode="w") as f:
			#f.write(delimiter.join(columns) + '\n')
			for k, v in current_run_dict.items():
				# UnicodeEncodeError: 'charmap' codec can't encode character '\u0308' in position 78: character maps to <undefined>
				f.write(v.to_string(columns))

		with open(os.path.join(output_path, "all_data.json"), encoding="utf-8", mode="w") as f:
			#f.write(delimiter.join(columns) + '\n')
			json.dump(current_run_dict, f)

	print("Done.")

main()