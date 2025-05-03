import streamlit as st
import hashlib
import os
from chatbot import chatbot_interface  # Import chatbot interface from chatbot.py

# Set page configuration at the top level
st.set_page_config(page_title="Career Advisor ChatBot", layout="wide")

# File to store user credentials
USER_DB = "user_credentials.txt"


# Utility Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    
    users = {}
    with open(USER_DB, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line and ":" in line:
                parts = line.split(":", 1)  # Split at first colon only
                if len(parts) == 2:
                    username, password_hash = parts
                    users[username] = password_hash
    return users

def save_user(username, password):
    with open(USER_DB, "a") as f:
        f.write(f"{username}:{hash_password(password)}\n")

def authenticate(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

# Pages
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def register_page():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Register"):
        # Validation checks
        if not username.strip():
            st.error("Username cannot be empty.")
        elif not password.strip():
            st.error("Password cannot be empty.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long.")
        else:
            # Proceed with user registration
            users = load_users()
            if username in users:
                st.error("Username already exists.")
            else:
                save_user(username, password)
                st.success("Registered successfully! Please log in.")

def try_page():
    st.title("Try") 
    st.session_state.logged_in = True
    st.session_state.username = "Guest"
    st.success("You are now trying the chatbot as a guest!")   
    st.rerun() 
    

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

def landing_page():
    st.title("Welcome to the Career Advisor ChatBot")
    st.write("Please use the navigation menu to access different features of the chatbot.")

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    # Routing
    if st.session_state.logged_in:
        # Chatbot page
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            logout()
        st.sidebar.markdown("---")

        # Run the chatbot interface
        chatbot_interface()
    else:
        # Show login/registration options
        option = st.sidebar.radio("Choose an option", ("Login", "Register","Try"))
        if option == "Login":
            login_page()
        elif option == "Register":
            register_page()
        elif option == "Try":
            try_page() 
        else:
            landing_page()

# Run the app
if __name__ == "__main__":
    main()