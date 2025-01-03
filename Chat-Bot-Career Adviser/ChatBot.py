import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



nltk.download('averaged_perceptron_tagger')
# Download NLTK data
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')


# Career advice function
def give_career_advice(user_input):
    tokens = word_tokenize(user_input.lower())
    tokens = [t for t in tokens if t not in stopwords.words('english')]
    
    if 'software' in tokens or 'development' in tokens or 'coding' in tokens:
        return "Have you considered learning programming languages like Python or Java?"
    elif 'marketing' in tokens or 'advertising' in tokens or 'business' in tokens:
        return "Building a strong portfolio and networking can be beneficial."
    elif 'art' in tokens or 'design' in tokens or 'creative' in tokens:
        return "Developing a portfolio and exploring different mediums can be helpful."
    else:
        return "Can you tell me more about your career interests?"

def main():
    print("Welcome to the Career Advice Chatbot!")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        advice = give_career_advice(user_input)
        print("Chatbot: ", advice)

if __name__ == "__main__":
    main()
