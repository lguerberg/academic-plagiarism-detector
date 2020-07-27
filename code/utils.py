import math
import unicodedata
import gensim
from gensim.models import KeyedVectors
from nltk.corpus import wordnet
from nltk import re
from nltk import word_tokenize
from nltk import tokenize
import txt_reader as txr
import nltk
from os.path import basename
from nameparser.parser import HumanName
import scraper as sc
import os

from googletrans import Translator
translator = Translator()

def traducir(text):
    return translator.translate(text).text
    
def limpiar_folder(folder):
    files = [f for f in os.listdir(folder)]
    for f in files:
        os.remove(os.path.join(folder, f))

def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)

    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)


def find_owner(doc):

    if basename(doc)[-4:] == '.pdf':
        doc_to_check = preprocess_text(txr.convert_pdf_to_txt(doc,caratula=True))

    else:
         doc_to_check = preprocess_text(txr.convert_docx_to_txt(doc,caratula=True))

    if len(get_human_names(basename(doc))) > 0:
        return get_human_names(basename(doc))[0]

    if len(get_human_names(doc_to_check)[0]) > 0:
        return get_human_names(doc_to_check)[0]

    return "Error al deducir el nombre del creador."


def preprocess_text(text):
    text = text.lower() 
    
    text = text.replace('.','PUNTOSEGUIDO')
    
    #eliminar numeros
    text = ''.join([word for word in text if not word.isdigit()])
    
    #eliminar caracteres unicode
    text = unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode("ascii")
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    
    #eliminar algunas stop words particulares de los documentos
    special_stop_words = ['cuestionario','preguntas','respuestas','responder','trabajo','practico','cuatrimestre','pagina']
    text  = ' '.join([word.lower() for word in re.split(r"\W+",text) if word.lower() not in special_stop_words])
    
    #eliminar palabras de menos de 1 letra que no sea vocal
    text  = ' '.join([word.lower() for word in re.split(r"\W+",text) if len(word)>1 or word in ['a','e','i','o','u']])
    
    text = text.replace('puntoseguido','.')
    return text


def is_in_vocabulary(sentence,trained_model):
    words = tokenize.word_tokenize(sentence)
    return [word for word in words if word in trained_model.wv.vocab ]

def is_a_question_word(word):
    return word in ['cuales','que','de','explique','desarrolle','describa','¿','grafique']

def cargar_modelo(path):
    return KeyedVectors.load_word2vec_format(path,limit=100500)

def get_synonyms(word):
    synonyms = []

    for syn in wordnet.synsets(word,lang='spa'):
        for l in syn.lemma_names('spa'):
            synonyms.append(l)


    return set(synonyms)

def check_synonyms_similarities(word_to_check,words_to_compare):
    cant = 0
    word1_synonyms = get_synonyms(word_to_check)

    for word in words_to_compare:
        if word in word1_synonyms:
            cant = cant + 1
 
    return cant

def calcular_porcentaje_palabras(porcentaje,palabras):
    cant_palabras = math.floor(len(palabras)*porcentaje)

    if cant_palabras <= 5:
        return 10

    return cant_palabras


def parsear_plagio(file,sentence1,sentence2,similaridad):
    return file  +  ";" +  sentence1 + ";" + sentence2 + ";" + str(round(similaridad*100,2)) + '%' + '\n'


def configurar_deteccion():
    plagio_algorithm = ""
    trained_model = None

    print("Porfavor, elija el algoritmo con el que se va a trabajar: -")

    while not plagio_algorithm in ['A','B']:
        plagio_algorithm = input("A -> COSINE SIMILARITY\nB -> WORDNET\nIngrese A o B: ")

    #Carga modelo entrenado
    #-----------------O----------------------
    if plagio_algorithm == "A":
        print("Cargando modelo...")
        trained_model = cargar_modelo (r"Modelos\Word2Vec Model.vec")

        print("Modelo cargado")
    #-----------------O----------------------
    else:
        trained_model = None

    return [plagio_algorithm,trained_model]

def calcular_porcentaje_plagio(df_plagios,doc):
    cant_oraciones_total = len(tokenize.sent_tokenize(doc))
    cant_oraciones_plagiadas = len(df_plagios['Oracion Chequeada'].drop_duplicates().to_list())

    return math.floor((cant_oraciones_plagiadas / cant_oraciones_total) * 100)

def exportar_resultados(df_plagios,plagio_algorithm):
    if plagio_algorithm == 'A':
        df_plagios.to_csv("Resultados/Plagios - Cosine Similarity.csv",sep=';',index=False)
    else:
        df_plagios.to_csv("Resultados/Plagios - Wordnet.csv",sep=';',index=False)

def get_algoritmo_by_id(id):
    if id == 'A':
        return 'Cosine Similarity'
    else:
        return 'Wordnet'

def scrapear_web(tema,dir_to_save,max_pages=20):

    #limpiar la carpeta de documentos scrapeados
    limpiar_folder(dir_to_save)

    #scrape
    cant = 0
    query = tema + " Trabajo practico"

    cant = sc.google_search_and_save(query,dir_to_save,max_pages)
    print("Se han descargado de la web ,",str(cant)," archivos.")

