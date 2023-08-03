import os
from bs4 import BeautifulSoup
import pandas as pd
import csv
import sys
import string
import re
import tiktoken
from openai.embeddings_utils import get_embedding
import numpy as np
import ast

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
    
    # loop through all files and subdirectories in the directory
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            extension = file_path.split('.')[-1].lower()
            texts = load_data(file_path, extension)
            if texts:
                texts = clean_data(texts)
                all_texts.append(texts)
            else:
                unsupported.add(extension)

    return all_texts

def clean_item(item):
   
    unwanted_strings = ['False', 'Normal', 'X-GOOGLE-CALENDAR-CONTENT-DISPLAY:CHIP\n', \
                        'X-GOOGLE-CALENDAR-CONTENT-ICON:https://calendar.google.com/googlecalendar/i', \
                        'END:VEVENT', 'BEGIN:VEVENT', 'CLASS:PUBLIC', 'TRANSP:OPAQUE',  'SEQUENCE:0'\
                        ' mages/cake.gif', 'X-GOOGLE-CALENDAR-CONTENT-DISPLAY:CHIP', '+0000']

 
    cleaned_item = ''.join(ch for ch in item if ord(ch) < 128)  # remove non-ASCII
    cleaned_item = re.sub(r'<a.*?>.*?</a>', '', cleaned_item)  # remove <a> tags
    cleaned_item = cleaned_item.replace('\n', '')
    
    for unwanted in unwanted_strings:
        cleaned_item = cleaned_item.replace(unwanted, '')  # remove unwanted strings
    
    return cleaned_item

def clean_data(data):
    
    new_data = []
    
    for item in data:
        if isinstance(item, list):
            new_data.append(clean_data(item))
        elif isinstance(item, str) and item != '':  # remove empty strings
            cleaned_item = clean_item(item)
            if cleaned_item != '':  # remove strings that become empty after cleaning
                new_data.append(cleaned_item)
    
    return new_data

def make_embeddings(df, max_tokens, encoding, model):

    encoding = tiktoken.get_encoding(encoding)
    df["n_tokens"] = df['text'].apply(lambda x: len(encoding.encode(x)))
    
    # filter out large text
    df = df[df.n_tokens <= max_tokens].copy()
    df["embedding"] = df['text'].apply(lambda x: get_embedding(x, engine=model))
    df = df.dropna(how='all')
    
    return df

def convert_to_df(history):
    
    df = pd.DataFrame(history)
    df = df.fillna('')
   
    # combine all columns into one
    df['text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
    df = df[['text']]
    
    return df 

def run(model, encoding, max_tokens, path, embedding=True):    
    
    # directory
    history = directory(path)
    df = convert_to_df(history)
    
    if embedding:
        df = make_embeddings(df, max_tokens, encoding, model)

    return df

def get_embedding_matrix(path):
    
    df = pd.read_csv(path)
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    
    return df

if __name__ == "__main__":
    
    model = "text-embedding-ada-002"
    encoding = "cl100k_base"
    max_tokens = 8191
    path =  '../../files'
    
    df = run(model, encoding, max_tokens, path, True)
    df.to_csv('../../search/embedding_history.csv', index=False)    
