# custom libraries
from lib import loading, requests, helpers

def main():
        
        # load history and train model
        history = loading.run('../../files')
        trained_model = requests.load(history)
        
        # get questions from users
        while True:
            question = input('>')
            if question.lower('exit')
                break
            
            # print the response 
            print(trained_model(question))
    
        return 

if __name__ == '__main__':
        main()

