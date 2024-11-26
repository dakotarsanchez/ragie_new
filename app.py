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
        # Backend logic to handle the query will be added here

if __name__ == "__main__":
    main()
