import csv
import re
import json
import regex as re
from datetime import datetime
from geojson import Point, LineString, Feature, FeatureCollection, MultiPoint
import pyproj as proj
from geopy import distance

#static files
from storm_classifier import classifier

norm_factor=1

class City(dict):
	def __init__(self, name, country, region, pop, distance, risk_factor, lat, lon):
		dict.__init__(self, name=name, country=country, region = region, 
			pop = pop, distance = distance, risk_factor = risk_factor, lat=lat, lon=lon)


def normalise(list):
	global norm_factor
	for hurr in list:
		for point in hurr['geoJSON']['features']:

			#only keep top 2 risks
			del point['properties']['proximity'][2:]

			for city in point['properties']['proximity']:
				city['risk_factor'] = 4*city['risk_factor']/norm_factor
			if len(point['properties']['proximity']) > 0:
				point['properties']['risk'] = point['properties']['proximity'][0]['risk_factor']
				point['properties']['highest_risk'] = point['properties']['proximity'][0]['name']
			else:
				point['properties']['risk'] = 0.01
				point['properties']['highest_risk'] = None

def get_proximity(lat, lon, name, cat, speed):
	global norm_factor
	center_point = [{'lat': lat, 'lng': lon}]
	radius = 500

	proximity = []

	with open('cities_pop.csv', newline='') as csvfile:
		cities = csv.reader(csvfile, delimiter=',')
		for row in cities:
			#key Country,City,AccentCity,Region,Population,Latitude,Longitude
			test_point = [{'lat': float(row[5]), 'lng': float(row[6])}]
			center_point_tuple = tuple(center_point[0].values())
			test_point_tuple = tuple(test_point[0].values())

			dist = distance.distance(center_point_tuple, test_point_tuple).km

			if dist <= radius:
				pop = float(row[4])
				risk_factor = ((500.0-dist)/500.0)*pop*cat['risk']*speed
				proximity.append(City(row[2], row[0], row[3], pop, dist, risk_factor, float(row[5]), float(row[6])))

				if risk_factor > norm_factor:
					norm_factor = risk_factor

	return proximity

def calculate_risk(lat, lon, name, cat, speed):
	prox = get_proximity(lat, lon, name, cat, speed)
	prox.sort(key=lambda x: x['risk_factor'], reverse=True)
	return prox

#need to include landfall

if __name__ == "__main__":
	hurricane = []
	list = []
	name='ABLE'
	num=1

	print(name, '-- hurricane number', num)
	with open('hurdat.csv', newline='') as csvfile:
		data = csv.reader(csvfile, delimiter=',')
		# print(data)

		old=[]
		for row in data:
			old.append(row)

	for index, row in enumerate(old[1:], start=1):
		coord=[]
		if row[4] != '':
			if 'W' in row[5]:
				coord.append(-float(re.sub('W', '', row[5])))
			elif 'E' in row[5]:
				coord.append(float(re.sub('E', '', row[5])))
			else: break

			if 'N' in row[4]:
				coord.append(float(re.sub('N', '', row[4])))
			elif 'S' in row[4]:
				coord.append(-float(re.sub('S', '', row[4])))
			else: break

			cat = classifier[row[3].strip()]
			prox = calculate_risk(coord[1], coord[0], name, cat, float(row[6]))

			time = '0000' if row[1] == '0' else row[1]
			time = time[:-2] + ':' + time[-2:]

			landfall = False
			if row[2].strip() == 'L':
				landfall = True

			date = datetime.strptime(row[0], "%Y%m%d")
			point = Feature(geometry=Point(coord), 
				properties={
					'class': row[3].strip(), 
					'date': date.strftime('%m-%d-%Y'),
					'time': time,
					'risk': cat['risk'],
					'report': cat['description'],
					'speed': row[6],
					'landfall': landfall,
					'proximity': prox
				})
			hurricane.append(point)
			first_step=False
		else:
			list.append(
				{
					'geoJSON': FeatureCollection(hurricane),
					'metadata': {'number': num, 'name': name }
				})
			name = row[1].strip()
			hurricane=[]
			num = num+1
			print(name, '-- hurricane number', num)
			first_step=True
			# if num > 1:
			# 	break


	normalise(list)
	json = json.dumps(list, indent=2, sort_keys=True)
	f = open("hurricanes-big2.json","w")
	f.write(json)
	f.close()
