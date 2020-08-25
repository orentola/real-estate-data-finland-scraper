"""

The purpose of this script is to transform the scraped JSON into 
apartment specific (data transfer) objects. Data validation and the mapping
of the JSON data into the downstream data storages will take place here.

TODO:
- Build an object representation of the daily JSON data dump, important to note
that the schema of the data dump can change and this is the place where the validation
will take place.
--> Done for SaleApartment
--> RentApartment needs to be implemented
- Find all files that need to be transformed.
- Build (and/or re-use) the data transfer object for transferring data to correct
endpoints in a SQL database.
- Build any logic for creating any new fields etc (e.g. parsing something from the text etc.)
--> Mostly implemented

"""

import json
import os
import requests
import re
import copy
from datetime import datetime

# Add appropriate exception handling, or then not for those fields that are mandatory. 
class Apartment:
	def __init__(self, current_date, data_dict, geo_coder=None):
		
		self.current_date = current_date
		self.link = self.get_initial_data(data_dict,"link")
		self.street = self.get_initial_data(data_dict,"street")
		self.district = self.get_initial_data(data_dict,"district")
		self.city = self.get_initial_data(data_dict,"city")
		self.room_configuration = self.get_initial_data(data_dict,"roomConfiguration")
		self.building_year = self.get_initial_data(data_dict,"buildingYear")
		self.subType = self.get_initial_data(data_dict,"subType")
		
		self.set_address()

		#self.kaupunging_osa = self.get_initial_data(data_dict,"Kaupunginosa","additionalInfo")
		self.oikotie_id = self.get_initial_data(data_dict,"Kohdenumero","additionalInfo")
		self.floor_number = self.get_initial_data(data_dict,"Kerros","additionalInfo").replace(" ", "").split("/")[0]
		self.floor_number_max = self.get_initial_data(data_dict,"Kerroksia","additionalInfo")

		# Convert to float maybe. 

		# TODO: Move the parsing of numeric data into a separate function
		self.size = float(self.parse_number_from_eu_to_us_format(self.get_initial_data(data_dict,"Asuinpinta-ala","additionalInfo").replace("\u00b2", "").replace(" ", "").replace("m", "")))
		self.rooms_description = self.get_initial_data(data_dict,"Huoneiston kokoonpano","additionalInfo", "numeric")
		self.room_count = float(self.get_initial_data(data_dict,"Huoneita","additionalInfo", "numeric"))
		self.condition = self.get_initial_data(data_dict,"Kunto","additionalInfo")
		self.kitchen_equipment = self.get_initial_data(data_dict,"Keittiön varusteet","additionalInfo")
		self.balcony = self.get_initial_data(data_dict,"Parveke","additionalInfo")
		self.balcony_info = self.get_initial_data(data_dict,"Parvekkeen lisätiedot","additionalInfo")
		self.bathroom_equipment = self.get_initial_data(data_dict,"Kylpyhuoneen varusteet","additionalInfo")
		self.upcoming_renovations = self.get_initial_data(data_dict,"Tulevat remontit","additionalInfo")
		self.completed_renovations = self.get_initial_data(data_dict,"Tehdyt remontit","additionalInfo")
		self.ownership_type = self.get_initial_data(data_dict,"Asumistyyppi","additionalInfo")
		self.new_apartment = self.get_initial_data(data_dict,"Uudiskohde","additionalInfo")

		# TODO handle sauna string better
		self.has_sauna = self.get_initial_data(data_dict,"Taloyhtiössä on sauna","additionalInfo")
		
		self.building_type = self.get_initial_data(data_dict,"Rakennuksen tyyppi","additionalInfo")
		self.has_elevator = self.get_initial_data(data_dict,"Hissi","additionalInfo")
		self.common_sauna = self.get_initial_data(data_dict,"Taloyhtiössä on sauna","additionalInfo")

		self.surface_materials = self.get_initial_data(data_dict,"Pintamateriaalit","additionalInfo")
		self.views = self.get_initial_data(data_dict,"Näkymät","additionalInfo")
		self.services = self.get_initial_data(data_dict,"Palvelut","additionalInfo")
		self.window_direction = self.get_initial_data(data_dict,"Ikkunoiden suunta","additionalInfo")
		self.transportation = self.get_initial_data(data_dict,"Liikenneyhteydet","additionalInfo")

		self.geocoded_data = None
		self.geo_coder = geo_coder

		# Status of renovations, completed, upcoming
		#self.set_completed_renovations()

		#self.set_renovation_status_pipes() 
		#self.set_renovation_status_roof()
		#self.set_renovation_status_outer_walls()
		#self.set_renovation_status_balcony()
		#self.set_renovation_status_windows()
		#self.set_renovation_status_elevator()

	#def set_completed_renovations(self):
	#	# TODO TO IDENTIFY WHICH RENOVATIONS ARE COMPLETED, this is not trivial
	#	keywords_windows = ["ikkuna", "ikkunoiden"]
	#	keywords_pipes = ["putkisaneeraus", "putkiremontin yht"]

	#	self._completed_renovations = {
	#		"pipes":"",
	#		"roof":"",
	#		"outer_walls":"",
	#		"balcony":"",
	#		"windows":"",
	#		"elevator":""
	#		}

	#def get_completed_renovations(self):
	#	return self._completed_renovations
	#completed_renovations = propety(set_completed_renovations, get_completed_renovations)

	def get_initial_data(self, input_dict, key, additional_dict=None, expected_output_type="string"):
		"""
		This is a function for safe access to the dictionary
		whose values may or may not exist

		returns the key if found 

		catches keyerror exception
		"""

		try:
			if additional_dict == None:
				output = input_dict[key]
			else:
				output = input_dict[additional_dict][key]
			if (len(output) == 0):
				if (expected_output_type == "numeric"):
					return 0	
				return ""
			return output.replace("\n", "").replace("\x95", "")

		except KeyError:
			if expected_output_type == "numeric":
				return 0
			return ""
		except TypeError:
			print("Error getting initial data. TypeError with fields: " + str(key))
	
	def parse_number_from_eu_to_us_format(self, input):
		if input == "":
			return 0
		
		return input.replace(",", ".")

	def parse_price(self, input):
		"""
		Takes the raw string price as input
		Outputs the float representation of the input
		"""

		if input == None or len(input) == 0:
			return 0.0

		try:
			return float(input.replace("\u20ac", "").replace(" ","").replace("/", "").replace("kk","").replace(",","."))
		except ValueError:
			print("Problem parsing string to float.")
			print("Problem with string: " + input)
			print("Parsed string: " + input.replace("\u20ac", "").replace(" ","").replace("/", "").replace("kk","").replace(",","."))

	def get_address(self):
		return self._address
	def set_address(self):
		self._address = self.street + " " + self.district + " " + self.city
	address = property(get_address, set_address)


	def get_schema(self, delimiter=','):
		data = self.__dict__
		output_str = ""

		for key, value in data.items():
			output_str = output_str + delimiter + str(key)

		return output_str.replace(delimiter, "", 1)[:-1]

	def as_string(self, delimiter=','):
		data = self.__dict__
		output_str = ""

		for key, value in data.items():
			# This should be implemented recursively to account for arbitrary data structures
			if (isinstance(value, GeocodedData) == True or isinstance(value, Geocoder) == True):
				for k1, v1 in value.__dict__.items():
					output_str = output_str + delimiter + str(v1)
			else:
				output_str = output_str + delimiter + str(value)
		
		return output_str.replace(delimiter, "", 1) # remove first delimiter

	def geocode_address(self):
		if (self.geo_coder == None):
			print("No Geocoder set for this object.")
			self.geocoded_data = ""
		else:
			self.geocoded_data = self.geo_coder.geocode_address(self.address)

