# custom libraries
from lib import loading, request, helper
import os
import sys
import pandas as pd

def main():
        
        model = "gpt-4"
        embedding = "text-embedding-ada-002"
        df = loading.get_embedding('../search/embedding_history.csv')
        token_budget= 5000       
 
        if len(sys.argv) != 2:
            print("Usage: python script.py 'your question'")
            sys.exit(1)

        query = sys.argv[1]
        response = request.ask(query, df, model, token_budget, embedding, True)
        
        return response

if __name__ == '__main__':
        print(main())


