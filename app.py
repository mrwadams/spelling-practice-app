import streamlit as st
import random
import os
from gtts import gTTS
from io import BytesIO
import base64
import pandas as pd

# Constants for filenames and filepaths
WORD_LIST_ALIASES = {
    'year_1_2.txt': 'Year 1 & 2',
    'year_3_4.txt': 'Year 3 & 4',
}
CORRECT_SOUND_PATH = "static/correct.wav"
INCORRECT_SOUND_PATH = "static/incorrect.wav"

# Function to read words from a text file
def read_word_list(file_name):
    with open(f"word_lists/{file_name}", 'r') as f:
        return [line.strip() for line in f.readlines()]

# Functions to convert audio data to Base64 for web display
def audio_to_base64(audio_data):
    return base64.b64encode(audio_data.getbuffer()).decode()

def audio_file_to_base64(file_path):
    with open(file_path, 'rb') as f:
        audio_data = f.read()
    return base64.b64encode(audio_data).decode()

# Function to convert text to audio using Google Text to Speech
def text_to_audio(word):
    tts = gTTS(word, lang='en')
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

correct_audio_base64 = audio_file_to_base64(CORRECT_SOUND_PATH)
incorrect_audio_base64 = audio_file_to_base64(INCORRECT_SOUND_PATH)

# Main function to run the app
def app():
    st.title("Spelling Practice App")
    st.sidebar.header("About")

    # Sidebar information about the app
    with st.sidebar:
        st.markdown("""
        This app helps students practise spelling the Common Exception Words.
        
        To start, simply choose a word list from the menu and start practising.
        
        Listen to the pronunciation of the word and type the correct spelling in the text box."
        
        Press 'Check Answer' to see if your spelling is correct, and use the 'Next Word' button to go to a new word. Happy spelling!

        You can also view the full word list by selecting the 'View Word List' page.
        """)
        st.markdown("Created by [Matt Adams](https://www.linkedin.com/in/matthewrwadams/).")
        st.markdown("""---""")

    # Sidebar for selecting word list and page
    selected_word_list = st.sidebar.selectbox(
        "Choose a word list:",
        [file[:-4] for file in sorted(os.listdir('word_lists')) if file.endswith('.txt')],
        format_func=lambda x: WORD_LIST_ALIASES.get(x + '.txt', x)
    )
    st.session_state.word_list = selected_word_list

    # Initialize score if it doesn't exist in the session state
    if "score" not in st.session_state:
        st.session_state.score = 0

    # Sidebar for choosing the page
    page = st.sidebar.selectbox("Select a page:", ["Practise Spellings", "View Word List"])

    # Page to view the word list
    if page == "View Word List":
        st.header("View Word List 📖")
        if "word_list" in st.session_state:
            words = read_word_list(f"{st.session_state.word_list}.txt")
            st.write(pd.DataFrame(words, columns=["Words"]))
        else:
            st.warning("Please select a word list first.")

    # Page to practice spellings
    elif page == "Practise Spellings":
        st.header("Practise Spellings 📝")
        st.write(f"Score: {st.session_state.score}")
        if "word_list" in st.session_state:
            words = read_word_list(f"{st.session_state.word_list}.txt")

            if "selected_word" not in st.session_state:
                st.session_state.selected_word = random.choice(words)

            # Button to hear the word
            if st.button("Hear Word👂"):
                audio_data = text_to_audio(st.session_state.selected_word)
                base64_audio = audio_to_base64(audio_data)
                st.markdown(f'<audio controls autoplay src="data:audio/mp3;base64,{base64_audio}"/>', unsafe_allow_html=True)

            # Initialize user input key if it doesn't exist in the session state
            if "input_key" not in st.session_state:
                st.session_state.input_key = 0

            # Text input for user to enter the spelling
            user_input = st.text_input("Type the word:", key=st.session_state.input_key)

            check_col, next_col = st.columns(2)
            check_pressed = check_col.button("Check Answer ✅")

            # Check answer button logic
            if check_pressed:
                if user_input.strip() == '':
                    st.info("Please enter a spelling before checking the answer.")
                elif user_input.strip().lower() == st.session_state.selected_word.strip().lower():
                    st.success("Correct!")
                    st.markdown(f'<audio autoplay src="data:audio/wav;base64,{correct_audio_base64}"/>', unsafe_allow_html=True)
                    st.session_state.score += 1
                    st.session_state.selected_word = random.choice(words)
                else:
                    st.error(f"Oops! You typed '{user_input}'. The correct spelling is '{st.session_state.selected_word}'")
                    st.markdown(f'<audio autoplay src="data:audio/wav;base64,{incorrect_audio_base64}"/>', unsafe_allow_html=True)
                    st.session_state.selected_word = random.choice(words)

                # Reset the input field key to clear it
                st.session_state.input_key += 1

            # Next word button logic
            next_pressed = next_col.button("Next Word ➡️")

            if next_pressed:
                st.session_state.selected_word = random.choice(words)
                user_input = ''
        else:
            st.warning("Please select a word list first.")

if __name__ == "__main__":
    app()