import os
import datetime
import math
import sys
import openai
import whisper
import tiktoken
import backoff
import streamlit as st
import numpy as np
from pytube import YouTube
from contextlib import contextmanager
from io import StringIO
from streamlit.runtime.scriptrunner.script_run_context import SCRIPT_RUN_CONTEXT_ATTR_NAME
from threading import current_thread


# CONFIG
AUDIO_FILENAME = "temp-audio.mp4"
TRANSCRIPT_DIR = "transcripts"
MAX_PROMPT_TOKENS = 3000
GPT_MODEL = "gpt-3.5-turbo"
TIKTOKEN_ENCODING_TYPE = tiktoken.encoding_for_model(GPT_MODEL)
SYSTEM_PROMPT = "You are a helpful assistant."

st.set_page_config(layout="wide")

@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                buffer.write(b)
                output_func(buffer.getvalue())
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write

@contextmanager
def st_stdout(dst):
    with st_redirect(sys.stdout, dst):
        yield

@contextmanager
def st_stderr(dst):
    with st_redirect(sys.stderr, dst):
        yield

def download_audio(url):
    yt = YouTube(url)
    channel = ''.join(letter for letter in yt.author if letter.isalnum() or letter == ' ')
    fn = ''.join(letter for letter in yt.title if letter.isalnum() or letter == ' ')
    now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    transcript_filename = f"{channel} -- {fn} -- {now}.txt"
    with open(f"{TRANSCRIPT_DIR}//{transcript_filename}", "w") as f:
        f.write(f"Video URL: {url}\n\n")
    yt.streams.filter(only_audio=True).first().download(filename=AUDIO_FILENAME)
    return transcript_filename

def transcribe_audio(transcript_filename, language):
    model = whisper.load_model("base")
    if language == "Autodetect":
        language = None
        # detect language of video and display to user
        audio = whisper.load_audio(AUDIO_FILENAME)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        # detect language
        _, probs = model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        with st_stdout("info"):
            print(f"Detected language: {detected_language}")
    else:
        language = "en"
    with st_stdout("code"):
        result = model.transcribe(AUDIO_FILENAME, fp16=False, no_speech_threshold=0.7, language="en", verbose=True)
    with open(f"{TRANSCRIPT_DIR}//{transcript_filename}", "a") as f:
        f.write(result["text"])

@backoff.on_exception(backoff.expo, openai.error.RateLimitError, openai.error.Timeout, max_time=60)
def summarize_audio(transcript_filename):
    with open(f"{TRANSCRIPT_DIR}//{transcript_filename}", "r") as f:
        transcript = f.read()
    words = transcript.split(" ")
    encoding = TIKTOKEN_ENCODING_TYPE
    num_tokens = len(encoding.encode(transcript))
    num_chunks = math.ceil(num_tokens / MAX_PROMPT_TOKENS)
    chunks = np.array_split(words, num_chunks)
    summary_responses = []
    for chunk in chunks:
        sentences = ' '.join(list(chunk))
        prompt = f"{sentences}\n\ntl;dr:"
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
    ]
    )
        summary_responses.append(response.choices[0].message.content)
    full_summary = ''.join(summary_responses)
    with open(f"{TRANSCRIPT_DIR}//{transcript_filename}", "a") as f:
        f.write(f"\n\n====SUMMARY====\nNumber of tokens in transcript: {num_tokens}\n\n{full_summary}\n\n")
    return full_summary

def main():
    # Add the title and GitHub link at the top
    st.markdown("# YouTube Video Summarizer")
    st.markdown("[README](https://github.com/woodleyj/SummarizeYouTubeVideo)")
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    api_key = st.text_input("Enter your OpenAI API key:", type="password", key="api_key")
    openai.api_key = api_key
    youtube_url = st.text_input("Enter the YouTube URL of the video you want to summarize:", key="youtube_url")
    language = st.selectbox("Select language:", ["English", "Autodetect"])

    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "transcript_filename" not in st.session_state:
        st.session_state.transcript_filename = None

    summarize_button = st.button("Summarize", on_click=lambda: setattr(st.session_state, "is_processing", True), disabled=st.session_state.is_processing or not api_key or not youtube_url)

    # Create a placeholder for the download button
    download_button_placeholder = st.empty()

    if summarize_button and st.session_state.is_processing:
        try:
            with st.spinner("Downloading audio..."):
                st.session_state.transcript_filename = download_audio(youtube_url)
            with st.spinner("Transcribing audio..."):
                transcribe_audio(st.session_state.transcript_filename, language)
            with st.spinner("Summarizing transcript..."):
                st.session_state.summary = summarize_audio(st.session_state.transcript_filename)
            st.session_state.is_processing = False
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.is_processing = False

    if st.session_state.summary and st.session_state.transcript_filename:
        st.write(st.session_state.summary)
        with open(f"{TRANSCRIPT_DIR}//{st.session_state.transcript_filename}", "r") as file:
            transcript_data = file.read()
        # Update the download button placeholder when the file is ready to be downloaded
        download_button_placeholder.download_button(
            label="Download Transcript",
            data=transcript_data,
            file_name=st.session_state.transcript_filename,
            mime="text/plain",
        )
    # else:
    #     # Show the disabled download button when the file is not ready
    #     download_button_placeholder.download_button(
    #         label="Download Transcript",
    #         data="",
    #         file_name="",
    #         mime="text/plain",
    #         disabled=True,
    #     )

if __name__ == "__main__":
    main()