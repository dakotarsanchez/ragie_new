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
            
            # Initialize the meeting script agent
            self.meeting_script_agent = Agent(
                role='Meeting Script Processor',
                goal='Retrieve and process meeting scripts',
                backstory='Expert in handling and analyzing meeting scripts',
                llm=self.llm,
                tools=[self._create_meeting_script_tool()]
            )
            
            # Initialize the intent determination agent
            self.intent_determination_agent = Agent(
                role='Intent Determination',
                goal='Determine if a query is related to meeting notes, client agreements, or both',
                backstory='Expert in understanding and categorizing user queries',
                llm=self.llm,
                tools=[self._create_intent_determination_tool()]
            )
            
            # Initialize the meeting notes agent
            self.meeting_notes_agent = Agent(
                role='Meeting Notes Processor',
                goal='Process and analyze meeting notes',
                backstory='Expert in handling meeting notes',
                llm=self.llm,
                tools=[self._create_meeting_notes_tool()]
            )

            # Initialize the client agreement agent
            self.client_agreement_agent = Agent(
                role='Client Agreement Processor',
                goal='Process and analyze client agreements',
                backstory='Expert in handling client agreements',
                llm=self.llm,
                tools=[self._create_client_agreement_tool()]
            )
            
            # Initialize the summarizer agent
            self.summarizer_agent = Agent(
                role='Summarizer',
                goal='Summarize relevant meeting notes and client agreements',
                backstory='Expert in synthesizing information from multiple sources',
                llm=self.llm,
                tools=[self._create_summarizer_tool()]
            )
            
        except Exception as e:
            st.error(f"Error initializing agents: {str(e)}")
            self.ragie_api_key = None

    def _create_formatting_tool(self):
        """Create a tool for text formatting."""
        return Tool(
            name="format_text",
            func=lambda text: self.llm.invoke(
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
            func=lambda text: self.llm.invoke(
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
    
    def _route_query(self, query: str) -> str:
        """Save and return the user query for confirmation."""
        try:
            # Save the query to a variable
            self.last_query = query
            
            # Print the query to confirm it is passed correctly
            print(f"Received query: {self.last_query}")
            
            # Return the query
            return self.last_query

        except Exception as e:
            print(f"Error during query handling: {str(e)}")
            st.error("An error occurred while processing the query. Please try again later.")
            return ""

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

    def _create_meeting_script_tool(self):
        """Create a tool for processing meeting scripts."""
        return Tool(
            name="process_meeting_script",
            func=self.process_meeting_script,
            description="Processes meeting scripts to extract key information"
        )
    
    def retrieve_meeting_scripts(self) -> List[Dict]:
        """Retrieve meeting scripts from a data source."""
        # Example: Fetch meeting scripts from an API
        url = "https://api.example.com/meeting_scripts"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.ragie_api_key}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            scripts = response.json().get('scripts', [])
            return scripts
        except Exception as e:
            error_msg = f"Error retrieving meeting scripts: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return []
    
    def process_meeting_script(self, script_id: str) -> Optional[str]:
        """Process a specific meeting script."""
        # Fetch the raw script data
        raw_script = self._fetch_raw_script(script_id)
        
        if raw_script:
            # Example processing: Summarize the script
            summary = self.llm.predict(
                f"Summarize the following meeting script: {raw_script}"
            )
            return summary
        else:
            return None
    
    def _fetch_raw_script(self, script_id: str) -> Optional[str]:
        """Fetch the raw meeting script from the data source."""
        url = f"https://api.example.com/meeting_scripts/{script_id}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.ragie_api_key}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('script', '')
        except Exception as e:
            error_msg = f"Error fetching meeting script for ID {script_id}: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return None

    def _create_intent_determination_tool(self):
        """Create a tool for determining the intent of a query."""
        return Tool(
            name="determine_intent",
            func=self.determine_intent,
            description="Determines if a query is related to meeting notes, client agreements, or both"
        )

    def determine_intent(self, query: str) -> str:
        """Use the LLM to determine the intent of the query and trigger appropriate agents."""
        try:
            ai_message = self.llm.invoke(
                f"""Determine the intent of the following query. Is it related to meeting notes, 
                client agreements, or both? Provide a clear answer: {query}"""
            )
            
            # Debugging: Print the ai_message to understand its structure
            print(f"AI Message: {ai_message}")

            # Assuming ai_message is a string or has a content attribute
            if isinstance(ai_message, str):
                intent = ai_message.strip().lower()
            else:
                # Adjust this based on the actual structure of ai_message
                intent = ai_message.content.strip().lower()

            # Trigger agents based on the determined intent
            if "meeting notes" in intent:
                print("Triggering Meeting Notes Agent")
                self.meeting_notes_agent.tools[0].func(query)
            if "client agreements" in intent:
                print("Triggering Client Agreement Agent")
                self.client_agreement_agent.tools[0].func(query)
            if "both" in intent or "unclear" in intent:
                print("Triggering both Meeting Notes and Client Agreement Agents")
                self.meeting_notes_agent.tools[0].func(query)
                self.client_agreement_agent.tools[0].func(query)

            return intent
        except Exception as e:
            error_msg = f"Error determining intent: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return "Error determining intent"

    def _create_meeting_notes_tool(self):
        """Create a tool for processing meeting notes."""
        return Tool(
            name="process_meeting_notes",
            func=self.process_meeting_notes,
            description="Processes meeting notes to extract key information"
        )

    def _create_client_agreement_tool(self):
        """Create a tool for processing client agreements."""
        return Tool(
            name="process_client_agreements",
            func=self.process_client_agreements,
            description="Processes client agreements to extract key information"
        )

    def process_meeting_notes(self, query: str) -> Optional[str]:
        """Process meeting notes based on the query by querying the Ragie AI API."""
        print(f"Processing meeting notes for query: {query}")
        
        # Define the API endpoint and payload
        url = "https://api.ragie.ai/retrievals"
        payload = {
            "rerank": True,
            "query": query,
            "top_k": 8,
            "filter": {"folder": {"$eq": "test_meetings"}}
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.ragie_api_key}"
        }
        
        try:
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            output = response.json()
            
            # Extract and return the relevant chunks
            scored_chunks = output.get('scored_chunks', [])
            relevant_texts = [chunk['text'] for chunk in scored_chunks]
            return "\n".join(relevant_texts)
        
        except requests.exceptions.HTTPError as err:
            error_msg = f"HTTP error occurred: {err}"
            print(error_msg)
            st.error(error_msg)
            return None
        except Exception as err:
            error_msg = f"Other error occurred: {err}"
            print(error_msg)
            st.error(error_msg)
            return None

    def process_client_agreements(self, query: str) -> Optional[str]:
        """Process client agreements based on the query by querying the Ragie AI API."""
        print(f"Processing client agreements for query: {query}")
        
        # Define the API endpoint and payload
        url = "https://api.ragie.ai/retrievals"
        payload = {
            "rerank": True,
            "query": query,
            "top_k": 8,
            "filter": {"folder": {"$eq": "test_client_agreements"}}
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.ragie_api_key}"
        }
        
        try:
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            output = response.json()
            
            # Extract and return the relevant chunks
            scored_chunks = output.get('scored_chunks', [])
            relevant_texts = [chunk['text'] for chunk in scored_chunks]
            return "\n".join(relevant_texts)
        
        except requests.exceptions.HTTPError as err:
            error_msg = f"HTTP error occurred: {err}"
            print(error_msg)
            st.error(error_msg)
            return None
        except Exception as err:
            error_msg = f"Other error occurred: {err}"
            print(error_msg)
            st.error(error_msg)
            return None

    def _create_summarizer_tool(self):
        """Create a tool for summarizing information."""
        return Tool(
            name="summarize_information",
            func=self.summarize_information,
            description="Summarizes meeting notes and client agreements"
        )

    def summarize_information(self, meeting_notes: str, client_agreements: str) -> str:
        """Summarize the provided meeting notes and client agreements."""
        combined_text = f"Meeting Notes:\n{meeting_notes}\n\nClient Agreements:\n{client_agreements}"
        summary = self.llm.invoke(
            f"Summarize the following information into a concise and useful output: {combined_text}"
        )
        return summary

class RouterAgent:
    def __init__(self, rag_agent: RAGAgent):
        self.rag_agent = rag_agent

    def process_query(self, query: str) -> str:
        """Process the query using the intent determination agent."""
        print(f"RouterAgent received query: {query}")
        intent = self.rag_agent.intent_determination_agent.tools[0].func(query)
        print(f"Determined intent: {intent}")

        meeting_notes_result = ""
        client_agreements_result = ""

        # Trigger the appropriate agent based on the intent
        if "meeting notes" in intent:
            print("Triggering Meeting Notes Agent")
            meeting_notes_result = self.rag_agent.meeting_notes_agent.tools[0].func(query)
        
        if "client agreements" in intent:
            print("Triggering Client Agreement Agent")
            client_agreements_result = self.rag_agent.client_agreement_agent.tools[0].func(query)
            print(f"Client Agreement Agent Output: {client_agreements_result}")

        # Use the summarizer agent to create a useful output
        summary = self.rag_agent.summarizer_agent.tools[0].func(meeting_notes_result, client_agreements_result)
        print(f"Summarizer Agent Output: {summary}")
        return summary
