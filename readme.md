This is an AI-ASSISTANT for farmers like my dad and others who wants to use AI in the farms but they can't because in our farms network isn't a thing. You understand what I am saying right..... So, I build this AI agent that can work offline without any internet connection so that they can work more significantly in the farm and can produce more grains ever than before.

It can tell almost everything as long as it is about farming and in its reach like only from vidharbha area in Maharashtra. So I have used the ollema and gemma3:1b as a base of this project and take some help from ai assistants like claude and chatgpt as well. So that's it. See you next time.......

Run the Gradio demo
git clone https://github.com/dilesh596/The_Farmers_AI_Friend cd The_Farmers_AI_Friend pip install -r requirements.txt python app.py


How to run it

This app runs fully offline after the one-time downloads below. It needs Python 3.9 or newer.

1. Install Ollama and download the model

Install Ollama from https://ollama.com, then run:

bash
ollama pull gemma3:1b

Keep Ollama running in the background while you use the app.

2. Get the code
bash
git clone https://github.com/dilesh596/The_Farmers_AI_Friend.git
cd The_Farmers_AI_Friend
3. Install the dependencies
bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
4. Start the app
bash
streamlit run app.py

Your browser opens at http://localhost:8501.

Notes
advice.json must stay in the same folder as app.py.
Voice input downloads the speech model once, so do your first voice test while online. After that it works offline.
To use a different model, run ollama pull <model-name> and type that name in the "Ollama model" box in the sidebar.
The crop statistics are historical. Please consult your local agriculture officer for current advice.
