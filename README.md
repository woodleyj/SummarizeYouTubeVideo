# YouTube Video Summarizer

## Overview
YouTube Video Summarizer is a web application that allows you to generate a summary of any YouTube video with ease. This powerful tool can transcribe the audio of a YouTube video, and then use advanced AI to produce a concise summary of the content. It's a great way to quickly understand the key points of a video without having to watch the entire thing.

## Features
- Transcription of YouTube video audio
- Automatic language detection
- Summarization of video content using advanced AI
- Downloadable transcripts with summaries
- User-friendly and intuitive interface

## How to Use (Local Setup)

1. Clone the repository or download the app.py file to your local machine.

2. Install the required packages by running `pip install -r requirements.txt`.

3. Run the app using `streamlit run app.py`.

4. Open your browser and navigate to the URL provided by Streamlit.

5. Follow the steps explained in the "Using the App" section below.

## How to Use (Streamlit Cloud)

1. Navigate to the YouTube Video Summarizer app hosted on Streamlit Cloud (the app URL will be provided by the app owner or administrator).

2. Follow the steps explained in the "Using the App" section below.

## Using the App

1. Enter your OpenAI API key in the text input field. This is necessary for the app to function correctly.

2. Enter the YouTube URL of the video you want to summarize in the "Enter the YouTube URL of the video you want to summarize:" text input field.

3. Choose the language of the video from the "Select language:" dropdown menu. You can choose "Autodetect" if you're unsure of the language.

4. Click on the ![Summarize button](images/summarize_button.png) button to start the summarization process. The app will first download the audio, transcribe it, and then generate a summary. This may take a few moments depending on the length of the video.

5. Once the summary is generated, it will be displayed on the screen. You can read the summary directly in the app or download the full transcript (including the summary) by clicking on the "Download Transcript" button.

## FAQ

### Q: Why is the transcription a different language than the audio's language?

A: There could be a few reasons why the transcription may not match the language of the audio:

1. **Language detection error**: If you have selected "Autodetect" in the "Select language:" dropdown menu, the app relies on its language detection feature to identify the language of the video. In some cases, the detection may not be accurate, leading to transcription in the wrong language.

2. **Language selection error**: If you have manually chosen a language in the "Select language:" dropdown menu, ensure that you have selected the correct language for the video. If the wrong language is chosen, the transcription will not match the audio's language.

3. **Mixed languages in the video**: If the video contains multiple languages or switches between languages during the course of the video, the transcription may not accurately represent all languages in the video. The app is currently designed to work best with a single language per video.

To resolve the issue, try selecting the correct language from the "Select language:" dropdown menu instead of using "Autodetect" or ensure that the correct language is chosen if you have manually selected one.

### Q: Is there any cost associated with using this app?

A: The app itself is free to use, but it relies on the OpenAI API, which has its own pricing. Please refer to OpenAI's pricing page for more information about API usage costs.

### Q: Are there any limitations on the length of the YouTube videos that can be summarized?

A: There's no strict limitation on the length of the videos. However, longer videos may take more time to process and may consume more tokens from your OpenAI API quota. Keep in mind that the summarization process might be less accurate for extremely long videos due to token limitations.

### Q: How can I obtain an OpenAI API key?

A: You can apply for access to the OpenAI API on the OpenAI website. Once approved, you will receive an API key that you can use with this app.

### Q: Can I use the app without an OpenAI API key?

A: Unfortunately, you cannot use the app without a valid OpenAI API key, as the summarization feature relies on OpenAI's GPT-3 model.

### Q: Is the app safe to use? What happens to the data I input?

A: The app is designed for personal use, and the data you input is only used for the purpose of generating the summary. For users running the app locally, the transcriptions and summaries are saved in a folder called "transcripts" in the same directory as the app.py file. If you're using the app on Streamlit Cloud, the app owner/host should provide more information about data handling.

### Q: How accurate is the transcription and summarization provided by the app?

A: The app uses advanced AI models for both transcription and summarization, which generally provide high-quality results. However, the accuracy may vary depending on factors such as audio quality, language, and the complexity of the content. Please note that the app is not perfect, and it's always a good idea to review the generated summary for accuracy and completeness.

### Q: Can I use the app for languages other than English?

A: Currently, the app primarily supports English for transcription and summarization. However, the app's language detection feature can identify other languages in the video. Support for more languages may be added in the future.

If you have any other questions or need further assistance, feel free to reach out to the app owner or administrator.

## Notes
This application makes use of the OpenAI API and requires a valid API key to function. Please ensure that you have a valid key before attempting to use the app.

For users running the app locally, the transcriptions and summaries generated by the app are saved in a folder called "transcripts" in the same directory as the app.py file. This folder will be created automatically if it does not already exist.

Please note that this app is intended for personal use and is not affiliated with YouTube or OpenAI.