from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import streamlit as st
import requests
from typing import List, Dict, Optional

class RAGAgent:
    def __init__(self):
        """Initialize the RAG Agent with API keys and create the agent crew."""
        try:
            self.ragie_api_key = st.secrets["RAGIE_API_KEY"]
            self.openai_api_key = st.secrets["OPENAI_API_KEY"]
            
            # Debugging output to verify API key retrieval
            print(f"RAGIE API Key: {self.ragie_api_key}")
            print(f"OpenAI API Key: {self.openai_api_key}")
            
            if not self.ragie_api_key or not self.openai_api_key:
                raise ValueError("Required API keys not found in secrets")
                
            # Initialize LLM with gpt-3.5-turbo
            self.llm = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                model="gpt-3.5-turbo"
            )
            
            # Create specialized agents
            self.formatter_agent = Agent(
                role='Text Formatter',
                goal='Format and clean meeting summaries for optimal readability',
                backstory='Expert at processing and formatting text while preserving meaning',
                llm=self.llm,
                tools=[self._create_formatting_tool()]
            )
            
            self.analyzer_agent = Agent(
                role='Content Analyzer',
                goal='Analyze and structure meeting content logically',
                backstory='Specialist in organizing information and identifying key points',
                llm=self.llm,
                tools=[self._create_analysis_tool()]
            )
            
            # Create the routing agent
            self.routing_agent = Agent(
                role='Query Router',
                goal='Determine the intent of user queries and route them appropriately',
                backstory='Expert in understanding user intent and categorizing queries',
                llm=self.llm,
                tools=[self._create_routing_tool()]
            )
            
        except Exception as e:
            st.error(f"Error initializing agents: {str(e)}")
            self.ragie_api_key = None

    def _create_formatting_tool(self):
        """Create a tool for text formatting."""
        return Tool(
            name="format_text",
            func=lambda text: self.llm.predict(
                f"""Format this text for optimal readability. Fix any merged words, 
                standardize bullet points, and ensure proper line breaks while 
                preserving all information: {text}"""
            ),
            description="Formats text for readability"
        )

    def _create_analysis_tool(self):
        """Create a tool for content analysis."""
        return Tool(
            name="analyze_content",
            func=lambda text: self.llm.predict(
                f"""Analyze this meeting summary and structure it logically with 
                clear sections and proper formatting: {text}"""
            ),
            description="Analyzes and structures content"
        )

    def _create_routing_tool(self):
        """Create a tool for routing queries."""
        return Tool(
            name="route_query",
            func=lambda query: self._route_query(query),
            description="Routes queries to the appropriate category"
        )
    
    def _route_query(self, query: str) -> List[Dict]:
        """Determine the intent of the query and delegate to the appropriate agent(s)."""
        try:
            intent = self.llm.predict(
                f"""Determine if this query is about meeting transcripts or client agreements. 
                Respond with 'test_meeting', 'test_client_agreements', or 'Query category not recognized. Please refine your query.' if unclear: {query}"""
            )
            print(f"Predicted intent: {intent}")
            
            # Delegate to the appropriate agent(s) based on intent
            if intent == 'test_meeting':
                return self.meeting_script_agent.retrieve_chunks()
            elif intent == 'test_client_agreements':
                return self.client_agreement_agent.retrieve_chunks()
            elif intent == "Query category not recognized. Please refine your query.":
                # Engage both agents if the category is not recognized
                meeting_chunks = self.meeting_script_agent.retrieve_chunks()
                agreement_chunks = self.client_agreement_agent.retrieve_chunks()
                return meeting_chunks + agreement_chunks
            else:
                # Handle any other unexpected intents
                st.warning("Unexpected intent received. Engaging both agents.")
                meeting_chunks = self.meeting_script_agent.retrieve_chunks()
                agreement_chunks = self.client_agreement_agent.retrieve_chunks()
                return meeting_chunks + agreement_chunks
        except Exception as e:
            print(f"Error during LLM prediction: {str(e)}")
            st.error("An error occurred while processing the query. Please try again later.")
            return []

    def get_recent_meeting_summaries(self) -> List[Dict]:
        """Fetch and process the 3 most recent meeting summaries."""
        if not self.ragie_api_key:
            print("No API key found")
            return []
        
        url = "https://api.ragie.ai/documents?page_size=3&filter=%7B%22folder%22%3A%20%7B%22%24eq%22%3A%20%22test_meetings%22%7D%7D"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.ragie_api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            documents = result.get('documents', [])
            
            # Process each document with the agent crew
            for doc in documents:
                doc['summary'] = self.process_meeting_summary(doc['id'])
            
            return documents
        except Exception as e:
            error_msg = f"Error fetching meeting summaries: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return []

    def process_meeting_summary(self, document_id: str) -> Optional[str]:
        """Fetch and return the raw meeting summary."""
        raw_summary = self._fetch_raw_summary(document_id)
        return raw_summary

    def _fetch_raw_summary(self, document_id: str) -> Optional[str]:
        """Fetch the raw summary from the API."""
        if not self.ragie_api_key:
            return None
            
        url = f"https://api.ragie.ai/documents/{document_id}/summary"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.ragie_api_key}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse the JSON response
            data = response.json()
            
            # Extract the summary text from the response
            # Adjust this based on the actual structure of your API response
            summary_text = data.get('summary', '')
            
            if not summary_text:
                st.warning(f"No summary found for document {document_id}")
                return None
            
            return summary_text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching meeting summary for document {document_id}: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return None
        except ValueError as e:
            error_msg = f"Error parsing JSON response for document {document_id}: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return None
