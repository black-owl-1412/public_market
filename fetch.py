import requests
from constants import HEADERS  


def fetch(url): 
    response = requests.get(url = url , headers= HEADERS , timeout=  30) 
    response.raise_for_status()   
    return response.text 






