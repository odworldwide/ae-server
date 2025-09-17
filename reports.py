from datetime import datetime
import chat
import market

name = ''


def new_hurricane(hurricane, sysName):
	chat.update(sysName, '### NEW STORM: '+ hurricane['metadata']['name'], 'weather')
	print('### NEW STORM: '+ hurricane['metadata']['name'])

#tracks the hurricane
def track(point, sysName, time_remaining):
	date = datetime.strptime(point['properties']['date'], "%m-%d-%Y")
	time = point['properties']['time']
	lon = str(point['geometry']['coordinates'][0]) + 'E'
	lat = str(point['geometry']['coordinates'][1]) + 'N'
	if time_remaining % 4 == 0:
		chat.update(sysName, 'the time is ' + time + ' on '+ date.strftime('%m-%d') + ', location ' + lat + ', '+ lon, 'weather')
		chat.update(sysName, 'max wind speed is '+ point['properties']['speed'] + ' knots', 'weather')
		chat.update(sysName, 'this storm is now classified as a ' + point['properties']['report'], 'weather')

	if time_remaining > 1:
		time_remaining = time_remaining-1
	return time_remaining