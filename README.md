# Farmers AI Friend

A multilingual, offline AI-powered agricultural assistant designed to help farmers get crop guidance in their preferred language.

## Overview

Farmers AI Friend is a Python-based application that provides crop and seasonal farming advice using local village/district data, language-aware responses, and an offline AI model. The app is tailored for Indian farmers, especially in Vidarbha, Maharashtra, where quick and understandable agricultural advice can be critical.

The system helps farmers ask questions in English, Marathi, or Hindi and receive guidance such as:

- which crops can be sown this month
- what crops are suitable for the selected district
- planting and sowing windows for major crops
- rice nursery and sowing timing guidance
- general seasonal farming recommendations

## Why this project matters

Many farmers need timely agricultural advice, but access to reliable digital assistance is often limited by language barriers, connectivity issues, and lack of localized recommendations. This project aims to bridge that gap by creating a simple, farmer-friendly AI tool that works locally without relying on external cloud services.

## Key Features

- Multilingual support: English, Marathi, and Hindi
- Local language detection for Romanized Marathi/Hindi input
- Automatic conversion to Devanagari script for Marathi/Hindi responses
- District-based and month-based recommendations
- Chat-style interface powered by Streamlit
- Offline AI support with Ollama
- Voice input support using local speech recognition
- Uses historical agricultural reference data to avoid fabricating uncertain advice

## Tech Stack

- Python
- Streamlit
- Ollama
- faster-whisper
- JSON-based agricultural reference dataset

## Project Structure

```text
The_Farmers_AI_Friend/
├── qbot.py              # Main Streamlit app and logic
├── advice.json          # Agricultural reference data by district and month
├── README.md            # Project documentation
└── requirements.txt     # Optional dependency file (to be added if needed)
```

## How it works

1. The user selects a district and month.
2. The app loads agronomic reference data from `advice.json`.
3. The farmer asks a question in English, Marathi, or Hindi.
4. The app detects the language and prepares context using the selected district and month.
5. A local Ollama model answers using only the available agricultural reference data.
6. The result is delivered in a simple, plain-language format suitable for farmers.

## Installation

### Prerequisites

- Python 3.10+
- Ollama installed and running locally
- Internet access for the first-time model download (if needed)

### Install dependencies

```bash
pip install streamlit ollama faster-whisper
```

### Pull a local model

```bash
ollama pull gemma3:1b
```

## Run the application

```bash
streamlit run qbot.py
```

## Example Questions

- What crops should I grow this month?
- Which crops can be sown in June?
- When should I sow paddy?
- क्या इस महीने मूंग बोनी चाहिए?
- या महिन्यात कोणती पिके घ्यावीत?
- aata kay perave?

## Example Use Cases

- A farmer asks which crop is suitable for the current month.
- A farmer wants to know the ideal time to sow a particular crop.
- A farmer asks in Hindi or Marathi using Roman letters and receives a Devanagari response.
- A farmer uses voice input to ask a crop question hands-free.

## Important Note

This app relies on historical and local agricultural reference data. It is designed as a decision-support tool, not a replacement for local agriculture officers, agronomists, or field conditions. Farmers should validate recommendations with local agricultural experts before making critical crop decisions.

## Future Improvements

- add a proper `requirements.txt`
- support more districts and crops
- improve multilingual accuracy for agricultural terminology
- add better farmer-friendly UI improvements
- include weather and soil data integration
- add offline dashboards for crop calendars and seasonal alerts

## License

This project does not currently include a license file in the repository. If you plan to share it publicly or collaborate with others, adding an open-source license is recommended.

## Project Description

Farmers AI Friend is an offline AI-powered farming assistant that helps farmers get crop recommendations in English, Marathi, and Hindi using district-based agricultural data, local language support, and voice-enabled interaction.
