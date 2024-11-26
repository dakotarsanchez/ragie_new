import streamlit as st
import requests
from typing import List, Dict, Optional

class RAGAgent:
    def __init__(self):
        """Initialize the RAG Agent with API key from Streamlit secrets."""
        try:
            self.api_key = st.secrets["RAGIE_API_KEY"]
            if not self.api_key:
                raise ValueError("RAGIE_API_KEY not found in secrets")
        except Exception as e:
            st.error(f"Error initializing API key: {str(e)}")
            self.api_key = None

    def get_recent_meeting_summaries(self) -> List[Dict]:
        """Fetch the 3 most recent meeting summaries from Ragie API."""
        if not self.api_key:
            print("No API key found")
            return []
        
        url = "https://api.ragie.ai/documents?page_size=3&filter=%7B%22folder%22%3A%20%7B%22%24eq%22%3A%20%22test_meetings%22%7D%7D"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            documents = result.get('documents', [])
            
            # Fetch summary for each document
            for doc in documents:
                doc['summary'] = self.get_meeting_summary(doc['id'])
            
            return documents
        except Exception as e:
            error_msg = f"Error fetching meeting summaries: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return []

    def get_meeting_summary(self, document_id: str) -> Optional[str]:
        """Fetch the summary for a specific meeting by document ID."""
        if not self.api_key:
            print("No API key found")
            return None
            
        url = f"https://api.ragie.ai/documents/{document_id}/summary"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            # Return the raw response text instead of parsing JSON
            return response.text
        except Exception as e:
            error_msg = f"Error fetching meeting summary for document {document_id}: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return None 
