from flask import Flask, request, jsonify, render_template
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Initialize Flask app
app = Flask(__name__)

# Download necessary NLTK data
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

# Route for the homepage
@app.route('/')
def home():
    return render_template('chat.html')  # Render a simple chat interface

# Route to handle chat messages
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.get_json().get('input')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    advice = give_career_advice(user_input)
    return jsonify({'advice': advice})

if __name__ == '__main__':
    app.run(debug=True)
