from nltk import word_tokenize
from nltk import tokenize
from nltk.corpus import stopwords
import utils as ut
from googletrans import Translator
translator = Translator()

def chequear_plagio_word2vec(doc1,doc2,file,trained_model,UMBRAL_SIMILARIDAD):
    sentences1 = tokenize.sent_tokenize(doc1)
    sentences2 = tokenize.sent_tokenize(doc2)
    
    plagios = ""
    
    for sentence1 in sentences1:
        for sentence2 in sentences2:
            
            similaridad = 0
            
            words1 = ut.is_in_vocabulary(sentence1,trained_model)
            words2 = ut.is_in_vocabulary(sentence2,trained_model)

            if(len(words1)>5 and len(words2)>5):
                similaridad = trained_model.n_similarity(words1,words2)

                if similaridad > UMBRAL_SIMILARIDAD and not ut.is_a_question_word(words1[0]) and not ut.is_a_question_word(words2[0]):
                    plagios = plagios + ut.parsear_plagio(file,sentence1,sentence2,similaridad)

    return plagios


def chequear_plagio_wordnet(doc1,doc2,file,trained_model,UMBRAL_SIMILARIDAD):

    sentences1 = tokenize.sent_tokenize(doc1)
    sentences2 = tokenize.sent_tokenize(doc2)
    plagios = ""

    for sentence1 in sentences1:
        words1 = [word for word in tokenize.word_tokenize(sentence1) if word != '.'  and word not in stopwords.words('spanish')]

        if len(words1)>3:

            for sentence2 in sentences2:
                cant_similitudes = 0

                words2 = [word for word in tokenize.word_tokenize(sentence2) if word != '.' and word not in stopwords.words('spanish')]

                if len(words2)>3:

                    for word1 in words1:
                        cant_similitudes = cant_similitudes + ut.check_synonyms_similarities(word1,words2) 

                    if cant_similitudes >= ut.calcular_porcentaje_palabras(0.3,words2):
                        
                        plagios = plagios + ut.parsear_plagio(file,sentence1,sentence2,cant_similitudes)

    return plagios 
 

def chequear_plagio(plagio_algorithm,doc1,doc2,file,trained_model,UMBRAL_SIMILARIDAD=0.9):

    doc1 = ut.preprocess_text(doc1)
    doc2 = ut.preprocess_text(doc2)

    if plagio_algorithm == 'A':
        return chequear_plagio_word2vec(doc1,doc2,file,trained_model,UMBRAL_SIMILARIDAD)
    else:
        return chequear_plagio_wordnet(doc1,doc2,file,trained_model,UMBRAL_SIMILARIDAD)