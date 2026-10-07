"""Offline Vidarbha Crop & Garden Advisor  (chat version)
Streamlit + Ollama (local Gemma) + faster-whisper (local voice input)
Languages: English, Marathi, Hindi

Run:  streamlit run qbot.py
"""
import hashlib
import io
import json
import re
from pathlib import Path

import streamlit as st

try:
    import ollama
except ImportError:
    ollama = None

DATA_FILE = Path(__file__).parent / "advice.json"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_RE = re.compile("|".join(MONTHS), re.IGNORECASE)
HISTORY_TURNS = 6  # how many previous messages the model sees for follow-ups

LANG_NAMES = {"en": "English", "mr": "Marathi", "hi": "Hindi"}
REPLY_CHOICES = {
    "Auto (match my question)": None,
    "English": "en",
    "मराठी (Marathi)": "mr",
    "हिन्दी (Hindi)": "hi",
}
DEFAULT_QUESTIONS = {
    "en": "What crops should I grow and what should I do this month?",
    "mr": "या महिन्यात कोणती पिके घ्यावीत आणि मी काय करावे?",
    "hi": "इस महीने कौन सी फसलें उगानी चाहिए और मुझे क्या करना चाहिए?",
}

SYSTEM_PROMPT = (
    "You are a friendly farming and gardening advisor for the Vidarbha region "
    "of Maharashtra, India. Answer ONLY using the reference data provided with "
    "the latest question. The farmer may type Marathi or Hindi in English "
    "letters (for example 'aata kay perave' or 'abhi kya boyen'); understand "
    "it as Marathi or Hindi. If a Romanized Marathi or Hindi question has been "
    "converted to Devanagari, treat that converted text as the question and reply "
    "in the same language using Devanagari script. Do not answer in Romanized "
    "Marathi or Hindi. For questions asking when a crop should be planted, use "
    "the matching crop's sowing window from the reference data, not just the "
    "selected month's general sowing list. Rice nursery sowing and transplanting "
    "are different activities: never describe a nursery-sowing window as the "
    "transplanting date. If the reference has nursery dates but no transplanting "
    "date, explain that distinction and say the transplanting date is not listed. "
    "If the data does not cover something, say so plainly instead of "
    "guessing. For general 'what to grow' questions, start with what can be sown "
    "in the selected month (sowing_this_month), then next month "
    "(sowing_next_month). For specific follow-up questions, answer just that "
    "question briefly. Use familiar everyday crop names from the crop-name guide "
    "provided with the question; do not repeat technical English crop labels when "
    "a common local name is listed. Keep answers simple and use short sections. "
    "Mention once in a while that "
    "the statistics are historical and local agriculture officers should be "
    "consulted for current advice."
)

