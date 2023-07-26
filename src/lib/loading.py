import os
from bs4 import BeautifulSoup
import pandas as pd
import csv
import sys
import string
import re

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

if __name__ == "__main__":
    
    # directory
    path = '../../files'
    messages = directory(path)
    print(messages)
