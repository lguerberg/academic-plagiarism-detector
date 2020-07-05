import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import urlparse
from pathlib import Path
from pathlib import Path
import requests
from os.path import basename
import os

def google_search_and_save(query,path_to_save,max_pages):
    g_clean = [ ] #this is the list we store the search results
    url = 'https://www.google.com/search?num='+ str(max_pages) +'&client=ubuntu&channel=fs&q={}&ie=utf-8&oe=utf-8'.format(query)#this is the actual query we are going to scrape
    try:
        html = requests.get(url)
        if html.status_code==200:
            soup = BeautifulSoup(html.text, 'lxml')
            a = soup.find_all('a') # a is a list
            for i in a:
                k = i.get('href')
                try:
                    m = re.search(r"(?P<url>https?://[^\s]+)", k)
                    n = m.group(0)
                    rul = n.split('&')[0]
                    domain = urlparse(rul)
                    if(re.search('google.com', domain.netloc)):
                        continue
                    else:
                        g_clean.append(rul)
                except:
                    continue
    except Exception as ex:
        print(str(ex))
    finally:
        cant = 0
        for f in g_clean:
            if guardar_archivo(f,path_to_save):
                cant = cant + 1  
        return cant


def guardar_archivo(url,path):
    extension = url[-4:]

    try:
        if extension in extensiones_compatibles():

            if '.pdf' in basename(url) or '.docx' in basename(url):
                filename =  Path(path + "\\" + basename(url))
            else:
                filename = Path(path + "\\" + basename(url) + extension)

            response = requests.get(url)


            filename.write_bytes(response.content)
            if os.path.getsize(filename)<50000:
                os.remove(filename)
                return False
                
            print("Descargado archivo: ", basename(url))
            return True

        return False
    except Exception as e:
        print(e)
        print("Error al conectarse con la url: ",url)
        return False

def extensiones_compatibles():
    return ['.pdf','.docx']