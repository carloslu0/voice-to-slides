import requests
import json
import streamlit as st
from streamlit.logger import get_logger
import openai
import os

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Voice Notes to Deck",
        page_icon="🎙️",
    )

    st.write("# Voice notes to deck mini-app")


    uploaded_file = st.file_uploader("Choose a file", type=['mp3', 'wav', 'mp4', 'avi'])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        # Send the file to Deepgram for transcription
        url = "https://api.deepgram.com/v1/listen?tier=nova&filler_words=false&summarize=v2"
        payload = bytes_data
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f'Token {st.secrets["DEEPGRAM_API_KEY"]}'
        }
        response = requests.post(url, data=payload, headers=headers)
        response_json = response.json()
        transcription = response_json['results']['channels'][0]['alternatives'][0]['transcript']
        st.write(transcription)

        # Save the transcription as a variable
        user_message = transcription

        # Set the OpenAI API key
        openai.api_key = st.secrets["OPENAI_API_KEY"]

        # Send a request to GPT4's chat completion endpoint using the transcription as the user message
        gpt4_response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {
                    'role': 'system',
                    'content': """You are a world-class developer specializing in APIs. 
                    You help clients send a POST request to the Slides.com API by 
                    transforming transcripts of their voice notes into JSON that is accepted by the API.
                    Follow the example below delimited by <example></example tags.
                    <example>
                    { 
        "title": "My Deck",
        "loop": false,
        "slide-number": true,
        "theme-font": "overpass",
        "transition": "convex",
        "slides": [
            {
                "notes": "These are speaker notes, the'll only appear when this deck is presented.",
                "blocks": [
                    {
                        "type": "text",
                        "value": "Deck JSON Example",
                        "format": "h1"
                    },
                    {
                        "type": "text",
                        "value": "This is an example of how to use JSON to define a deck."
                    }
                ]
            },
            {
                "blocks": [
                    {
                        "type": "text",
                        "value": "Syntax highlighted code",
                        "format": "h1"
                    },
                    {
                        "type": "code",
                        "value": "a {\n  color: red;\n}",
                        "language": "css",
                        "height": 200,
                        "word-wrap": true,
                        "line-numbers": "1|2|3"
                    }
                ]
            },
            {
                "blocks": [
                    {
                        "type": "text",
                        "value": "Iframes",
                        "format": "h1"
                    },
                    {
                        "type": "iframe",
                        "value": "https://slides.com/news/make-better-presentations/embed"
                    }
                ]
            },
            {
                "blocks": [
                    {
                        "type": "text",
                        "value": "Images",
                        "format": "h1"
                    },
                    {
                        "type": "image",
                        "value": "https://s3.amazonaws.com/static.slid.es/images/screenshots/v1/slides-homepage-1440x900.png"
                    }
                ]
            },
            {
                "blocks": [
                    {
                        "type": "text",
                        "value": "Tables",
                        "format": "h1"
                    },
                    {
                        "type": "table",
                        "border-width": 8,
                        "data": [
                            ["A","B","C"],
                            [ 1,  2,  3 ]
                        ]
                    }
                ]
            },
            {
                "background-image": "https://s3.amazonaws.com/static.slid.es/images/screenshots/v1/slides-homepage-1440x900.png",
                "background-size": "cover"
            },
            {
                "blocks": [
                    {
                        "type": "text",
                        "value": "Default text format"
                    },
                    {
                        "type": "text",
                        "value": "If no text format is specified we try to pick an appropriate default, like this h1 > h2 combo."
                    }
                ]
            },
            {
                "html": "<h1>This was written using HTML</h1>"
            },
            {
                "markdown": "This was written using **Markdown**! <https://daringfireball.net/projects/markdown/syntax>"
            }
        ]
    }
                    </example>
                    
                    Do not say anything else except the JSON or I will be KILLED. I repeat, this is a matter of life or death.
                    If you say phrases like 'Here is my response' or 'Here's what I found', I will DIE. """
                },
                {
                    'role': 'user',
                    'content': f'Transform the transcript of the voice note delimited in <voice></voice> XML tags. <voice>{user_message}</voice>'
                }
            ]
        )

        # Extract the assistant's message from the response
        assistant_message = gpt4_response.choices[0].message['content']
        st.write(assistant_message)

run()