CROP_NAME_GUIDE = {
    "en": {
        "aonla": "Indian gooseberry",
        "banana": "banana",
        "ber": "jujube",
        "blackgram": "black gram",
        "brinjal": "eggplant",
        "chickpea": "chickpea",
        "cotton": "cotton",
        "custard apple": "custard apple",
        "gram": "chickpea",
        "greengram": "green gram",
        "greengram_blackgram": "green gram and black gram",
        "groundnut": "peanut",
        "guava": "guava",
        "jowar": "sorghum",
        "kharif_jowar": "sorghum",
        "kharif_sorghum": "sorghum",
        "kagzi lime": "lime",
        "lemon": "lemon",
        "linseed": "flaxseed",
        "maize": "corn",
        "mango": "mango",
        "moong": "green gram",
        "mosambi": "sweet lime",
        "onion": "onion",
        "orange": "orange",
        "paddy": "rice",
        "paddy_nursery": "rice seedlings",
        "papaya": "papaya",
        "pigeonpea": "pigeon pea",
        "pomegranate": "pomegranate",
        "rabi_jowar": "sorghum",
        "rabi_sorghum": "sorghum",
        "safflower": "safflower",
        "sapota": "sapodilla",
        "sesame": "sesame",
        "sesamum": "sesame",
        "sorghum": "sorghum",
        "soybean": "soybean",
        "sugarcane": "sugarcane",
        "sunflower": "sunflower",
        "tamarind": "tamarind",
        "urd": "black gram",
        "urdbean": "black gram",
        "wheat": "wheat",
    },
    "mr": {
        "aonla": "आवळा",
        "banana": "केळी",
        "ber": "बोर",
        "blackgram": "उडीद",
        "brinjal": "वांगी",
        "chickpea": "हरभरा",
        "cotton": "कापूस",
        "custard apple": "सीताफळ",
        "gram": "हरभरा",
        "greengram": "मूग",
        "greengram_blackgram": "मूग आणि उडीद",
        "groundnut": "भुईमूग",
        "guava": "पेरू",
        "jowar": "ज्वारी",
        "kharif_jowar": "ज्वारी",
        "kharif_sorghum": "ज्वारी",
        "kagzi lime": "लिंबू",
        "lemon": "लिंबू",
        "linseed": "जवस",
        "maize": "मका",
        "mango": "आंबा",
        "moong": "मूग",
        "mosambi": "मोसंबी",
        "onion": "कांदा",
        "orange": "संत्रे",
        "paddy": "भात (तांदूळ)",
        "paddy_nursery": "भाताची रोपे",
        "papaya": "पपई",
        "pigeonpea": "तूर",
        "pomegranate": "डाळिंब",
        "rabi_jowar": "ज्वारी",
        "rabi_sorghum": "ज्वारी",
        "safflower": "करडई",
        "sapota": "चिकू",
        "sesame": "तीळ",
        "sesamum": "तीळ",
        "sorghum": "ज्वारी",
        "soybean": "सोयाबीन",
        "sugarcane": "ऊस",
        "sunflower": "सूर्यफूल",
        "tamarind": "चिंच",
        "urd": "उडीद",
        "urdbean": "उडीद",
        "wheat": "गहू",
    },
    "hi": {
        "aonla": "आंवला",
        "banana": "केला",
        "ber": "बेर",
        "blackgram": "उड़द",
        "brinjal": "बैंगन",
        "chickpea": "चना",
        "cotton": "कपास",
        "custard apple": "सीताफल",
        "gram": "चना",
        "greengram": "मूंग",
        "greengram_blackgram": "मूंग और उड़द",
        "groundnut": "मूंगफली",
        "guava": "अमरूद",
        "jowar": "ज्वार",
        "kharif_jowar": "ज्वार",
        "kharif_sorghum": "ज्वार",
        "kagzi lime": "नींबू",
        "lemon": "नींबू",
        "linseed": "अलसी",
        "maize": "मक्का",
        "mango": "आम",
        "moong": "मूंग",
        "mosambi": "मौसंबी",
        "onion": "प्याज",
        "orange": "संतरा",
        "paddy": "धान (चावल)",
        "paddy_nursery": "धान की पौध",
        "papaya": "पपीता",
        "pigeonpea": "अरहर",
        "pomegranate": "अनार",
        "rabi_jowar": "ज्वार",
        "rabi_sorghum": "ज्वार",
        "safflower": "कुसुम",
        "sapota": "चीकू",
        "sesame": "तिल",
        "sesamum": "तिल",
        "sorghum": "ज्वार",
        "soybean": "सोयाबीन",
        "sugarcane": "गन्ना",
        "sunflower": "सूरजमुखी",
        "tamarind": "इमली",
        "urd": "उड़द",
        "urdbean": "उड़द",
        "wheat": "गेहूँ",
    },
}


# ---------------- data helpers ----------------
@st.cache_data
def load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def list_districts(data):
    return sorted(d["district"] for d in data["districts"])


def months_in_window(text):
    """'20 June - 15 July' -> {5, 6}; '1st week of July' -> {6}. (0-based)"""
    found = [MONTHS.index(m.group(0).capitalize()) for m in MONTH_RE.finditer(text)]
    if not found:
        return set()
    if len(found) == 1:
        return {found[0]}
    start, end = found[0], found[1]
    out, i = {start}, start
    while i != end:
        i = (i + 1) % 12
        out.add(i)
    return out


