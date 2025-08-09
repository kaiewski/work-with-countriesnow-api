#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import requests
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('tkagg')

if hasattr(sys.stdout, 'reconfigure'):
	sys.stdout.reconfigure(encoding='utf-8')

class Parser:
	"""
	A simple information parser.

	Attributes:
		main_url(str): basic resource link.
	"""

	def __init__(self, url: str) -> None:
		"""Class initialization."""

		self.main_url = url

	def getCountryPopulation(self, country: str) -> dict[int, int]:
		"""
		Receive the population of a specific country.

		Accepts the country, sends a POST request, and returns 
		the response body as a dictionary of numeric values 
		like year:population.
		"""

		url = self.main_url + '/population'
		payload = {'country': country}

		response = requests.request('POST', url, data=payload)
		data = json.loads(response.text)
		data_dict = {d['year']: d['value'] for d in 
					data['data']['populationCounts']}

		return data_dict

	def getCities(self, country: str) -> list:
		"""
		Receive a list of cities in a specific country.

		Accepts the country, sends a POST request, and returns 
		the response body as list of strings.
		"""

		url = self.main_url + '/cities'
		payload = {'country': country}

		response = requests.request('POST', url, data=payload)
		data = json.loads(response.text)
		cities = [item for item in data['data']]

		return cities

	def getCitiesPopulation(self, year: int, country: str, limit: int) -> dict[str, int]:
		"""
		Receive the population of the top N cities of a specific country.

		Accepts year, country and number of places in the top,
		sends a POST request, and returns the response body as
		dictionary of string and integer like city:population.
		"""

		url = self.main_url + '/population/cities/filter'
		city_names = []
		city_populations = []
		payload = {
			'country': country,
			'limit': limit,
			'orderBy': 'population',
			'order': 'dsc'}

		response = requests.request('POST', url, data=payload)
		data = json.loads(response.text)
		cities = [item for item in data['data']]

		for city in cities:
			city_names.append(city.get('city').capitalize())
			year_info = city.get('populationCounts')
			for i in range(len(year_info)):
				if int(year_info[i].get('year')) == int(year):
					city_populations.append(year_info[i].get('value'))
					break

		ascending_cities = dict(zip(city_names, city_populations))

		return ascending_cities

	def getImageCountryFlag(self, country: str) -> str:
		"""Receive the url to the flag of a specific country."""

		url = self.main_url + '/flag/images'
		payload = {"country": country}

		response = requests.request("POST", url, data=payload)
		data = json.loads(response.text)
		flag_image = data['data'].get('flag')
		
		return flag_image

	def getUnicodeCountryFlag(self, country: str) -> str:
		"""Receive the Unicode of the flag of a specific country."""

		url = self.main_url + '/flag/unicode'
		payload = {"country": country}

		response = requests.request("POST", url, data=payload)
		data = json.loads(response.text)
		unicode_flag = data['data'].get('unicodeFlag')
		
		return unicode_flag

	def getCountriesCurrency(self) -> dict[str, str]:
		"""
		Receive the currency of all countries.

		Sends a GET request, and returns the response body as
		dictionary of string like country:currency.
		"""

		url = self.main_url + '/currency'
		country_names = []
		country_currencies = []

		response = requests.request("GET", url)
		data = json.loads(response.text)
		countries = [item for item in data['data']]

		for country in countries:
			country_names.append(country.get('name'))
			country_currencies.append(country.get('currency'))

		countries_currency = dict(zip(country_names, country_currencies))

		return countries_currency

	def getDialCodeWithCurrency(self) -> dict[str, tuple[str, str]]:
		"""
		Receive the currency and dial codes of all countries.

		Sends a GET request, and returns the response body as
		dictionary of string like country:(currency, dial_code).
		"""

		currencies = self.getCountriesCurrency()
		url = self.main_url + '/codes'

		response = requests.request("GET", url)
		data = json.loads(response.text)
		countries = [item for item in data['data']]

		new_info = {}
		for country, curr_code in currencies.items():
			for entry in countries:
				if entry.get('name') == country:
					dial_code = entry.get('dial_code')
					new_info[country] = f"{curr_code}, {dial_code}"
					break

		return new_info

	def getDataPopulation(self, info: dict) -> list[int, int]:
		"""Receive a list where each element is a list of key and value."""

		return [list(pair) for pair in info.items()]

	def drawSinglePlot(self, country: str) -> None:
		"""
		Receive a graph of population change for the specific country.

		Receives a list of keys and values as input, 
		draws a graph of their dependencies on the screen.
		"""

		data = self.getDataPopulation(parser.getCountryPopulation(country))
		xAxis = []
		yAxis = []

		for info in data:
			xAxis.append(info[0])
			yAxis.append(info[1]/1000000)

		plt.figure(figsize=(5, 2.7), layout='constrained')
		plt.plot(xAxis, yAxis, 'o-')

		self.drawPlot('Year [-]', 'Population [mil.]', 'Compare population by year', True)

	def drawComparingCountriesPlot(self, country_names: list) -> None:
		"""
		Receive a graph comparing the population of the specific countries.
		
		Received as input a list of country names and draws 
		a graph of their population dependencies.
		"""

		xAxis = []
		yAxis = []
		plt.figure(figsize=(5, 2.7), layout='constrained')
		
		for country in country_names:
			data = self.getDataPopulation(parser.getCountryPopulation(country))
			for info in data:
				xAxis.append(info[0])
				yAxis.append(info[1]/1000000)

			plt.plot(xAxis, yAxis, 'o-', label=country_names[int(country_names.index(country))].title())
			plt.legend()
			xAxis = []
			yAxis = []

		self.drawPlot('Year [-]', 'Population [mil.]', 'Comparing populations for countries', True)

	def drawComparingCitiesPlot(self, city_names: list) -> None:
		"""
		Receive a graph comparing the population of the specific cities.

		Receives a list of cities to be compared as input, 
		then make POST requests for all the specified cities
		and displays their population dependencies in a single graph.
		"""

		xAxis = []
		yAxis = []
		plt.figure(figsize=(5, 2.7), layout='constrained')	
		url = self.main_url + '/population/cities'

		for city in city_names:
			payload = {
				'city': city.title()
			}
			response = requests.request("POST", url, data=payload)
			data = json.loads(response.text)
			info = data['data'].get('populationCounts')
			for year in info:
				xAxis.append(year.get('year'))
				yAxis.append(int(year.get('value'))/1000000)

			plt.plot(xAxis, yAxis, 'o-', label=city_names[int(city_names.index(city))].title())
			plt.legend()
			xAxis = []
			yAxis = []

		self.drawPlot('Year [-]', 'Population [mil.]', 'Comparing populations for cities', True)

	def drawPlot(self, xlabel: str, ylabel: str, title: str, grid: bool) -> None:
		"""
		Draw a graph according to the specified parameters.

		Attributes:
			xlabel(str): label x plot 
			ylabel(str): label y plot 
			title(str): title of plot
			grid(bool): on/off plot grid
		"""

		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.title(title)
		plt.grid(grid)
		plt.show()

if __name__ == '__main__':
	try:
		parser = Parser('https://countriesnow.space/api/v0.1/countries')
		# parser.getCountryPopulation('Czech Republic')
		# parser.getCities('Czech Republic')
		# parser.getCitiesPopulation(2008, 'Czech Republic', 10)
		# parser.getImageCountryFlag('Czech Republic')
		# parser.getUnicodeCountryFlag('Czech Republic')
		# parser.getCountriesCurrency()
		# parser.getDialCodeWithCurrency()

		# parser.drawSinglePlot('Czech Republic')
		# parser.drawComparingCountriesPlot(['Czech Republic', 'Poland', 'Germany', 'Austria', 'Slovak Republic'])
		# parser.drawComparingCitiesPlot(['Plzen', 'Praha', 'Ostrava', 'Brno'])

	except Exception as e:
		print(f'[Main] Error in main function: \n\t{e}')
