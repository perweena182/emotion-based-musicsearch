import webbrowser
import streamlit as st

lang=st.text_input("Language")

captured_emotion= "happy"

if lang:
    # webrtc_streamer (key="key", desired_playing_state=True
    #     video_processor_factory=Emotion Processor
   
    btn = st.button("Recommend me songs")  # Added '='
   
    if btn:
        if not captured_emotion:
            st.warning("Please let me capture your emotion first")
        else:
            #webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{captured_emotion}+song")
            search_query = f"https://www.youtube.com/results?search_query={lang}+{captured_emotion}+song"
           
            # Open the YouTube search results in a new browser window
            webbrowser.open(search_query)