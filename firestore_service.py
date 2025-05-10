import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from typing import List, Dict
import streamlit as st
import time
class FirestoreManager:
    def __init__(self):
        if not firebase_admin._apps:
            self.initialize_firestore()
        self.db = firestore.client()  # Add this line

    def initialize_firestore(self):
        """Initialize Firestore connection"""
        try:
            cred = credentials.Certificate("service-account.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Firebase initialization failed: {str(e)}")
            raise

    def save_chat_message(self, user_id: str, message: dict):
        """Save message to user's chat collection"""
        try:
            self.db.collection('users').document(user_id).collection('chats').add({
                'role': message['role'],
                'content': message['content'],
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            st.error(f"Save error: {str(e)}")

    def get_chat_history(self, user_id: str) -> list:
        """Get user's chat history sorted by timestamp"""
        try:
            docs = self.db.collection('users')\
                .document(user_id)\
                .collection('chats')\
                .order_by('timestamp')\
                .stream()
            
            return [{
                'role': doc.to_dict()['role'],
                'content': doc.to_dict()['content']
            } for doc in docs]
        except Exception as e:
            st.error(f"Load error: {str(e)}")
            return []