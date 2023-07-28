import os
import openai


def template():
    return

def set_key():
    openai.api_key = os.getenv("OPENAI_API_KEY")  
    return   

def get_models():
    models = openai.Model.list()
    return models

def request(content)
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{content}])
    return chat_completion.choices[0].messages.content
    
