import streamlit as st
from rag_agent import RAGAgent, RouterAgent

st.set_page_config(
    page_title="Meeting Summaries",
    page_icon="📝",
    layout="wide"
)

def main():
    st.title("Recent Meeting Summaries")
    
    # Initialize RAGAgent
    agent = RAGAgent()
    
    # Initialize RouterAgent with the RAGAgent instance
    router_agent = RouterAgent(rag_agent=agent)
    
    # Add a refresh button
    if st.button("Refresh Meetings"):
        with st.spinner("Fetching meetings..."):
            meetings = agent.get_recent_meeting_summaries()
            
            if meetings:
                for meeting in meetings:
                    title = meeting.get('name', 'Untitled')
                    created_at = meeting.get('created_at', 'Unknown date')
                    
                    with st.expander(f"Meeting: {title} ({created_at})"):
                        st.write(f"Document ID: {meeting.get('id')}")
                        summary = meeting.get('summary', 'No summary available')
                        if summary:
                            st.markdown(summary)
                        else:
                            st.warning("No summary available for this meeting")
            else:
                st.warning("No meetings found or error occurred while fetching meetings.")
    
    # Add a text input box for user queries
    user_query = st.text_input("Ask a question about the meeting summaries:")
    
    # Add a button to submit the query
    if st.button("Submit Query"):
        st.write("Query submitted:", user_query)
        
        # Use RouterAgent to process the query
        try:
            processed_query = router_agent.process_query(user_query)
            st.write("RouterAgent processed query:", processed_query)
        except Exception as e:
            st.error(f"An error occurred while processing the query: {str(e)}")
            st.write("Exception type:", type(e))
            st.write("Exception args:", e.args)

if __name__ == "__main__":
    main()
