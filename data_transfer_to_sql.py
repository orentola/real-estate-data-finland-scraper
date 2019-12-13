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

path_test = "C:\\Users\\orent\\Desktop\\data.json"
path_test2 = "C:\\Users\\orent\\Desktop\\testdata2.json"
tulevat_remontit = "C:\\Users\\orent\\Desktop\\remontit.json"
tehdyt_remontit = "C:\\Users\\orent\\Desktop\\tehdyt.json"


with open(path_test, "r") as f:
	data = json.load(f)

example = json.loads(data["0"])
obj_list = []
completed_renovations = []
upcoming_renovations = []

current_date = "tempdate"


for key, value in data.items():
	temp_json = json.loads(value)
	obj = SaleApartment(current_date, temp_json)

	completed_renovations.append(obj.completed_renovations)
	upcoming_renovations.append(obj.upcoming_renovations)
#	if (current_object_is_sale): # same for rentals
#		obj_list.append(SaleApartment(current_date, temp_json))
#	else:
#		obj_list.append(RentalApartment(current_date, temp_json))

with open(tulevat_remontit, "w") as f:
	for l in upcoming_renovations:
		f.write(l + "\n")

with open(tehdyt_remontit, "w") as f:
	for l in completed_renovations:
		f.write(l + "\n")


# Add appropriate exception handling, or then not for those fields that are mandatory. 
class Apartment:
	def __init__(self, current_date, data_dict):
		self.current_date = current_date
		self.link = self.get_initial_data(data_dict,"link")
		self.street = self.get_initial_data(data_dict,"street")
		self.distrcit = self.get_initial_data(data_dict,"district")
		self.city = self.get_initial_data(data_dict,"city")
		
		self.room_configuration = self.get_initial_data(data_dict,"roomConfiguration")
		self.building_year = self.get_initial_data(data_dict,"buildingYear")
		self.subType = self.get_initial_data(data_dict,"subType")
		
		#self.kaupunging_osa = self.get_initial_data(data_dict,"Kaupunginosa","additionalInfo")
		self.kohdenumero = self.get_initial_data(data_dict,"Kohdenumero","additionalInfo")
		self.kerros = int(self.get_initial_data(data_dict,"Kerros","additionalInfo").replace(" ", "").split("/")[0])
		self.kerros_max = int(self.get_initial_data(data_dict,"Kerroksia","additionalInfo"))

		# Convert to float maybe. 
		self.asuinpinta_ala = float(self.parse_number_from_eu_to_us_format(self.get_initial_data(data_dict,"Asuinpinta-ala","additionalInfo").replace("\u00b2", "").replace(" ", "").replace("m", "")))
		self.rooms_description = self.get_initial_data(data_dict,"Huoneiston kokoonpano","additionalInfo")
		self.room_count = float(self.get_initial_data(data_dict,"Huoneita","additionalInfo"))
		self.condition = self.get_initial_data(data_dict,"Kunto","additionalInfo")
		self.kitchen_equipment = self.get_initial_data(data_dict,"Keittiön varusteet","additionalInfo")
		self.balcony = self.get_initial_data(data_dict,"Parveke","additionalInfo")
		self.balcony_info = self.get_initial_data(data_dict,"Parvekkeen lisätiedot","additionalInfo")
		self.bathroom_equipment = self.get_initial_data(data_dict,"Kylpyhuoneen varusteet","additionalInfo")
		self.upcoming_renovations = self.get_initial_data(data_dict,"Tulevat remontit","additionalInfo")
		self.completed_renovations = self.get_initial_data(data_dict,"Tehdyt remontit","additionalInfo")
		
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

	def get_initial_data(self, input_dict, key, additional_dict=None):
		"""
		This is a function for safe access to the dictionary
		whose values may or may not exist

		returns the key if found 

		catches keyerror exception
		"""

		try:
			if additional_dict == None:
				return input_dict[key]
			return input_dict[additional_dict][key]
		except KeyError:
			return ""
		except TypeError:
			print("Error getting initial data. TypeError with fields: " + str(key))
	
	def parse_number_from_eu_to_us_format(self, input):
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



# TBD TO WHICH OBJECT BELONGS TO:
# data_dict["additionalInfo"]["Asumistyyppi"] #Omistus etc.
# data_dict["additionalInfo"]["Vesimaksu"] 
# data_dict["additionalInfo"]["Uudiskohde"]

# TODO
#class RentalApartment(Apartment):
#	def __init__(self, **data_dict):
#		super().__init__()
#		#self.etc

class SaleApartment(Apartment):
	def __init__(self, current_date, data_dict):
		super().__init__(current_date, data_dict)

		self.price_without_debt = self.parse_price(self.get_initial_data(data_dict,"Velaton hinta","additionalInfo"))
		self.sale_price = self.parse_price(self.get_initial_data(data_dict,"Myyntihinta","additionalInfo"))
		self.debt = self.parse_price(self.get_initial_data(data_dict,"Velkaosuus","additionalInfo"))
		self.maintenance_cost_monthly = self.parse_price(self.get_initial_data(data_dict,"Yhtiövastike yhteensä","additionalInfo"))
		self.debt_cost_monthly = self.parse_price(self.get_initial_data(data_dict,"Rahoitusvastike","additionalInfo"))
		self.land_ownership = self.get_initial_data(data_dict,"Tontin omistus","additionalInfo")
		self.total_cost_monthly = self.parse_price(self.get_initial_data(data_dict,"Hoitovastike","additionalInfo"))

class BlobDownloader():
	def __init__(self):
		pass