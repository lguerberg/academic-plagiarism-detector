import requests
import pandas as pd
from nltk import tokenize
from nltk import word_tokenize
from googletrans import Translator
import utils as ut
translator = Translator()

def inicializar_scores(categories):
	sum_scores = pd.DataFrame(columns=categories)
	sum_scores = sum_scores.append(pd.Series(0, index=sum_scores.columns), ignore_index=True)
	return sum_scores

def update_scores(actual_scores,new_data):
	categories = actual_scores.columns
	for key in new_data:
		if key == 'categories':
			categories = new_data[key]
			for category in categories:
				actual_scores[category['name']][0] = actual_scores[category['name']][0] + category['score']
	return actual_scores

def get_argmax(scores):
	max = -1
	category = ""

	for (column_name, column_data) in scores.iteritems():
		if(column_data.values[0] > max):
			max = column_data.values[0]
			category = column_name

	return translator.translate(category,dest="spanish").text.capitalize()

def clasificar_documento(doc,treshold=0.3,categories=['economy','technology','health','science-environment','business','politics','entertainment','sport']):
	try:
		doc_english = translator.translate(ut.preprocess_text(doc)).text
		sentences = tokenize.sent_tokenize(doc_english)
		
		sum_scores = inicializar_scores(categories)
		for sent in sentences[5:10]:
			url = 'https://api.dandelion.eu/datatxt/cl/v1'

			payload = {'text':sent,
			'model':"54cf2e1c-e48a-4c14-bb96-31dc11f84eac",
			'token':'cbbf951e9b704ea4a3ddfd09d27bed1d',
			'min_score':treshold}
			
			jsonData = requests.get(url, params=payload).json()
			sum_scores = update_scores(sum_scores,jsonData)

		return get_argmax(sum_scores)
	except:
		print("Error al categorizar el texto.")
