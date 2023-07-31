# custom libraries
from lib import loading, request, helper
import os
import sys

def main():
        
        #embedding_model = 'text-embedding-ada-002'
        engine = 'text-davinci-002'
        api_key = os.getenv("OPENAI_API_KEY")  
    
        if len(sys.argv) != 2:
            print("Usage: python script.py 'your question'")
            sys.exit(1)

        question = sys.argv[1]
        response = requests.send(question, engine, api_key)
        
        return response

if __name__ == '__main__':
        print(main())


