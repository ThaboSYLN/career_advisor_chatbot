import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import spacy

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_context(user_input):
    """
    Extract contextual information (grade, career interests, activities) 
    from the user's input using SpaCy NLP.
    """
    doc = nlp(user_input)
    context = {}

    # Extract grade level
    for ent in doc.ents:
        if ent.label_ == "ORDINAL" and "grade" in ent.text.lower():
            context["grade_level"] = ent.text

    # Extract career interests based on keywords
    career_keywords = ["engineer", "doctor", "teacher", "scientist", "nurse"]
    for token in doc:
        if token.text.lower() in career_keywords:
            context["career_interest"] = token.text

    # Extract activities like internship, mentorship, etc.
    activity_keywords = ["internship", "mentorship", "volunteering"]
    for token in doc:
        if token.text.lower() in activity_keywords:
            context.setdefault("activities", []).append(token.text)

    return context

def get_trending_careers():
    """
    Fetch a list of trending careers in South Africa using OpenAI.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a career market analyst. Provide a list of 10 currently trending careers "
                        "in South Africa with their growth potential. Format as dictionaries with 'title' and 'growth_rate' keys."
                    ),
                }
            ],
            temperature=0.7,
        )
        # Parse the response into a Python object
        careers = eval(response.choices[0].message.content)
        return {"careers": careers}
    except Exception as e:
        st.error("Error fetching trending careers.")
        return {"careers": []}

def generate_response(user_input):
    """
    Generate a response from OpenAI based on the user's input and session context.
    """
    try:
        # Incorporate user context into the prompt
        context = st.session_state.get("user_context", {})
        system_message = (
            f"You are a career advisor specializing in South African education and careers. "
            f"The user's context is: {context}. Respond with detailed and practical advice."
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error("Error generating response.")
        return "Sorry, I'm having trouble responding right now."

def chatbot_interface():
    """
    Main Streamlit interface for the Career Advisor Chatbot.
    """
    st.title("Career Advisor Chatbot")
    st.write("Welcome! I can help you explore careers, study options, and universities in South Africa.")

    # Initialize user context and messages in session state
    if "user_context" not in st.session_state:
        st.session_state.user_context = {}
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display trending careers
    st.subheader("Trending Careers in South Africa")
    careers = get_trending_careers()
    if careers["careers"]:
        for career in careers["careers"]:
            st.write(f"- {career['title']} (Growth Potential: {career['growth_rate']})")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input field
    if prompt := st.chat_input("What would you like to know about careers?"):
        # Add user input to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Extract context from user input and update session state
        new_context = extract_context(prompt)
        st.session_state.user_context.update(new_context)

        # Generate and display assistant's response
        with st.chat_message("assistant"):
            response = generate_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Display user context for transparency
    st.subheader("Conversation Context")
    st.json(st.session_state.get("user_context", {}))

if __name__ == "__main__":
    chatbot_interface()
