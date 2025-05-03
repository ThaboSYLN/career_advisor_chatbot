import streamlit as st
import hashlib
import os
import pyrebase
from dotenv import load_dotenv
from chatbot import chatbot_interface  # Import chatbot interface from chatbot.py

# Set page configuration at the top level
st.set_page_config(page_title="Career Advisor ChatBot", layout="wide")
# Load environment variables first
load_dotenv()
# Firebase Configuration
# Firebase Configuration
firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# Utility Functions
def register_user(email, password, username):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user_with_email_and_password(email, password)
        
        # Store additional user data in Realtime Database
        user_data = {
            "username": username,
            "email": email,
            "created_at": {".sv": "timestamp"}  # Server timestamp
        }
        db.child("users").child(user['localId']).set(user_data)
        
        return True, "Registration successful!"
    except Exception as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            return False, "Email already exists. Please use a different email."
        return False, f"Registration failed: {error_message}"

def login_user(email, password):
    try:
        # Authenticate user with Firebase
        user = auth.sign_in_with_email_and_password(email, password)
        
        # Get user details from database
        user_data = db.child("users").child(user['localId']).get().val()
        
        # Return username or email if username not available
        username = user_data.get('username') if user_data else email.split('@')[0]
        
        return True, user, username
    except Exception as e:
        error_message = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            return False, None, "Invalid email or password."
        return False, None, f"Login failed: {error_message}"

# Pages
def login_page():
    st.title("Login")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if not email or not password:
                st.error("Please enter both email and password.")
                return
                
            success, user, message = login_user(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = message  # Username or email
                st.session_state.user_id = user['localId']
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        st.info("Don't have an account? Register using the sidebar option.")

def register_page():
    st.title("Register")
    
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    password_confirm = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        # Validation checks
        if not username.strip() or not email.strip() or not password.strip():
            st.error("All fields are required.")
        elif not "@" in email:
            st.error("Please enter a valid email address.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long.")
        elif password != password_confirm:
            st.error("Passwords do not match.")
        else:
            # Register the user
            success, message = register_user(email, password, username)
            if success:
                st.success(message + " Please log in.")
            else:
                st.error(message)

def try_page():
    st.title("Try as Guest") 
    st.session_state.logged_in = True
    st.session_state.username = "Guest"
    st.session_state.user_id = "guest"
    st.success("You are now trying the chatbot as a guest!")   
    st.rerun() 

def logout():
    # Firebase doesn't need explicit logout on client side
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.rerun()

def landing_page():
    st.title("Welcome to the Career Advisor ChatBot")
    
    st.markdown("""
    <div style='text-align: center; margin: 50px 0'>
        <h2 style='color: #4CAF50;'>Your AI Career Guide</h2>
        <p style='font-size: 18px;'>Get personalized career advice, industry insights, and job recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Career Exploration")
        st.write("Discover careers that match your skills, interests, and educational background.")
    
    with col2:
        st.markdown("### 📊 Industry Insights")
        st.write("Get up-to-date information on growing industries and job market trends.")
    
    with col3:
        st.markdown("### 🚀 Personalized Advice")
        st.write("Receive customized recommendations for your unique career journey.")
    
    # Get started section
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Get Started Now</h3>", unsafe_allow_html=True)
    
    start_col1, start_col2, start_col3 = st.columns([1, 2, 1])
    
    with start_col2:
        option = st.radio("Choose an option:", ("Login", "Register", "Try as Guest"))
        if st.button("Continue"):
            if option == "Login":
                st.session_state.sidebar_option = "Login"
            elif option == "Register":
                st.session_state.sidebar_option = "Register"
            elif option == "Try as Guest":
                st.session_state.sidebar_option = "Try"
            st.rerun()

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
    
    if "sidebar_option" not in st.session_state:
        st.session_state.sidebar_option = "Login"
    
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
        option = st.sidebar.radio("Choose an option", ("Login", "Register", "Try"), 
                                  index=["Login", "Register", "Try"].index(st.session_state.sidebar_option))
        
        # Update the session state
        st.session_state.sidebar_option = option
        
        # Display corresponding page
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