import streamlit as st
from gtts import gTTS
import os
from googletrans import Translator
import pandas as pd
import time
import tempfile

def translate_text(text, source_language, target_languages):
    """
    Translates the input text into multiple languages.

    Args:
        text (str): The text to be translated.
        source_language (str): The source language code.
        target_languages (list): List of target language codes.

    Returns:
        dict: A dictionary containing translated text for each target language.
    """
    translator = Translator()
    translations = {}
    for target_language in target_languages:
        translation = translator.translate(text, src=source_language, dest=target_language)
        translations[target_language] = translation.text
    return translations

def synthesize_speech(text, lang_code, voice=None):
    """
    Synthesizes speech from the input text in the specified language and voice.

    Args:
        text (str): The text to synthesize.
        lang_code (str): Language code for the text.
        voice (str): The voice to use for speech synthesis.

    Returns:
        bytes: Audio file as bytes.
    """
    tts = gTTS(text, lang=lang_code, tld='com', slow=False, lang_check=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        audio_bytes = open(fp.name, "rb").read()
    os.unlink(fp.name)
    return audio_bytes

# Streamlit layout
st.title("Text Translator and Speech Synthesizer")

# Sidebar for user input options
st.sidebar.title("Options")
input_option = st.sidebar.radio("Select Input Option:", ("Enter Text", "Upload File"))

if input_option == "Enter Text":
    # Text input
    text_to_translate = st.text_area("Enter text to translate:", height=200)
elif input_option == "Upload File":
    # File upload
    uploaded_file = st.sidebar.file_uploader("Upload a file (PDF, TXT, Excel, CSV):", type=["pdf", "txt", "xlsx", "csv"])

    if uploaded_file is not None:
        # Read file content
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext == ".pdf":
            text_to_translate = "".join(pdftotext(uploaded_file))
        elif file_ext == ".txt":
            text_to_translate = uploaded_file.getvalue().decode("utf-8")
        elif file_ext in (".xlsx", ".csv"):
            df = pd.read_excel(uploaded_file) if file_ext == ".xlsx" else pd.read_csv(uploaded_file)
            text_to_translate = " ".join(df.iloc[:, 0].astype(str))
        else:
            st.sidebar.error("Unsupported file format. Please upload a PDF, TXT, Excel, or CSV file.")
            text_to_translate = ""

# Source language selection
source_language = st.sidebar.selectbox("Select source language:", ["Auto", "English", "French", "Spanish", "German", "Japanese", "Hindi", "Bengali", "Gujarati", "Kannada", "Malayalam", "Marathi", "Punjabi", "Tamil", "Telugu", "Urdu"])

# Target language selection (multiple)
st.sidebar.write("Select target languages:")
target_languages = st.sidebar.multiselect("Select target languages:", ["English", "French", "Spanish", "German", "Japanese", "Hindi", "Bengali", "Gujarati", "Kannada", "Malayalam", "Marathi", "Punjabi", "Tamil", "Telugu", "Urdu"])

# Mapping language names to language codes
language_codes = {
    "Auto": "auto",
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Japanese": "ja",
    "Hindi": "hi",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur"
}

# Voice selection
st.sidebar.write("Select voice:")
voices = {
    "Default": None,
    "Female": "female",
    "Male": "male",
    "Indian Female": "en-in",
    "Indian Male": "hi-in",
    "UK Female": "en-uk",
    "UK Male": "en-uk-north",
    "US Female": "en-us",
    "US Male": "en-us",
    "Australian Female": "en-au"
}
selected_voice = st.sidebar.selectbox("Select voice:", list(voices.keys()))

# Button to trigger translation and synthesis
translate_button = st.sidebar.button("Translate and Synthesize")

# Main content area
st.sidebar.markdown("---")

if translate_button:
    # Check if text is entered
    if not text_to_translate:
        st.error("Please enter text to translate.")
    else:
        # Translate text
        source_language_code = language_codes[source_language]
        target_language_codes = [language_codes[lang] for lang in target_languages]
        
        # Display loading spinner during translation
        with st.spinner("Translating..."):
            time.sleep(3)  # Simulate translation process
            try:
                translations = translate_text(text_to_translate, source_language_code, target_language_codes)
            except Exception as e:
                st.error(f"Translation error: {str(e)}")
                st.stop()  # Stop execution if translation fails
        
        # Display translated text for each target language
        if translations:
            st.write("Translated Text:")
            for lang, translation in translations.items():
                st.subheader(f"{lang}:")
                st.write(translation)

                # Synthesize speech for each translation and provide audio player
                try:
                    audio_bytes = synthesize_speech(translation, lang, voice=voices[selected_voice])
                    st.audio(audio_bytes, format="audio/mp3")  # Play audio directly within the application
                except Exception as e:
                    st.error(f"Speech synthesis error: {str(e)}")
