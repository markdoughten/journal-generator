import os
from bs4 import BeautifulSoup
import pandas as pd
import csv
import sys
import string
import re
import openai
import tiktoken

def load_data(file_path, extension):
    if extension in ['htm', 'html']:
        with open(file_path, 'r', encoding='utf8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            text = soup.get_text()
            return text.split('\n')
    elif extension in ['txt', 'ics']:
        with open(file_path, 'r', encoding='unicode_escape') as file:
            return file.readlines()
    elif extension == 'csv':
        with open(file_path, 'r', encoding='unicode_escape') as file:
            return list(csv.reader(file))
    else:
        return []

def directory(directory_path):
    
    # initialize a list to hold all the texts
    all_texts = []
    unsupported = set([])
    unwanted_strings = ['False', 'Normal', 'X-GOOGLE-CALENDAR-CONTENT-DISPLAY:CHIP\n', \
                        'X-GOOGLE-CALENDAR-CONTENT-ICON:https://calendar.google.com/googlecalendar/i', \
                        ' mages/cake.gif\n', 'CLASS:PUBLIC\n', \
                        ' mages/cake.gif', 'X-GOOGLE-CALENDAR-CONTENT-DISPLAY:CHIP']

    # loop through all files and subdirectories in the directory
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            extension = file_path.split('.')[-1].lower()
            texts = load_data(file_path, extension)
            if texts:
                texts = clean_data(texts, unwanted_strings)
                all_texts.append(texts)
            else:
                unsupported.add(extension)

    return all_texts

def clean_item(item, unwanted_strings):
    
    cleaned_item = ''.join(ch for ch in item if ord(ch) < 128)  # remove non-ASCII
    cleaned_item = re.sub(r'<a.*?>.*?</a>', '', cleaned_item)  # remove <a> tags
    cleaned_item = cleaned_item.replace('\n', '')
    
    for unwanted in unwanted_strings:
        cleaned_item = cleaned_item.replace(unwanted, '')  # remove unwanted strings
    
    return cleaned_item

def clean_data(data, unwanted_strings):
    
    new_data = []
    
    for item in data:
        if isinstance(item, list):
            new_data.append(clean_data(item, unwanted_strings))
        elif isinstance(item, str) and item != '':  # remove empty strings
            cleaned_item = clean_item(item, unwanted_strings)
            if cleaned_item != '':  # remove strings that become empty after cleaning
                new_data.append(cleaned_item)
    
    return new_data

def num_tokens(text, model):
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def make_embeddings(model, batch_size, history, api_key):

    embeddings = []
    gpt_model = "gpt-3.5-turbo"     

    for batch_start in range(0, len(history), batch_size):
        batch_end = batch_start + batch_size
        batch = history[batch_start:batch_end]
        print(num_tokens(batch[0], gpt_model))
        print(f"Batch {batch_start} to {batch_end-1}")
        response = openai.Embedding.create(model=model, api_key=api_key, input=batch)
        for i, be in enumerate(response["data"]):
            assert i == be["index"]  # double check embeddings are in same order as input
        batch_embeddings = [e["embedding"] for e in response["data"]]
        embeddings.extend(batch_embeddings)

    df = pd.DataFrame({"text": history, "embedding": embeddings})

    return df

def run(model, batch_size, path, api_key):    
    
    # directory
    history = directory(path)
    df = make_embeddings(model, batch_size, history, api_key)

    return df

if __name__ == "__main__":
    
    api_key = os.environ.get('OPENAI_API_KEY') 
    model = "text-embedding-ada-002"
    batch_size = 1000  
    df = run(model, batch_size, '../../files', api_key)
    df.to_csv('../../model')    