def sowing_in_month(record, month_idx):
    hits = []
    for group, crops in (record.get("sowing_windows") or {}).items():
        for crop, window in (crops or {}).items():
            if month_idx in months_in_window(str(window)):
                hits.append({"crop": crop.replace("_", " "),
                             "type": group.replace("_", " "),
                             "window": window})
    return hits


def build_context(data, district, month):
    record = next(d for d in data["districts"] if d["district"] == district)
    m = MONTHS.index(month)
    context = {k: v for k, v in record.items() if k != "source_url"}
    context["selected_month"] = month
    context["sowing_this_month"] = sowing_in_month(record, m) or "No listed sowing window in this month"
    context["sowing_next_month"] = sowing_in_month(record, (m + 1) % 12) or "No listed sowing window next month"
    context["rice_timing_windows"] = [
        {
            "activity": (
                "rice nursery sowing (not transplanting)"
                if crop == "paddy_nursery" else "rice sowing"
            ),
            "season": season.replace("_", " "),
            "window": window,
        }
        for season, crops in (record.get("sowing_windows") or {}).items()
        for crop, window in (crops or {}).items()
        if crop in {"paddy", "paddy_nursery"}
    ]
    context["data_warning"] = data["meta"].get("data_vintage_warning")
    return context


# ---------------- language + voice ----------------
def language_instruction(target):
    if target:
        name = LANG_NAMES[target]
        script = " Use Devanagari script." if target in ("mr", "hi") else ""
        return (f"Write your ENTIRE answer in {name}.{script} "
                "Do not write Marathi or Hindi using English letters. "
                "Keep numbers and dates as they are.")
    return ("Write your ENTIRE answer in the same language and script as the "
            "farmer's question: Marathi question -> Marathi in Devanagari, "
            "Hindi question -> Hindi in Devanagari, English question -> English.")


@st.cache_resource(show_spinner="Loading local speech model...")
def load_whisper(size):
    from faster_whisper import WhisperModel
    return WhisperModel(size, device="cpu", compute_type="int8")


def transcribe(audio_bytes, size, lang_code):
    model = load_whisper(size)
    segments, info = model.transcribe(
        io.BytesIO(audio_bytes), language=lang_code, beam_size=5, vad_filter=True
    )
    text = " ".join(s.text.strip() for s in segments).strip()
    return text, info.language


DEVANAGARI = re.compile(r"[\u0900-\u097F]")
# Words that are clearly Marathi / Hindi when typed in English letters.
# (Words shared by both languages are left out on purpose.)
MR_ROMAN = {"aahe", "ahe", "aahet", "kay", "kasa", "kase", "kashi", "mala",
            "pahije", "hava", "perave", "perni", "aani", "ani", "kiti",
            "kuthe", "kadhi", "kevha", "aata", "ata", "amhi", "tumhi", "majha",
            "majhya", "shet", "pik", "paus", "nako", "karave", "sanga", "sang",
            "mhanje", "konta", "konti", "sheti", "jamin", "kapus", "soyabin",
            "harbhara", "tur", "lagwad", "lavave", "udya", "ya", "mahinyat",
            "mahinyamadhe", "mahina", "pike", "ghyavi", "ghyavit", "ghavavit",
            "mi", "karawa", "karayla", "karu", "bhat", "lagvad", "lagavd",
            "lavani", "karavi", "karaychi", "rop", "ropanchi", "lavaychi",
            "lavavi", "paddy"}
HI_ROMAN = {"hai", "hain", "kya", "kaise", "kaisa", "kaun", "kab", "kahan",
            "kitna", "kitni", "mujhe", "chahiye", "boye", "boyen", "bona",
            "aur", "mein", "abhi", "kal", "fasal", "khet", "kheti", "baarish",
            "barish", "nahin", "kripya", "batao", "bataiye", "karna", "kisan",
            "zameen", "gehu", "chana", "dhan", "sarson", "kapas", "kare",
            "iss", "mahine", "kaunsi", "kaunse", "faslen", "fasale",
            "ugani", "karoon", "karun"}
