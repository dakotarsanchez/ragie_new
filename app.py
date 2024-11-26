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
                    with st.expander(f"Meeting: {meeting.get('name', 'Untitled')}"):
                        st.write(f"ID: {meeting.get('id')}")
                        st.write(f"Created: {meeting.get('created_at')}")
                        st.write(f"Updated: {meeting.get('updated_at')}")
            else:
                st.warning("No meetings found or error occurred while fetching meetings.")

if __name__ == "__main__":
    main()
