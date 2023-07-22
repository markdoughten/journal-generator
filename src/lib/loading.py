import os
from bs4 import BeautifulSoup
import pandas as pd
import csv
import sys

def load_data(file_path, extension):
    if extension in ['htm', 'html']:
        with open(file_path, 'r', encoding='utf8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            text = soup.get_text()
            return text.split('\n')
    elif extension == 'txt':
        with open(file_path, 'r', encoding='unicode_escape') as file:
            return file.read()
    elif extension == 'csv':
        with open(file_path, 'r', encoding='unicode_escape') as file:
            return list(csv.reader(file, delimiter=','))
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
            extension = file_path.split('.')[-1]
            texts = load_data(file_path, extension)
            if texts:
                all_texts.extend(texts)
            else:
                unsupported.add(extension)

    # all_texts contains the texts from all files
    print(f'Unsupported file types: {unsupported}')

    return all_texts

if __name__ == "__main__":
    
    # directory
    path = '../../files'
    output = directory(path)

    for item in output:
        if isinstance(item, list):  # Handle the case of CSV reader output
            for row in item:
                cleaned_row = [cell.replace(',', '') for cell in row]
                if cleaned_row:
                    output_str = ''.join(cleaned_row) + '\n'
                    sys.stdout.buffer.write(output_str.encode('utf-8'))
        else:
            sys.stdout.buffer.write(item.encode('utf-8'))