MR_DEV = {"आहे", "आहेत", "काय", "आणि", "मला", "पाहिजे", "कसे", "कसा", "कशी",
          "कुठे", "केव्हा", "कधी", "आता", "आम्ही", "माझ्या", "माझा", "पेरावे",
          "नको", "शेती", "पाऊस", "या", "महिन्यात", "कोणती", "पिके", "घ्यावीत",
          "मी", "करावे"}
HI_DEV = {"है", "हैं", "क्या", "और", "मुझे", "चाहिए", "कैसे", "कब", "कहाँ",
          "अभी", "में", "नहीं", "बोएं", "बारिश", "कृपया", "इस", "महीने",
          "कौन", "कौनसी", "फसल", "फसलें", "उगानी", "करना", "करूं", "करूँ"}


def detect_language(text):
    """Returns (lang_code, typed_in_english_letters)."""
    tokens = re.findall(r"[\w\u0900-\u097F]+", text.lower())
    if DEVANAGARI.search(text):
        mr = sum(t in MR_DEV for t in tokens)
        hi = sum(t in HI_DEV for t in tokens)
        return ("hi" if hi > mr else "mr"), False
    mr = sum(t in MR_ROMAN for t in tokens)
    hi = sum(t in HI_ROMAN for t in tokens)
    if mr == 0 and hi == 0:
        return "en", False
    return ("hi" if hi > mr else "mr"), True


def to_devanagari(model, text, lang):
    """Turn Marathi/Hindi typed in English letters into Devanagari (local LLM)."""
    name = LANG_NAMES[lang]
    example = ""
    if lang == "mr":
        example = (
            " For example, 'bhat lagvad kadhi karavi' becomes "
            "'भात लागवड कधी करावी?'."
        )
    elif lang == "hi":
        example = (
            " For example, 'abhi kya boyen' becomes "
            "'अभी क्या बोएँ?'."
        )
    prompt = (
        f"The following is {name} written using English letters. Preserve its "
        f"meaning and rewrite it in {name} using Devanagari script. Do not "
        f"translate it into another language.{example} "
        f"Output only the rewritten question, nothing else.\n\n{text}"
    )
    r = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0, "num_predict": 120},
    )
    out = r["message"]["content"].strip().strip('"\'`')
    if not out or not DEVANAGARI.search(out):
        raise ValueError(f"The model did not return the question in {name} Devanagari.")
    return out


def stream_answer(model, context, question, target, history):
    """history = earlier chat messages [{'role','content'}, ...]"""
    crop_names = CROP_NAME_GUIDE.get(target, CROP_NAME_GUIDE["en"])
    user_msg = (
        f"Reference data:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        "For rice timing questions, use rice_timing_windows. If it says "
        "'rice nursery sowing (not transplanting)', report that only as the "
        "nursery seed-sowing period; do not call it the date for planting "
        "seedlings in the field. If no transplanting period is listed, say so "
        "clearly rather than inventing one.\n\n"
        "Use these simple, familiar crop names in your answer instead of the "
        "raw crop labels when they appear in the reference data:\n"
        f"{json.dumps(crop_names, ensure_ascii=False, indent=2)}\n\n"
        f"Farmer's question: {question}\n\n"
        f"{language_instruction(target)}"
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m["role"], "content": m["content"]}
                 for m in history[-HISTORY_TURNS:]]
    messages.append({"role": "user", "content": user_msg})
    for chunk in ollama.chat(model=model, messages=messages, stream=True):
        yield chunk["message"]["content"]


# ---------------- UI ----------------
st.set_page_config(page_title="Vidarbha Crop Advisor", page_icon="🌱")
st.title("🌱 Vidarbha Crop & Garden Advisor")
st.caption("Runs fully offline with local open-weight models. English • मराठी • हिन्दी")

if ollama is None:
    st.error("The `ollama` package is missing. Run: pip install -r requirements.txt")
    st.stop()
if not DATA_FILE.exists():
    st.error(f"Could not find {DATA_FILE.name} next to app.py.")
    st.stop()

