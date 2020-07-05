#import de librerias
#-----------------O----------------------
import utils as ut
import pandas as pd
import warnings
import os
from os.path import basename
import txt_reader as txr
import plagio_detector as pg
import text_classifier as classifier
warnings.filterwarnings("ignore")
#-----------------O----------------------


print("-----------------O----------------------")
config = ut.configurar_deteccion()
plagio_algorithm = config[0]
trained_model = config[1]
print("-----------------O----------------------")


#carga documento a chequear plagios
#-----------------O----------------------
path_to_check = r"D:\TP NLP\Input\\"
documentos_input = os.listdir(path_to_check)
path_to_check = path_to_check + documentos_input[0]

print("Cargando documento: ", path_to_check)
doc_to_check = txr.convert_docx_to_txt(path_to_check)
plagios = ""
tema_documento = classifier.clasificar_documento(doc_to_check)
#-----------------O----------------------

#cargar documentos contra los que comparar
print("-----------------O----------------------")
directorio_documentos = r'D:\TP NLP\Dataset'
documentos = os.listdir(directorio_documentos)
ut.scrapear_web(tema_documento,directorio_documentos + r'\Scraped') #se puede especificar el numero maximo de documentos a descargar. Por defecto es 20 (tener en cuenta que solo descarga pdf y docx, por lo que
                                                                    # de los 20 solo descargara un promedio de 5 que son los que suelen ser pdf o docx)                                                
documentos_scrapeados = os.listdir(directorio_documentos + r'\Scraped')

print("-----------------O----------------------")

#para cada documento scrapeado, chequear plagios contra el original
#-----------------O----------------------
for f in documentos_scrapeados:
    if f.endswith('.pdf'):
        doc = txr.convert_pdf_to_txt(os.path.join(directorio_documentos + r'\Scraped', f))
    elif f.endswith('.docx'):
        doc = txr.convert_docx_to_txt(os.path.join(directorio_documentos + r'\Scraped', f))
    else:
        doc = "No format"  

    if doc not in ["No format","error"]:
        try:      
            plagios = plagios + pg.chequear_plagio(plagio_algorithm,doc,doc_to_check,f,trained_model) #se puede especificar un umbral de similitud. Por defecto es 0.9
            print("Documento chequeado: ", basename(f))
        except:
            continue

#para cada documento, chequear plagios contra el original
#-----------------O----------------------
for f in documentos:
    if f.endswith('.pdf'):
        doc = txr.convert_pdf_to_txt(os.path.join(directorio_documentos, f))
    elif f.endswith('.docx'):
        doc = txr.convert_docx_to_txt(os.path.join(directorio_documentos, f))
    else:
        doc = "No format"  

    if doc not in ["No format","error"]:
        try:      
            plagios = plagios + pg.chequear_plagio(plagio_algorithm,doc,doc_to_check,f,trained_model) #se puede especificar un umbral de similitud. Por defecto es 0.9
            print("Documento chequeado: ", basename(f))
        except:
            continue

#-----------------O----------------------

print("-----------------O----------------------")

#guardar resultados
#-----------------O----------------------
df_plagios = pd.DataFrame([x.split(';') for x in plagios.split('\n')],columns=['Doc Plagiado','Oracion Plagiada','Oracion Chequeada','Prediccion'])
df_plagios = df_plagios[:-1]
ut.exportar_resultados(df_plagios,plagio_algorithm)
#-----------------O----------------------

print("Analisis terminado")
print("-----------------O----------------------")

print("Nombre del archivo procesado: ", basename(path_to_check))
print("Nombre y apellido del alumno: ", ut.find_owner(path_to_check))
print("Tema del documento: ", tema_documento)
print("Porcentaje de plagio total: ", str(ut.calcular_porcentaje_plagio(df_plagios,doc_to_check)),'%')
print("Algoritmo utilizado: ",ut.get_algoritmo_by_id(plagio_algorithm))

print("-----------------O----------------------")