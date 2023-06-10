import base64
import os
import random
from io import BytesIO

import pandas as pd
import streamlit as st
from gtts import gTTS

# Constants for filenames and filepaths
WORD_LIST_ALIASES = {
    'year_1_2.txt': 'Year 1 & 2',
    'year_3_4.txt': 'Year 3 & 4',
}
CORRECT_SOUND_PATH = "static/correct.wav"
INCORRECT_SOUND_PATH = "static/incorrect.wav"

# Initialize incorrect words set if it doesn't exist in the session state
if "incorrect_words" not in st.session_state:
    st.session_state.incorrect_words = set()

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
    tts = gTTS(word, lang='en-uk')
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

correct_audio_base64 = audio_file_to_base64(CORRECT_SOUND_PATH)
incorrect_audio_base64 = audio_file_to_base64(INCORRECT_SOUND_PATH)

# Main function to run the app
def app():
    st.title("Spelling Practice App")

    # Sidebar for selecting word list
    selected_word_list = st.sidebar.selectbox(
        "Choose a word list:",
        [file[:-4] for file in sorted(os.listdir('word_lists')) if file.endswith('.txt')],
        format_func=lambda x: WORD_LIST_ALIASES.get(x + '.txt', x)
    )
    st.session_state.word_list = selected_word_list

    # Sidebar for choosing the page
    page = st.sidebar.selectbox("Select a page:", ["Practise Spellings", "View Word List", "View Incorrectly Spelled Words"])

    st.sidebar.markdown("""---""")
    st.sidebar.header("How to Use")
    with st.sidebar:
        st.markdown("""
        1. To start, simply choose a word list from the menu above.
        
        2. Click 'New Word' to select a new word to spell.

        3. Listen to the the word and then try to spell it in the text box.
        
        4. Press 'Check Answer' to see if your spelling is correct.
        
        Happy spelling!

        You can look at the full word lists by selecting the 'View Word List' page.

        You can also view the words you have spelt incorrectly by selecting the 'View Incorrectly Spelled Words' page.
        """)
        st.markdown("""---""")

    st.sidebar.header("About")

    # Sidebar information about the app
    with st.sidebar:
        st.markdown("""
        This app is designed to help children practise spelling the Common Exception Words.
        
        No personal data is collected or stored by this app. 
        """)
        st.markdown("Created by [Matt Adams](https://www.linkedin.com/in/matthewrwadams/)")
        st.markdown("Source code available on [GitHub](https://github.com/mrwadams/spelling-practice-app)")
        st.markdown("""---""")
    

    # Initialize score and total attempts if they don't exist in the session state
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "total_attempts" not in st.session_state:
        st.session_state.total_attempts = 0


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
        st.markdown("""---""")
        if "word_list" in st.session_state:
            words = read_word_list(f"{st.session_state.word_list}.txt")

            if "selected_word" not in st.session_state:
                st.session_state.selected_word = random.choice(words)
                audio_data = text_to_audio(st.session_state.selected_word)
                st.session_state.base64_audio = audio_to_base64(audio_data)

            if st.button("New Word ✨"):
                st.session_state.selected_word = random.choice(words)
                audio_data = text_to_audio(st.session_state.selected_word)
                st.session_state.base64_audio = audio_to_base64(audio_data)

            # Render the audio widget every time the page is displayed
            st.markdown(f'<audio controls autoplay src="data:audio/mp3;base64,{st.session_state.base64_audio}"/>', unsafe_allow_html=True)

            if "input_key" not in st.session_state:
                st.session_state.input_key = 0

            user_input = st.text_input("Type the word:", key=st.session_state.input_key)

            check_col = st.columns(1)
            check_pressed = check_col[0].button("Check Answer ✅")

            # Check answer button logic
            if check_pressed:
                if user_input.strip() == '':
                    st.info("Please enter a spelling before checking the answer.")
                else:
                    st.session_state.total_attempts += 1
                    if user_input.strip().lower() == st.session_state.selected_word.strip().lower():
                        st.success("Correct!")
                        st.markdown(f'<audio autoplay src="data:audio/wav;base64,{correct_audio_base64}"/>', unsafe_allow_html=True)
                        st.session_state.score += 1
                        st.session_state.selected_word = random.choice(words)
                        audio_data = text_to_audio(st.session_state.selected_word)
                        st.session_state.base64_audio = audio_to_base64(audio_data)
                    else:
                        st.error(f"Oops! You typed '{user_input}'. The correct spelling is '{st.session_state.selected_word}'")
                        st.markdown(f'<audio autoplay src="data:audio/wav;base64,{incorrect_audio_base64}"/>', unsafe_allow_html=True)
                        st.session_state.incorrect_words.add(st.session_state.selected_word)
                        st.session_state.selected_word = random.choice(words)
                        audio_data = text_to_audio(st.session_state.selected_word)
                        st.session_state.base64_audio = audio_to_base64(audio_data)

                    st.session_state.input_key += 1

            st.write(f"Score: {st.session_state.score} out of {st.session_state.total_attempts}")
            st.markdown("""---""")
            with st.expander("Note for Teachers / Parents"):
                st.markdown("""
        It's best for children to use this app on a laptop / desktop computer. This is because software keyboards on mobile devices often autocorrect spelling mistakes, which defeats the purpose of a spelling app! 🙂
        """)
        else:
            st.warning("Please select a word list first.")

    elif page == "View Incorrectly Spelled Words":
        st.header("Words to Review 📖")
        if st.session_state.incorrect_words:
            st.write(pd.DataFrame(sorted(list(st.session_state.incorrect_words)), columns=["Words"]))
        else:
            st.info("You have not misspelled any words in this session yet.")        

if __name__ == "__main__":
    app()
