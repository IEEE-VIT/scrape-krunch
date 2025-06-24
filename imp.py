import requests
from bs4 import BeautifulSoup as bs
import time



def get_stuff():
    html=requests.get("https://idrw.org/")
    soup=bs(html.content,"xml")
    items=soup.find_all("p")
    print("items\n")
    for item in items:
        print(item.text)
    articles = []

get_stuff()