class RentalApartment(Apartment):
	def __init__(self, current_date, data_dict, geo_coder=None):
		super().__init__(current_date, data_dict, geo_coder)

		#self.rent = self.parse_price((self.get_initial_data(data_dict, "price"))
		self.rent = self.parse_price(self.get_initial_data(data_dict, "Vuokra/kk", "additionalInfo"))
		self.deposit_additional_info = self.get_initial_data(data_dict, "Lisätietoa vakuudesta", "additionalInfo")
		self.rental_period = self.get_initial_data(data_dict, "Vuokra-aika", "additionalInfo")
		self.deposit_amount = self.get_initial_data(data_dict, "Vakuus", "additionalInfo")
		self.rent_increase_principles = self.get_initial_data(data_dict, "Vuokrankorotusperusteet", "additionalInfo")
		self.is_furnished = self.get_initial_data(data_dict, "Vuokrataan kalustettuna", "additionalInfo")
		self.other_terms = self.get_initial_data(data_dict, "Muut ehdot", "additionalInfo")
		self.set_is_forenom()
		
	def get_is_forenom(self):
		return self._is_forenom

	def set_is_forenom(self):
		self._is_forenom = True if self.other_terms.find("Forenom") != -1 else False
	is_forenom = property(get_is_forenom, set_is_forenom)

