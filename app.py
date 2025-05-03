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
    """Load user credentials from file with improved error handling"""
    users = {}
    
    # Check if file exists
    if not os.path.exists(USER_DB):
        # Create the file if it doesn't exist
        with open(USER_DB, "w") as f:
            pass
        return users
    
    # Read user credentials
    try:
        with open(USER_DB, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if not line or ":" not in line:
                    continue
                    
                try:
                    parts = line.split(":", 1)  # Split at first colon only
                    if len(parts) == 2:
                        username = parts[0]
                        password_hash = parts[1]
                        if username and password_hash:
                            users[username] = password_hash
                except Exception as e:
                    st.error(f"Error processing credential line: {e}")
                    continue
    except Exception as e:
        st.error(f"Error loading user credentials: {e}")
    
    return users

def save_user(username, password):
    """Save user credentials to file with error handling"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(USER_DB) if os.path.dirname(USER_DB) else ".", exist_ok=True)
        
        with open(USER_DB, "a") as f:
            f.write(f"{username}:{hash_password(password)}\n")
        return True
    except Exception as e:
        st.error(f"Error saving user: {e}")
        return False

def authenticate(username, password):
    """Authenticate user with improved error handling"""
    try:
        users = load_users()
        return username in users and users[username] == hash_password(password)
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

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
                if save_user(username, password):
                    st.success("Registered successfully! Please log in.")
                else:
                    st.error("Registration failed. Please try again.")

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
        option = st.sidebar.radio("Choose an option", ("Login", "Register", "Try"))
        
        # Use conditional rendering instead of function calls
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