data = load_data()
districts = list_districts(data)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- sidebar: settings, mic, quick actions ----
pending = None          # the question to answer in this run
pending_lang = None     # language detected from voice (if any)

with st.sidebar:
    st.header("Settings")
    district = st.selectbox(
        "District", districts,
        index=districts.index("Bhandara") if "Bhandara" in districts else 0,
    )
    month = st.selectbox("Month", MONTHS, index=MONTHS.index("October"))
    reply_label = st.radio("Reply language", list(REPLY_CHOICES))
    reply_code = REPLY_CHOICES[reply_label]

    st.divider()
    if hasattr(st, "audio_input"):
        audio = st.audio_input("🎤 Speak your question")
        if audio is not None:
            audio_bytes = audio.getvalue()
            h = hashlib.md5(audio_bytes).hexdigest()
            if st.session_state.get("audio_hash") != h:
                st.session_state.audio_hash = h
                try:
                    with st.spinner("Listening (offline)..."):
                        text, detected = transcribe(
                            audio_bytes, st.session_state.get("whisper_size", "small"),
                            reply_code,
                        )
                    if text:
                        pending = text
                        pending_lang = detected if detected in LANG_NAMES else None
                    else:
                        st.warning("Could not hear anything. Please try again.")
                except Exception as e:
                    st.error(
                        f"Voice recognition failed: {e}\n\n"
                        "The speech model must be downloaded once while online."
                    )
    else:
        st.warning("Voice input needs a newer Streamlit: pip install -U streamlit")

    if st.button("💡 Advice for this month", use_container_width=True):
        pending = DEFAULT_QUESTIONS[reply_code or "en"]
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    model = st.text_input("Ollama model", value="gemma3:1b")
    st.selectbox("Voice model", ["small", "base"], key="whisper_size")
    st.info(data["meta"].get("data_vintage_warning", ""))

# ---- chat history ----
if not st.session_state.messages:
    st.info("Ask anything about crops, sowing time, rain or pests. "
            "Type below or use the 🎤 in the sidebar.\n\n"
            "You can type in English letters too:\n\n"
            "*aata kay perave?* → आता काय पेरावे?\n\n"
            "*abhi kya boyen?* → अभी क्या बोएं?\n\n"
            "*When should I sow gram?* → English answer")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("converted"):
            st.caption(f"→ {msg['converted']}")
        if msg.get("context"):
            with st.expander(f"Data used ({msg['district']}, {msg['month']})"):
                st.json(msg["context"])

# ---- new question ----
typed = st.chat_input("Ask your question / प्रश्न विचारा / सवाल पूछें")
if typed:
    pending, pending_lang = typed, None

if pending:
    det_lang, is_roman = detect_language(pending)
    # explicit choice > language heard by the mic > language detected from text
    target = reply_code or pending_lang or det_lang
    context = build_context(data, district, month)

    with st.chat_message("user"):
        st.markdown(pending)
        converted = None
        if is_roman and not pending_lang:
            try:
                with st.spinner("Converting to Devanagari..."):
                    converted = to_devanagari(model, pending, det_lang)
            except Exception as e:
                st.error(
                    f"Could not convert your {LANG_NAMES[det_lang]} question "
                    f"to Devanagari: {e}\n\n"
                    f"Check that Ollama is running and `ollama pull {model}` is done."
                )
                st.stop()
            if converted:
                st.caption(f"→ {converted}")
    question_for_model = converted if converted else pending

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                stream_answer(model, context, question_for_model, target,
                              st.session_state.messages)
            )
            with st.expander(f"Data used ({district}, {month})"):
                st.json(context)
            st.session_state.messages.append(
                {"role": "user", "content": pending, "converted": converted})
            st.session_state.messages.append({
                "role": "assistant", "content": answer,
                "context": context, "district": district, "month": month,
            })
        except Exception as e:
            st.error(
                f"Could not reach the local model: {e}\n\n"
                f"Check that Ollama is running and `ollama pull {model}` is done."
            )