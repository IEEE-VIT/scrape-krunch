import requests
from bs4 import BeautifulSoup as bs
import time
import os
from ollama import chat
from ollama import ChatResponse



def get_stuff():
    html=requests.get("https://idrw.org/")
    soup=bs(html.text,"xml")
    headings = soup.find_all("h2")
    # para=soup.find("div", class_="art-postcontent clearfix")
    para=soup.find_all("article")
    for item in headings:
        print(item.text)
        print(para[2].text)
        print(item.find_next("p").text if item.find_next("p") else "no para ")
        
        
        response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': f"Summarize this : {para[2].text}",
        },
    ])
        print("\n\n\n\n\n\n\n\n")
        print(response['message']['content'])
        print(response.message.content)

    # print("items\n")
    # for item in headings:
    #     print(item.text)
    # for h in para:
    #     print(h.text)



get_stuff()
    # or access fields directly from the response object
