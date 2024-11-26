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

        url = "https://api.ragie.ai/documents"
        params = {
            "page_size": 3,
            "filter": {"folder": {"$eq": "test_meetings"}}
        }
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        print(f"Making request to URL: {url}")
        print(f"With params: {params}")
        print(f"Headers (excluding auth token): {{'accept': {headers['accept']}}}")

        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            return result.get('documents', [])
        except Exception as e:
            error_msg = f"Error fetching meeting summaries: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return [] 