class SaleApartment(Apartment):
	def __init__(self, current_date, data_dict, geo_coder=None):
		super().__init__(current_date, data_dict)

		# TODO Implement how to detect renovations

		self.price_without_debt = self.parse_price(self.get_initial_data(data_dict,"Velaton hinta","additionalInfo"))
		self.sale_price = self.parse_price(self.get_initial_data(data_dict,"Myyntihinta","additionalInfo"))
		self.debt = self.parse_price(self.get_initial_data(data_dict,"Velkaosuus","additionalInfo"))
		self.maintenance_cost_monthly = self.parse_price(self.get_initial_data(data_dict,"Yhtiövastike yhteensä","additionalInfo"))
		self.debt_cost_monthly = self.parse_price(self.get_initial_data(data_dict,"Rahoitusvastike","additionalInfo"))
		self.land_ownership = self.get_initial_data(data_dict,"Tontin omistus","additionalInfo")
		self.total_cost_monthly = self.parse_price(self.get_initial_data(data_dict,"Hoitovastike","additionalInfo"))


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
			self.geocoding_endpoint = "https://nominatim.openstreetmap.org/search/{ADDRESS}?format=json&country=Finland"
			
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

	def geocode_address(self, address):
		if (self.type == "OSM"):
			return geocode_address_OSM(self, address)
		elif (self.type == "Azure Maps"):
			return geocode_address_azure_maps(self, address)
		return ""

	def geocode_address_azure_maps(self, address):
		geocodes_output = GeocodedData()
		try:
			session_obj.params.update({"query": address})
			response = session_obj.get(geocoding_endpoint)

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

	def geocode_address_OSM(self, address):
		geocodes_output = GeocodedData()
		try:
			url = geocoding_endpoint.replace("{ADDRESS}", self.address)
			response = session_obj.get(url)

			if (response.status_code == requests.codes.ok):
				response_json = json.loads(response.text)
				geocodes_output.lat = response_json[0]["lat"]
				geocodes_output.lon = response_json[0]["lon"]
				if "display_name" in response_json[0].keys():
					geocodes_output.additional_info = response_json[0]["display_name"]
				if "type" in response_json[0].keys():
					geocodes_output.lat_lon_type = response_json[0]["type"]
				
				postal_code_pattern = "\d{5}"
				r1 = re.findall(postal_code_pattern, self.additional_info)
				geocodes_output.postal_code = r1[0]
				geocodes_output.status = True

		except KeyError:
			print("Problem accessing json element at: " + self.link)
			print("response dump: " + response.text)
		except IndexError:
			print("Problem accessing json element at: " + self.link)
			print("response dump: " + response.text)
		
		return geocodes_output

class GeocodedData:
	def __init__(self):
		self.lat = ""
		self.lon = ""
		self.lat_lon_type = ""
		self.additional_info = ""
		self.postal_code = ""
		self.status = False

