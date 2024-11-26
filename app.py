import streamlit as st
from rag_agent import RAGAgent

st.set_page_config(
    page_title="Meeting Summaries",
    page_icon="📝",
    layout="wide"
)

def main():
    st.title("Recent Meeting Summaries")
    
    # Initialize RAGAgent
    agent = RAGAgent()
    
    # Add a refresh button
    if st.button("Refresh Meetings"):
        with st.spinner("Fetching meetings..."):
            meetings = agent.get_recent_meeting_summaries()
            
            if meetings:
                for meeting in meetings:
                    # Use a more descriptive title from the document metadata
                    title = meeting.get('name', 'Untitled')
                    created_at = meeting.get('created_at', 'Unknown date')
                    
                    with st.expander(f"Meeting: {title} ({created_at})"):
                        # Display document metadata
                        st.write(f"Document ID: {meeting.get('id')}")
                        
                        # Display the raw summary text
                        summary = meeting.get('summary', 'No summary available')
                        if summary:
                            st.markdown(summary)  # Use markdown to render any formatting in the summary
                        else:
                            st.warning("No summary available for this meeting")
            else:
                st.warning("No meetings found or error occurred while fetching meetings.")
    
    # Add a text input box for user queries
    user_query = st.text_input("Ask a question about the meeting summaries:")
    
    # Add a button to submit the query
    if st.button("Submit Query"):
        st.write("Query submitted:", user_query)
        
        # Use the routing agent to determine the query category
        try:
            category = agent.routing_agent.tools[0].func(user_query)
            st.write("Predicted category:", category)
            
            if category == "test_meeting":
                st.write("Routing to meeting transcripts processing...")
                # Add logic to handle meeting transcripts queries
            elif category == "test_client_agreements":
                st.write("Routing to client agreements processing...")
                # Add logic to handle client agreements queries
            elif category == "both":
                st.write("Query is ambiguous; processing for both meeting transcripts and client agreements...")
                # Add logic to handle both categories
            else:
                st.warning("Query category not recognized. Please refine your query.")
        except Exception as e:
            st.error(f"An error occurred while processing the query: {str(e)}")
            st.write("Exception type:", type(e))
            st.write("Exception args:", e.args)

if __name__ == "__main__":
    main()
