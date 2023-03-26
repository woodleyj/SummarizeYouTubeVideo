import os
import datetime
import math
import numpy as np
from pytube import YouTube
import streamlit as st
import openai
import whisper
import tiktoken

# CONFIG
AUDIO_FILENAME = "temp-audio.mp4"
TRANSCRIPT_DIR = "transcripts"
MAX_PROMPT_TOKENS = 3000
GPT_MODEL = "gpt-3.5-turbo"
TIKTOKEN_ENCODING_TYPE = tiktoken.encoding_for_model(GPT_MODEL)
SYSTEM_PROMPT = "You are a helpful assistant."

st.set_page_config(layout="wide")

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

def transcribe_audio(transcript_filename):
    model = whisper.load_model("base")
    result = model.transcribe(AUDIO_FILENAME, fp16=False)
    with open(f"{TRANSCRIPT_DIR}//{transcript_filename}", "a") as f:
        f.write(result["text"])

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
    st.title("YouTube Video Summarizer")
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    openai.api_key = api_key
    youtube_url = st.text_input("Enter the YouTube URL of the video you want to summarize:")

    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "transcript_filename" not in st.session_state:
        st.session_state.transcript_filename = None

    summarize_button = st.button("Summarize", on_click=lambda: setattr(st.session_state, "is_processing", True), disabled=st.session_state.is_processing or not api_key or not youtube_url)

    if summarize_button and st.session_state.is_processing:
        try:
            with st.spinner("Downloading audio..."):
                st.session_state.transcript_filename = download_audio(youtube_url)
            with st.spinner("Transcribing audio..."):
                transcribe_audio(st.session_state.transcript_filename)
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
        st.download_button(
            label="Download Transcript",
            data=transcript_data,
            file_name=st.session_state.transcript_filename,
            mime="text/plain",
        )

if __name__ == "__main__":
    main()