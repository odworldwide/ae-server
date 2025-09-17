# from scipy.stats import skewnorm
import numpy
import json

def add_noise(risk):
	threshold_risk = risk

	# make sure we can't send sd below 0
	if risk >= 1:
		threshold_risk = 0.99

	#noise amount varies depending on how close you are to 0
	risk = risk+numpy.random.normal(0.2, (1-threshold_risk)/25)

	if risk < 0:
		risk = 0
	return risk


def get_json(obj):
	return json.loads(
		json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
	)