# imports
import ast  
import openai
import pandas as pd
import tiktoken
from scipy import spatial
import os
import requests
import json

def send(user_input, engine, api_key):
   
    openai.api_key = api_key
    
    # Use OpenAI's API to generate a response
    response = openai.Completion.create(
        engine=engine,
        prompt=user_input,
        temperature=0.5,
        max_tokens=100
    )

    return response.choices[0].text.strip()

def num_tokens(text, model):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# search function
def strings_ranked_by_relatedness(query, df, embedding, relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y), top_n=100):
    
    query_embedding_response = openai.Embedding.create(model=embedding, input=query)
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [(row["text"], relatedness_fn(query_embedding, row["embedding"]))for i, row in df.iterrows()]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    
    return strings[:top_n], relatednesses[:top_n]

def query_message(query, df, model, token_budget, embedding):
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    
    strings, relatednesses = strings_ranked_by_relatedness(query, df, embedding)
    introduction = 'Write a journal entry about a date based on the historical information available'
    question = f"\n\nDate: {query}"
    message = introduction
    
    for string in strings:
        next_event = f'\n\nRelevant event:\n"""\n{string}\n"""'
        if (num_tokens(message + next_event + question, model=model) > token_budget):
            break
        else:
            message += next_event
    
    return message + question

def ask(query, df, model, token_budget, embedding, print_message=False):
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    
    message = query_message(query, df, model, token_budget, embedding)
    
    if print_message:
        print(message)
    
    messages = [
        {"role": "system", "content": "You answer questions like journal entries."},
        {"role": "user", "content": message}]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    
    return response["choices"][0]["message"]["content"]

    
