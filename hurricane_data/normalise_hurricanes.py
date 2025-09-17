import json
import os
# import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np
import statistics

dirname = os.path.dirname(__file__)
big_risks = []

def find_distribution(threshold):
	max_risks = []
	global big_risks
	with open(os.path.join(dirname,'./hurricanes-big.json')) as file:
		data = json.load(file)
		for hurr in data:
			risks = []
			for point in hurr['geoJSON']['features']:
				if float(point['properties']['risk']) == 0.01: 
					risks.append(0.0)
					point['properties']['risk'] = 0
				else:
					risks.append(float(point['properties']['risk'])*1.9887285164974275)
					# point['properties']['risk'] = point['properties']['risk']*1.9887285164974275
			# sort_features = sorted(hurr['geoJSON']['features'], key=lambda x: float(x['properties']['risk']), reverse=True)
			risks.sort(reverse=True)
			print(risks)
			max_risks.append(risks[0])
			big_risks = big_risks + risks
		norm_json = json.dumps(data, indent=2, sort_keys=True)
		f = open("hurricanes-norm.json","w")
		f.write(norm_json)
		f.close()
	return max_risks

if __name__ == "__main__":
	print("#### welcome to fud #####")
	threshold = 1
	risks = find_distribution(threshold)

	print('of all points:')
	print('mean is', statistics.mean(big_risks))
	print('mode is', statistics.mode(big_risks))
	print('median is', statistics.median(big_risks))


	print('of maxima:')
	print('mean is', statistics.mean(risks))
	print('mode is', statistics.mode(risks))
	print('median is', statistics.median(risks))
	print('top 15th percentile mean is', np.percentile(risks, 80))