class DataReader:
	def __init__(self, type, path=None):
		self.type = type
		self.path = path
		self.sale_objects_list = []
		self.sale_objects_list_unique = []
		
		self.rent_objects_list = []
		self.rent_objects_list_unique = []

	def read_all_data_to_objects(self):
		if (self.type == "local"):
			"""
			The data needs to reside in path + /YYYY-MM-DD/{rent|sale}/{scraper_name}/data.json

			TODO: Add exception handling

			1. Traverse each folder in the path until .json data file is found.
			2. Create the corresponding sale or rental apartment ouf to the json data.
			3. Add the data into the corresponding object list
			"""

			# Find all YYYY-MM-DD patterns in the folder 
			date_folders_list = next(os.walk(self.path))[1]
			
			# Peek into each folder
			for fol in date_folders_list:
				current_path_date = os.path.join(self.path, fol)
				current_date = fol

				# Update rental data
				current_rental_scrapers = next(os.walk(os.path.join(current_path_date, "rent")))[1]

				for rs in current_rental_scrapers:
					self.update_sale_and_rent_lists(os.path.join(current_path_date, "rent", rs, "data.json"), "rent", current_date)

				# Update sales data
				current_sale_scrapers = next(os.walk(os.path.join(current_path_date, "sale")))[1]
				for rs in current_sale_scrapers:
					self.update_sale_and_rent_lists(os.path.join(current_path_date, "sale", rs, "data.json"), "sale", current_date)


	def update_sale_and_rent_lists(self, path, type, current_date):
		with open(path, "r") as f:
			current_data = json.load(f)

		for key, value in current_data.items():
			temp_json = json.loads(value)
			if (type == "rent"):
				obj = RentalApartment(current_date, temp_json)
				# Add a deep copy of the object to the list, not just the reference
				self.rent_objects_list.append(copy.deepcopy(obj))

			elif (type == "sale"):
				obj = SaleApartment(current_date, temp_json)
				# Add a deep copy of the object to the list, not just the reference
				self.sale_objects_list.append(copy.deepcopy(obj))

	def write_all_data_to_path(self, path, unique=False):	
		""" 
		TODO: Better exception handling
		"""

		if unique == False:
			rent_objects_list = self.rent_objects_list
			sale_objects_list = self.sale_objects_list
		else:
			rent_objects_list = self.rent_objects_list_unique
			sale_objects_list = self.sale_objects_list_unique

		rent_output_list = []
		sale_output_list = []

		if (os.path.exists(path) == False):
			os.makedirs(path)

		# Write rentals 
		rent_output_list.append(rent_objects_list[0].get_schema("#") + '\n')

		for r in rent_objects_list:
			rent_output_list.append(r.as_string("#") + '\n')

		with open(os.path.join(path, "rent.csv"), "w", encoding='utf-8') as f:
			for row in rent_output_list:
				f.write(row)
		
		# Write sale
		sale_output_list.append(sale_objects_list[0].get_schema("#") + '\n')

		for s in sale_objects_list:
			sale_output_list.append(s.as_string("#") + '\n')

		with open(os.path.join(path, "sale.csv"), "w", encoding='utf-8') as f:
			for row in sale_output_list:
				f.write(row)

	def update_unique_lists(self):
		"""
		Creates unique lists of the listings based on the latest data.

		Uniqueness is defined by the link to the property. 
		The last piece of data is needed based on self.current_date

		The temp dicts will be of form [link] = [current_date, current_object]

		TODO
		- Check that the reference goes correctly within the loops (r and s)
		- Refactor this in a way that it makes sense, duplicative code at the moment

		"""
		
		r_temp_dict = {}
		for r in self.rent_objects_list:	
			if r.link in r_temp_dict:
				# If newer found, update
				if (datetime.strptime(r_temp_dict[r.link][0], "%Y-%m-%d") < datetime.strptime(r.current_date, "%Y-%m-%d")):
					#TODO
					# This might be dangerous, need to make sure r actually points to the underlying object in this case which I am unsure
					r_temp_dict[r.link] = [r.current_date, r]
			else:
				r_temp_dict[r.link] = [r.current_date, r]

		for key, value in r_temp_dict.items():
			self.rent_objects_list_unique.append(copy.deepcopy(value[1]))

		s_temp_dict = {}
		for s in self.sale_objects_list:	
			if s.link in s_temp_dict:
				# If newer found, update
				if (datetime.strptime(s_temp_dict[s.link][0], "%Y-%m-%d") < datetime.strptime(s.current_date, "%Y-%m-%d")):
					#TODO
					# This might be dangerous, need to make sure r actually points to the underlying object in this case which I am unsure
					s_temp_dict[s.link] = [s.current_date, s]
			else:
				s_temp_dict[s.link] = [s.current_date, s]
		
		for key, value in s_temp_dict.items():
			self.sale_objects_list_unique.append(copy.deepcopy(value[1]))


def main():
	data_path = "C:\\Users\\orent\\Documents\\Asuntosijoittaminen\\webscraper\\latest\\data\\"
	output_path = "C:\\Users\\orent\\Documents\\Asuntosijoittaminen\\webscraper\\latest\\"
	reader = DataReader("local", data_path)
	reader.read_all_data_to_objects()
	reader.update_unique_lists()
	reader.write_all_data_to_path(output_path, unique=True)

main()

