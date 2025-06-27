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
    """Register user and send email verification"""
    try:
        # Create user in Firebase Authentication
        user = auth.create_user_with_email_and_password(email, password)
        
        # Send email verification
        auth.send_email_verification(user['idToken'])
        
        # Store additional user data in Realtime Database with verification status
        user_data = {
            "username": username,
            "email": email,
            "email_verified": False,
            "created_at": {".sv": "timestamp"}
        }
        db.child("users").child(user['localId']).set(user_data)
        
        return True, "Registration successful! Please check your email for verification link before logging in."
    except Exception as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            return False, "Email already exists. Please use a different email."
        elif "WEAK_PASSWORD" in error_message:
            return False, "Password is too weak. Please use at least 6 characters."
        elif "INVALID_EMAIL" in error_message:
            return False, "Invalid email format. Please enter a valid email address."
        return False, f"Registration failed: {error_message}"

def login_user(email, password):
    """Login user and check email verification status"""
    try:
        # Authenticate user with Firebase
        user = auth.sign_in_with_email_and_password(email, password)
        
        # Get user info to check email verification
        user_info = auth.get_account_info(user['idToken'])
        email_verified = user_info['users'][0].get('emailVerified', False)
        
        if not email_verified:
            return False, None, "Please verify your email before logging in. Check your inbox for the verification link."
        
        # Update verification status in database if verified
        if email_verified:
            db.child("users").child(user['localId']).child("email_verified").set(True)
        
        # Get user details from database
        user_data = db.child("users").child(user['localId']).get().val()
        
        # Return username or email if username not available
        username = user_data.get('username') if user_data else email.split('@')[0]
        
        return True, user, username
    except Exception as e:
        error_message = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_message or "INVALID_PASSWORD" in error_message:
            return False, None, "Invalid email or password."
        elif "EMAIL_NOT_FOUND" in error_message:
            return False, None, "No account found with this email address."
        elif "USER_DISABLED" in error_message:
            return False, None, "This account has been disabled."
        return False, None, f"Login failed: {error_message}"

def resend_verification_email(email, password):
    """Resend verification email"""
    try:
        # Sign in to get the token
        user = auth.sign_in_with_email_and_password(email, password)
        
        # Check if already verified
        user_info = auth.get_account_info(user['idToken'])
        if user_info['users'][0].get('emailVerified', False):
            return False, "Email is already verified. You can now log in."
        
        # Send verification email
        auth.send_email_verification(user['idToken'])
        return True, "Verification email sent! Please check your inbox."
    except Exception as e:
        error_message = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            return False, "Invalid email or password."
        return False, f"Failed to resend verification email: {error_message}"

