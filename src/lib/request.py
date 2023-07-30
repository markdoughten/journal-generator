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
    
