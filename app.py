try:
    import streamlit as st
except ModuleNotFoundError:
    print("Streamlit is not installed. Please run 'pip install streamlit' to install it.")
    exit(1)

# Set page configuration
st.set_page_config(page_title="Career Advisor Chatbot", layout="wide")

# Custom CSS for dark theme
st.markdown(
    """
    <style>
        body {
            background-color: #1e1e2f;
            color: #f5f5f5;
            font-family: 'Arial', sans-serif;
        }
        .header-title {
            font-size: 3rem;
            color: #ffcc00;
            text-align: center;
            margin-bottom: 10px;
        }
        .subheading {
            font-size: 1.5rem;
            color: #f5f5f5;
            text-align: center;
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 2rem;
            color: #ffcc00;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        .section-content {
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .cta-button {
            background-color: #ffcc00;
            color: #1e1e2f;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            text-align: center;
            display: block;
            margin: 20px auto;
        }
        .cta-button:hover {
            background-color: #ffd633;
        }
        .image-container {
            text-align: center;
            margin: 20px 0;
        }
        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown("<div class='header-title'>Welcome to the Career Advisor Chatbot</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subheading'>Your personalized career guidance assistant for South African students, Grades 10-12.</div>",
    unsafe_allow_html=True,
)

# Add Hero Image
st.markdown(
    """
    <div class='image-container'>
        <img src='https://unsplash.com/photos/IgUR1iX0mqM/download?force=true&w=1920' alt='Hero Image'>
    </div>
    """,
    unsafe_allow_html=True
)

# Problem Statement Section
st.markdown("<div class='section-title'>Problem Statement</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='section-content'>
        Many young people in South Africa face significant challenges when it comes to career guidance:
        <ul>
            <li>Limited access to career resources, especially in underprivileged communities.</li>
            <li>Lack of awareness about diverse career options.</li>
            <li>Mismatch between skills and career choices.</li>
            <li>Delayed career decisions, leading to last-minute, uninformed choices.</li>
            <li>Rapidly changing job market making it difficult to keep up with emerging careers.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# Add Image for Problem Statement
st.markdown(
    """
    <div class='image-container'>
        <img src='https://unsplash.com/photos/gMsnXqILjp4/download?force=true&w=1200' alt='Problem Statement Image'>
    </div>
    """,
    unsafe_allow_html=True
)

# Solutions Section
st.markdown("<div class='section-title'>How This Chatbot Helps</div>", unsafe_allow_html=True)
st.markdown(
    """
    <div class='section-content'>
        Our Career Advisor Chatbot provides:
        <ul>
            <li>24/7 access to career resources for all students, regardless of their background.</li>
            <li>Personalized career recommendations based on your skills, interests, and goals.</li>
            <li>Awareness of diverse career options, including emerging opportunities in technology and other industries.</li>
            <li>Guidance on necessary skills, qualifications, and pathways for specific careers.</li>
            <li>Real-time insights on in-demand jobs, salary trends, and future market predictions.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# Add Image for Solutions Section
st.markdown(
    """
    <div class='image-container'>
        <img src='https://unsplash.com/photos/ZzOa5G8hSPI/download?force=true&w=1200' alt='Solutions Image'>
    </div>
    """,
    unsafe_allow_html=True
)

# Call to Action Button
st.markdown("<button class='cta-button'>Get Started</button>", unsafe_allow_html=True)
