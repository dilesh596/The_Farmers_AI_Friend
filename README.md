# The Farmers AI Friend

An offline AI-powered agricultural advisory app for farmers in Vidarbha, Maharashtra. It helps farmers ask crop-related questions in English, Marathi, or Hindi and get locally relevant suggestions based on district, month, and historical agronomic data.

## Overview

The Farmers AI Friend is a Streamlit-based application that combines:

- local agricultural reference data from `advice.json`
- a local Ollama language model for natural-language responses
- offline speech recognition with `faster-whisper`
- bilingual / multilingual support for English, Marathi, and Hindi

The app is designed to give simple, practical crop and gardening guidance such as:

- which crops can be sown in a selected month
- what should be done during the current season
- timing for rice nursery and sowing activities
- general suggestions for crop planning, pests, and seasonal farming decisions

It is meant to be a helpful decision-support tool for small and marginal farmers, especially in Indian agricultural contexts where language accessibility matters.

## Why this project matters

Many farmers need timely advice but may not have access to reliable digital advisory systems in their native language. This project aims to bridge that gap by providing a farmer-friendly, local, and offline AI assistant that works without requiring internet-based cloud services.

## Features

- Farmers can ask questions in English, Marathi, or Hindi
- Automatic language detection for Romanized Marathi/Hindi inputs
- Local conversion to Devanagari script for Marathi and Hindi responses
- District and month-based crop recommendations
- Use of historical, reference-based agricultural data
- Offline local model support with Ollama
- Voice input support for spoken questions
- Simple chat-style user experience via Streamlit

## Tech Stack

- Python
- Streamlit
- Ollama
- faster-whisper
- JSON-based agricultural reference dataset

## Project Structure

```text
The_Farmers_AI_Friend/
├── qbot.py
├── advice.json
├── README.md
└── .gitignore (if present)
```

## How it works

1. The user selects a district and month.
2. The app loads local agronomic data from `advice.json`.
3. The user enters a question in English, Marathi, or Hindi.
4. The app detects the language and prepares context from the selected district/month.
5. A local Ollama model answers using the reference data and avoids guessing when information is unavailable.
6. The response is presented in the requested language with simple farming-friendly wording.

## Installation

Make sure Python 3.10+ is installed.

Install the required packages:

```bash
pip install streamlit ollama faster-whisper
```

Make sure Ollama is installed and running locally, then pull a model such as:

```bash
ollama pull gemma3:1b
```

## Run the app

```bash
streamlit run qbot.py
```

## Example questions

- What crops should I grow this month?
- Which crops can be sown in June?
- When should I sow paddy?
- क्या इस महीने मूंग बोनी चाहिए?
- या महिन्यात कोणती पिके घ्यावीत?

## Important note

The app uses historical local agricultural data and reference-based advice. It should be used as a helpful decision-support tool, but farmers should also consult local agriculture officers, extension services, and current field conditions before making major farming decisions.

## License

This project currently does not specify a license in the repository files. If you plan to publish it publicly for broader use, consider adding an appropriate open-source license.

## Future Improvements

- add a proper `requirements.txt`
- support more districts and crop datasets
- add a web dashboard for crop calendars and alerts
- improve multilingual handling and local language accuracy
- package the app for deployment in rural environments