# Pages
def login_page():
    st.title("🔐 Login")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("login_form"):
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_login, col_resend = st.columns(2)
            with col_login:
                submit_login = st.form_submit_button("Login", use_container_width=True)
            with col_resend:
                submit_resend = st.form_submit_button("Resend Verification", use_container_width=True)
            
            if submit_login:
                if not email or not password:
                    st.error("⚠️ Please enter both email and password.")
                    return
                    
                with st.spinner("Logging in..."):
                    success, user, message = login_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = message  # Username or email
                        st.session_state.user_id = user['localId']
                        st.success("✅ Logged in successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            if submit_resend:
                if not email or not password:
                    st.error("⚠️ Please enter both email and password to resend verification.")
                    return
                
                with st.spinner("Sending verification email..."):
                    success, message = resend_verification_email(email, password)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
    
    with col2:
        st.info("💡 **New User?**\n\nRegister using the sidebar option to create your account.")
        st.info("📧 **Email Verification Required**\n\nYou must verify your email before logging in. Check your inbox after registration.")

def register_page():
    st.title("📝 Create Account")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("register_form"):
            st.markdown("### Personal Information")
            username = st.text_input("👤 Username", placeholder="Choose a username")
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            
            st.markdown("### Password")
            password = st.text_input("🔒 Password", type="password", placeholder="Minimum 6 characters")
            password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password")
            
            # Terms and conditions
            terms_accepted = st.checkbox("✅ I agree to the Terms of Service and Privacy Policy")
            
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                # Validation checks
                if not username.strip() or not email.strip() or not password.strip():
                    st.error("⚠️ All fields are required.")
                elif not "@" in email or not "." in email.split("@")[1]:
                    st.error("⚠️ Please enter a valid email address.")
                elif len(password) < 6:
                    st.error("⚠️ Password must be at least 6 characters long.")
                elif password != password_confirm:
                    st.error("⚠️ Passwords do not match.")
                elif not terms_accepted:
                    st.error("⚠️ Please accept the Terms of Service and Privacy Policy.")
                else:
                    # Register the user
                    with st.spinner("Creating your account..."):
                        success, message = register_user(email, password, username)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("📧 **Next Steps:**\n\n1. Check your email inbox\n2. Click the verification link\n3. Return here to log in")
                        else:
                            st.error(f"❌ {message}")
    
    with col2:
        st.info("🔐 **Security Features**\n\n• Email verification required\n• Secure password encryption\n• Firebase authentication")
        st.info("📧 **Email Verification**\n\nAfter registration, you'll receive a verification email. Click the link to activate your account.")

def try_page():
    st.title("🚀 Try as Guest") 
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; border: 2px dashed #4CAF50; border-radius: 10px;'>
            <h3>🎯 Guest Access</h3>
            <p>Experience our Career Advisor ChatBot without creating an account!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.username = "Guest"
            st.session_state.user_id = "guest"
            st.success("🎉 You are now trying the chatbot as a guest!")   
            st.rerun()
        
        st.info("💡 **Guest Limitations:**\n\n• Chat history not saved\n• Limited features\n• No personalization")

def logout():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    # Clear chat history
    if "conversation_history" in st.session_state:
        del st.session_state.conversation_history
    if "messages" in st.session_state:
        del st.session_state.messages
    st.rerun()

def landing_page():
    st.title("🎯 Welcome to the Career Advisor ChatBot")
    
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
        if st.button("Continue", use_container_width=True):
            if option == "Login":
                st.session_state.sidebar_option = "Login"
            elif option == "Register":
                st.session_state.sidebar_option = "Register"
            elif option == "Try as Guest":
                st.session_state.sidebar_option = "Try"
            st.rerun()
# Main Application Logic
# Replace the existing CSS section in your main() function with this improved version:

def main():
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
    
    if "sidebar_option" not in st.session_state:
        st.session_state.sidebar_option = "Login"
    
    # Enhanced CSS for better styling and visibility
    st.markdown("""
    <style>
    /* Form container styling */
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 5px;
        border: none;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #45a049, #4CAF50);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Input field styling - this fixes your visibility issue */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #333333 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2) !important;
    }
    
    /* Password input styling */
    .stTextInput > div > div > input[type="password"] {
        background-color: white !important;
        color: #333333 !important;
        border: 1px solid #cccccc !important;
        border-radius: 5px !important;
    }
    
    /* Label styling */
    .stTextInput > label {
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #333333 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f0f2f6 !important;
    }
    
    /* Sidebar text visibility */
    .sidebar .sidebar-content {
        color: #333333 !important;
    }
    
    /* Sidebar title */
    .sidebar .markdown-text-container h1,
    .sidebar .markdown-text-container h2,
    .sidebar .markdown-text-container h3 {
        color: #333333 !important;
    }
    
    /* Sidebar radio button text */
    .sidebar .stRadio label {
        color: #333333 !important;
    }
    
    /* Sidebar radio button options */
    .sidebar .stRadio > div label {
        color: #333333 !important;
    }
    
    /* All sidebar text elements */
    .sidebar * {
        color: #333333 !important;
    }
    
    /* Sidebar markdown text */
    .sidebar .markdown-text-container {
        color: #333333 !important;
    }
    
    /* Override any white text in sidebar */
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: #333333 !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #e8f5e8 !important;
        border-left: 4px solid #4caf50 !important;
        color: #2e7d32 !important;
    }
    
    .stSuccess > div {
        color: #2e7d32 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #fff8e1 !important;
        border-left: 4px solid #ff9800 !important;
        color: #ef6c00 !important;
    }
    
    .stWarning > div {
        color: #ef6c00 !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    /* Error messages */
    .stError {
        background-color: #ffebee !important;
        border-left: 4px solid #f44336 !important;
        color: #d32f2f !important;
    }
    
    .stError > div {
        color: #d32f2f !important;
    }
    
    /* Alert messages */
    .stAlert {
        color: #333333 !important;
    }
    
    .stAlert > div {
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Rest of your main() function continues here...
    # Routing
    if st.session_state.logged_in:
        # Chatbot page
        st.sidebar.title(f"👋 Welcome, {st.session_state.username}!")
        if st.sidebar.button("🚪 Logout"):
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