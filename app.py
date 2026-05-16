import streamlit as st
import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from io import BytesIO
import re
import time
import streamlit.components.v1 as components
import json

try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    mic_recorder = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Load environment variables
load_dotenv()

# Configure page - FAST & MINIMAL
st.set_page_config(
    page_title="English Learning Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Note: demo UI will be rendered as a self-contained HTML component below.

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "Groq"  # Default to fastest model
if 'response_time' not in st.session_state:
    st.session_state.response_time = 0
if 'last_audio_hash' not in st.session_state:
    st.session_state.last_audio_hash = None
if 'last_transcript' not in st.session_state:
    st.session_state.last_transcript = ""
if 'last_spoken_reply' not in st.session_state:
    st.session_state.last_spoken_reply = ""
if 'last_voice_audio' not in st.session_state:
    st.session_state.last_voice_audio = None
if 'learning_insights' not in st.session_state:
    st.session_state.learning_insights = ""
if 'show_detailed_feedback' not in st.session_state:
    st.session_state.show_detailed_feedback = False
if 'app_screen' not in st.session_state:
    st.session_state.app_screen = "Speak"
if 'learning_mode' not in st.session_state:
    st.session_state.learning_mode = "Conversation"  # Options: Conversation, Translation, Pronunciation, Grammar, Roleplay, Storytelling, Interview Prep, Sentence Versions, Emotional Learning
if 'current_roleplay' not in st.session_state:
    st.session_state.current_roleplay = "Restaurant"
if 'voice_speed' not in st.session_state:
    st.session_state.voice_speed = "Normal"
if 'urdu_support' not in st.session_state:
    st.session_state.urdu_support = True
if 'daily_reminder' not in st.session_state:
    st.session_state.daily_reminder = False
if 'storytelling_prompt' not in st.session_state:
    from language_utils import get_storytelling_prompt
    st.session_state.storytelling_prompt = get_storytelling_prompt()
if 'current_interview_q' not in st.session_state:
    from language_utils import get_interview_question
    st.session_state.current_interview_q = get_interview_question(0)

# Sidebar - Quick Configuration
with st.sidebar:
    st.markdown("## 🌿 Calm Coach")
    st.caption("Speak naturally. The app replies simply. Keys stay in your environment only.")

    groq_key = os.getenv("GROQ_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    st.caption("All advanced controls moved to the Settings screen.")

# Main hero
# If the user prefers the exact demo UI, render it via an isolated HTML component
demo_ui = st.session_state.get("use_demo_ui", True)
# Allow forcing the fully interactive native Streamlit UI when demo iframe isn't responsive
if st.session_state.get('force_native'):
    demo_ui = False
if demo_ui:
    # Show a small banner control so user can fall back to the native interactive UI
    col1, col2 = st.columns([1,4])
    with col1:
        if st.button('Use interactive UI (fix issues)'):
            st.session_state['force_native'] = True
            st.experimental_rerun()
    with col2:
        st.markdown('')
    # Allow injecting the full conversation history (reply + base64 audio) from Python into the demo iframe.
    # This ensures the demo UI maintains conversation across Streamlit reruns
    pending_from_py = st.session_state.get('pending_response')
    conversation_history = st.session_state.get('conversation', [])
    demo_html = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>English Learning Assistant</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
<style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
        --bg: #F5F7FF;
        --surface: #FFFFFF;
        --surface2: #EEF1FF;
        --primary: #4361EE;
        --primary-light: #EEF0FF;
        --primary-dark: #2C46C9;
        --accent-green: #22C55E;
        --accent-green-light: #DCFCE7;
        --accent-orange: #F97316;
        --accent-orange-light: #FFF0E6;
        --text: #0D0E1A;
        --text2: #5A5E7A;
        --text3: #9499B8;
        --border: rgba(67,97,238,0.12);
        --border2: rgba(67,97,238,0.2);
        --shadow: 0 4px 20px rgba(67,97,238,0.10);
        --shadow-sm: 0 2px 10px rgba(67,97,238,0.08);
        --radius: 20px;
        --radius-sm: 12px;
        --nav-h: 76px;
    }

    body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; display: flex; justify-content: center; align-items: flex-start; }

    .app { width: 100%; max-width: 420px; min-height: 100vh; background: var(--bg); position: relative; display: flex; flex-direction: column; overflow: hidden; }

    /* ── Screens ── */
    .screen { display: none; flex-direction: column; flex: 1; padding-bottom: calc(var(--nav-h) + 12px); overflow-y: auto; min-height: calc(100vh - var(--nav-h)); animation: fadeIn 0.25s ease; }
    .screen.active { display: flex; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* ── Header ── */
    .header { padding: 52px 24px 20px; display: flex; align-items: center; justify-content: space-between; }
    .header-title { font-family: 'DM Serif Display', serif; font-size: 24px; color: var(--text); letter-spacing: -0.3px; }
    .header-title span { color: var(--primary); }
    .header-badge { background: var(--primary-light); color: var(--primary); font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: 100px; }

    /* ── SPEAK SCREEN ── */
    .speak-greeting { padding: 0 24px 24px; }
    .speak-greeting p { font-size: 15px; color: var(--text2); line-height: 1.5; }

    .ai-message-area { flex: 1; padding: 0 24px; display: flex; flex-direction: column; gap: 12px; min-height: 180px; }

    .bubble-row { display: flex; gap: 10px; align-items: flex-end; animation: bubbleIn 0.3s cubic-bezier(0.34,1.56,0.64,1); }
    @keyframes bubbleIn { from { opacity: 0; transform: scale(0.88) translateY(8px); } to { opacity: 1; transform: scale(1) translateY(0); } }

    .bubble-row.user { flex-direction: row-reverse; }

    .avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--primary); display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 14px; }
    .avatar.user-av { background: var(--surface2); }

    .bubble { max-width: 76%; padding: 14px 16px; border-radius: 18px; font-size: 15px; line-height: 1.5; color: var(--text); position: relative; }
    .bubble.ai { background: var(--surface); border-bottom-left-radius: 4px; box-shadow: var(--shadow-sm); }
    .bubble.user { background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
    .bubble .tip-tag { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--accent-green); background: var(--accent-green-light); padding: 3px 8px; border-radius: 100px; margin-top: 8px; font-weight: 500; }
    .bubble .tip-text { font-size: 13px; color: var(--text2); margin-top: 4px; line-height: 1.4; }

    .typing-dots { display: flex; gap: 4px; padding: 14px 16px; background: var(--surface); border-radius: 18px; border-bottom-left-radius: 4px; width: fit-content; box-shadow: var(--shadow-sm); }
    .typing-dots span { width: 6px; height: 6px; background: var(--text3); border-radius: 50%; animation: dotBounce 1.2s infinite ease-in-out; }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes dotBounce { 0%,80%,100% { transform: translateY(0); opacity: 0.4; } 40% { transform: translateY(-5px); opacity: 1; } }

    /* ── Mic Zone ── */
    .mic-zone { padding: 28px 24px 20px; display: flex; flex-direction: column; align-items: center; gap: 16px; }

    .mic-ring { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; cursor: pointer; user-select: none; }
    .mic-ring, .mic-btn { z-index: 9999; pointer-events: auto; }
    .mic-ring::before, .mic-ring::after { content: ''; position: absolute; border-radius: 50%; border: 2px solid var(--primary); opacity: 0; transition: all 0.3s; }
    .mic-ring::before { width: 130%; height: 130%; }
    .mic-ring::after  { width: 160%; height: 160%; }

    .mic-ring.listening::before { opacity: 0.2; animation: pulse1 1.2s infinite ease-out; }
    .mic-ring.listening::after { opacity: 0.12; animation: pulse2 1.2s 0.3s infinite ease-out; }
    @keyframes pulse1 { 0%,100% { transform: scale(1); opacity: 0.2; } 50% { transform: scale(1.05); opacity: 0.35; } }
    @keyframes pulse2 { 0%,100% { transform: scale(1); opacity: 0.12; } 50% { transform: scale(1.08); opacity: 0.22; } }

    .mic-btn { width: 100%; height: 100%; border-radius: 50%; background: var(--primary); border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: transform 0.15s, background 0.2s; box-shadow: 0 8px 32px rgba(67,97,238,0.35); }
    .mic-btn:active { transform: scale(0.94); }
    .mic-btn.listening { background: #D72B3F; box-shadow: 0 8px 32px rgba(215,43,63,0.35); }
    .mic-btn svg { width: 36px; height: 36px; }

    .mic-label { font-size: 14px; color: var(--text2); text-align: center; font-weight: 400; letter-spacing: 0.1px; }
    .mic-label strong { color: var(--primary); font-weight: 500; }

    .secondary-actions { display: flex; gap: 10px; padding: 0 24px; margin-bottom: 8px; }
    .sec-btn { flex: 1; padding: 11px 8px; background: var(--surface); border: 1.5px solid var(--border); border-radius: var(--radius-sm); font-size: 13px; font-family: 'DM Sans', sans-serif; color: var(--text2); cursor: pointer; text-align: center; transition: all 0.15s; font-weight: 500; }
    .sec-btn:hover { border-color: var(--border2); background: var(--primary-light); color: var(--primary); }

    /* ── CHAT SCREEN ── */
    .chat-messages { flex: 1; padding: 0 24px 16px; display: flex; flex-direction: column; gap: 12px; overflow-y: auto; }
    .chat-input-row { padding: 12px 24px 16px; display: flex; gap: 10px; align-items: center; background: var(--bg); border-top: 1px solid var(--border); }
    .chat-input { flex: 1; padding: 12px 16px; border-radius: 100px; border: 1.5px solid var(--border); background: var(--surface); font-family: 'DM Sans', sans-serif; font-size: 14px; color: var(--text); outline: none; transition: border-color 0.2s; }
    .chat-input:focus { border-color: var(--primary); }
    .chat-input::placeholder { color: var(--text3); }
    .chat-mic-btn { width: 44px; height: 44px; border-radius: 50%; background: var(--primary); border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 14px rgba(67,97,238,0.3); transition: transform 0.15s; }
    .chat-mic-btn:active { transform: scale(0.92); }

    /* ── LEARN SCREEN ── */
    .learn-header { padding: 52px 24px 8px; }
    .learn-header p { font-size: 14px; color: var(--text2); margin-top: 4px; }
    .learn-section-label { padding: 20px 24px 10px; font-size: 12px; font-weight: 600; color: var(--text3); letter-spacing: 0.8px; text-transform: uppercase; }
    .learn-cards { padding: 0 24px; display: flex; flex-direction: column; gap: 12px; }
    .learn-card { background: var(--surface); border-radius: var(--radius); padding: 18px 20px; box-shadow: var(--shadow-sm); cursor: pointer; transition: all 0.2s; border: 1.5px solid transparent; }
    .learn-card:hover { border-color: var(--border2); }
    .learn-card.expanded { border-color: var(--primary); }
    .lc-header { display: flex; justify-content: space-between; align-items: center; }
    .lc-label { font-size: 11px; font-weight: 600; color: var(--text3); letter-spacing: 0.6px; text-transform: uppercase; }
    .lc-chevron { font-size: 18px; color: var(--text3); transition: transform 0.2s; }
    .learn-card.expanded .lc-chevron { transform: rotate(180deg); }
    .lc-user { font-size: 14px; color: var(--text2); margin-top: 8px; font-style: italic; }
    .lc-correct { font-size: 16px; font-weight: 500; color: var(--text); margin-top: 10px; padding: 12px 14px; background: var(--primary-light); border-radius: var(--radius-sm); color: var(--primary-dark); }
    .lc-tip { display: none; margin-top: 12px; padding: 12px 14px; background: var(--accent-orange-light); border-radius: var(--radius-sm); font-size: 13px; color: var(--accent-orange); line-height: 1.5; }
    .learn-card.expanded .lc-tip { display: block; }
    .lc-tip-icon { font-size: 14px; margin-right: 4px; }

    /* ── PROGRESS SCREEN ── */
    .progress-header { padding: 52px 24px 20px; }
    .progress-header p { font-size: 14px; color: var(--text2); margin-top: 4px; }
    .stats-grid { padding: 0 24px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .stat-card { background: var(--surface); border-radius: var(--radius); padding: 20px 18px; box-shadow: var(--shadow-sm); }
    .stat-icon { font-size: 22px; margin-bottom: 10px; }
    .stat-val { font-size: 28px; font-weight: 600; color: var(--text); letter-spacing: -1px; }
    .stat-label { font-size: 12px; color: var(--text2); margin-top: 2px; font-weight: 400; }

    .progress-section { padding: 20px 24px 0; }
    .progress-section-title { font-size: 14px; font-weight: 500; color: var(--text); margin-bottom: 12px; }
    .word-chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .word-chip { padding: 6px 14px; background: var(--primary-light); color: var(--primary); border-radius: 100px; font-size: 13px; font-weight: 500; }

    .streak-banner { margin: 20px 24px 0; background: linear-gradient(135deg, var(--primary) 0%, #7B5CF6 100%); border-radius: var(--radius); padding: 20px 22px; display: flex; align-items: center; gap: 16px; color: #fff; }
    .streak-num { font-size: 42px; font-weight: 700; line-height: 1; }
    .streak-info p:first-child { font-size: 14px; font-weight: 500; opacity: 0.9; }
    .streak-info p:last-child { font-size: 12px; opacity: 0.65; margin-top: 2px; }

    /* ── SETTINGS SCREEN ── */
    .settings-header { padding: 52px 24px 20px; }
    .settings-section { padding: 0 24px 20px; }
    .settings-section-label { font-size: 11px; font-weight: 600; color: var(--text3); letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 10px; }
    .settings-card { background: var(--surface); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-sm); }
    .settings-row { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border); gap: 12px; }
    .settings-row:last-child { border-bottom: none; }
    .settings-row-info p:first-child { font-size: 15px; color: var(--text); font-weight: 400; }
    .settings-row-info p:last-child { font-size: 12px; color: var(--text3); margin-top: 2px; }
    .toggle { width: 46px; height: 26px; background: var(--border2); border-radius: 100px; position: relative; cursor: pointer; transition: background 0.2s; flex-shrink: 0; border: none; }
    .toggle.on { background: var(--primary); }
    .toggle::after { content: ''; position: absolute; width: 20px; height: 20px; border-radius: 50%; background: #fff; top: 3px; left: 3px; transition: transform 0.2s; box-shadow: 0 1px 4px rgba(0,0,0,0.15); }
    .toggle.on::after { transform: translateX(20px); }

    .level-selector { display: flex; gap: 8px; }
    .level-opt { flex: 1; padding: 10px 8px; border-radius: var(--radius-sm); border: 1.5px solid var(--border); background: transparent; font-family: 'DM Sans', sans-serif; font-size: 13px; color: var(--text2); cursor: pointer; text-align: center; transition: all 0.15s; font-weight: 500; }
    .level-opt.selected { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }

    .speed-slider-row { padding: 16px 20px; }
    .speed-slider-row label { font-size: 15px; color: var(--text); display: block; margin-bottom: 12px; }
    .speed-slider-row input[type="range"] { width: 100%; accent-color: var(--primary); cursor: pointer; }
    .speed-ticks { display: flex; justify-content: space-between; font-size: 11px; color: var(--text3); margin-top: 4px; }

    /* ── Bottom Nav ── */
    .bottom-nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 420px; height: var(--nav-h); background: var(--surface); border-top: 1px solid var(--border); display: flex; align-items: flex-start; padding-top: 10px; z-index: 100; backdrop-filter: blur(10px); }
    .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 4px 0; transition: all 0.15s; border: none; background: transparent; font-family: 'DM Sans', sans-serif; }
    .nav-icon { width: 40px; height: 32px; border-radius: 100px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
    .nav-item.active .nav-icon { background: var(--primary-light); }
    .nav-icon svg { width: 20px; height: 20px; stroke: var(--text3); transition: stroke 0.2s; }
    .nav-item.active .nav-icon svg { stroke: var(--primary); }
    .nav-label { font-size: 11px; color: var(--text3); font-weight: 400; transition: color 0.2s; }
    .nav-item.active .nav-label { color: var(--primary); font-weight: 500; }

    /* Language selector pills */
    .lang-pills { display: flex; gap: 8px; padding: 0 24px 20px; }
    .lang-pill { padding: 7px 16px; border-radius: 100px; border: 1.5px solid var(--border); font-size: 13px; font-family: 'DM Sans', sans-serif; color: var(--text2); cursor: pointer; transition: all 0.15s; background: var(--surface); font-weight: 500; }
    .lang-pill.selected { background: var(--primary-light); border-color: var(--primary); color: var(--primary); }

    /* State label */
    .state-label { text-align: center; font-size: 13px; font-weight: 500; color: var(--text3); min-height: 18px; letter-spacing: 0.2px; }
    .state-label.listening { color: #D72B3F; }
    .state-label.thinking { color: var(--primary); }

    /* Waveform */
    .waveform { display: flex; align-items: center; justify-content: center; gap: 4px; height: 32px; opacity: 0; transition: opacity 0.3s; }
    .waveform.active { opacity: 1; }
    .waveform span { width: 3px; background: #D72B3F; border-radius: 100px; animation: wave 0.8s ease-in-out infinite; height: 8px; }
    .waveform span:nth-child(1) { animation-delay: 0s; }
    .waveform span:nth-child(2) { animation-delay: 0.1s; height: 16px; }
    .waveform span:nth-child(3) { animation-delay: 0.2s; height: 24px; }
    .waveform span:nth-child(4) { animation-delay: 0.15s; height: 20px; }
    .waveform span:nth-child(5) { animation-delay: 0.05s; height: 14px; }
    .waveform span:nth-child(6) { animation-delay: 0.25s; height: 8px; }
    @keyframes wave { 0%,100% { transform: scaleY(0.6); } 50% { transform: scaleY(1.4); } }

    /* Header DM serif */
    .screen-title { font-family: 'DM Serif Display', serif; font-size: 24px; color: var(--text); letter-spacing: -0.3px; }
</style>
</head>
<body>
<div class="app">

    <!-- ══ SPEAK SCREEN ══ -->
    <div class="screen active" id="screen-speak">
        <div class="header">
            <div class="header-title">Speak<span>AI</span></div>
            <div class="header-badge">🇵🇰 Urdu + English</div>
        </div>
        <div class="speak-greeting">
            <p>Speak naturally — in English, Urdu, or mix both. I'll reply and help you improve.</p>
        </div>

        <div class="lang-pills">
            <button class="lang-pill selected" onclick="selectLang(this,'Conversation')">Conversation</button>
            <button class="lang-pill" onclick="selectLang(this,'Interview')">Interview</button>
            <button class="lang-pill" onclick="selectLang(this,'Story')">Storytelling</button>
        </div>

        <div class="ai-message-area" id="ai-area">
            <div class="bubble-row">
                <div class="avatar">🤖</div>
                <div class="bubble ai">
                    Assalamu alaikum! I'm your English coach. Speak naturally — in English, Urdu, or both. I'm here to help you improve without pressure.
                    <div class="tip-tag">💡 Tip</div>
                    <div class="tip-text">Start with: "Tell me about yourself"</div>
                </div>
            </div>
        </div>

        <div class="mic-zone">
            <div class="waveform" id="waveform">
                <span></span><span></span><span></span><span></span><span></span><span></span>
            </div>
            <p class="state-label" id="state-label">Tap the mic to start speaking</p>
            <div class="mic-ring" id="mic-ring">
                <button class="mic-btn" id="mic-btn" onclick="toggleMic()" aria-label="Toggle microphone">
                    <svg id="mic-icon" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z"/>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                        <line x1="12" y1="19" x2="12" y2="22"/>
                    </svg>
                </button>
            </div>
        </div>

        <div class="secondary-actions">
            <button class="sec-btn" onclick="clearChat()">Clear chat</button>
            <button class="sec-btn" onclick="switchTo('screen-chat')">Type instead</button>
        </div>
    </div>

    <!-- ══ CHAT SCREEN ══ -->
    <div class="screen" id="screen-chat">
        <div class="header">
            <div class="screen-title">Chat</div>
            <div class="header-badge">Active</div>
        </div>

        <div class="chat-messages" id="chat-area">
            <div class="bubble-row">
                <div class="avatar">🤖</div>
                <div class="bubble ai">Hello! Type anything — English, Urdu, or mixed. I'll always reply in simple English and give you one helpful tip.</div>
            </div>
            <div class="bubble-row user">
                <div class="avatar user-av">👤</div>
                <div class="bubble user">Main kal school nahi gaya tha.</div>
            </div>
            <div class="bubble-row">
                <div class="avatar">🤖</div>
                <div class="bubble ai">
                    I didn't go to school yesterday.
                    <div class="tip-tag">💡 Grammar tip</div>
                    <div class="tip-text">Use "didn't" + base verb for past negatives. "Nahi gaya" = "didn't go"</div>
                </div>
            </div>
        </div>

        <div class="chat-input-row">
            <input class="chat-input" id="chat-input" type="text" placeholder="Type in English or Urdu…" onkeydown="handleChatKey(event)">
            <button class="chat-mic-btn" onclick="switchTo('screen-speak')" aria-label="Voice mode">
                <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
                    <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="22"/>
                </svg>
            </button>
        </div>
    </div>

    <!-- ══ LEARN SCREEN ══ -->
    <div class="screen" id="screen-learn">
        <div class="learn-header">
            <div class="screen-title">Learning Cards</div>
            <p>Tap any card to see the correction and tip.</p>
        </div>

        <div class="learn-section-label">Today's corrections</div>
        <div class="learn-cards">

            <div class="learn-card" onclick="toggleCard(this)">
                <div class="lc-header">
                    <div class="lc-label">Past Tense</div>
                    <div class="lc-chevron">⌄</div>
                </div>
                <div class="lc-user">"He go yesterday school."</div>
                <div class="lc-correct">✓ He went to school yesterday.</div>
                <div class="lc-tip"><span class="lc-tip-icon">💡</span> Use past tense "went" for completed actions. Word order: Subject → Verb → Object → Time.</div>
            </div>

            <div class="learn-card" onclick="toggleCard(this)">
                <div class="lc-header">
                    <div class="lc-label">Articles</div>
                    <div class="lc-chevron">⌄</div>
                </div>
                <div class="lc-user">"I want eat apple."</div>
                <div class="lc-correct">✓ I want to eat an apple.</div>
                <div class="lc-tip"><span class="lc-tip-icon">💡</span> "An" goes before vowel sounds (a, e, i, o, u). "Want to eat" — always use "to" after "want".</div>
            </div>

            <div class="learn-card" onclick="toggleCard(this)">
                <div class="lc-header">
                    <div class="lc-label">Prepositions</div>
                    <div class="lc-chevron">⌄</div>
                </div>
                <div class="lc-user">"I am living in Pakistan since 5 years."</div>
                <div class="lc-correct">✓ I have been living in Pakistan for 5 years.</div>
                <div class="lc-tip"><span class="lc-tip-icon">💡</span> Use "for" with durations (5 years, 2 months). Use "since" with start points (since 2019).</div>
            </div>

            <div class="learn-card" onclick="toggleCard(this)">
                <div class="lc-header">
                    <div class="lc-label">Vocabulary</div>
                    <div class="lc-chevron">⌄</div>
                </div>
                <div class="lc-user">"This movie was very much good."</div>
                <div class="lc-correct">✓ This movie was really good.</div>
                <div class="lc-tip"><span class="lc-tip-icon">💡</span> Use "really" or "very" — not "very much" before adjectives. "Very much" works with verbs: "I liked it very much."</div>
            </div>

        </div>

        <div style="height: 16px;"></div>
    </div>

    <!-- ══ PROGRESS SCREEN ══ -->
    <div class="screen" id="screen-progress">
        <div class="progress-header">
            <div class="screen-title">Your Progress</div>
            <p>Keep going — every conversation counts.</p>
        </div>

        <div class="streak-banner">
            <div class="streak-num">🔥 7</div>
            <div class="streak-info">
                <p>Day streak!</p>
                <p>You're on fire. Don't break the chain.</p>
            </div>
        </div>

        <div class="stats-grid" style="margin-top: 16px;">
            <div class="stat-card">
                <div class="stat-icon">⏱</div>
                <div class="stat-val">48</div>
                <div class="stat-label">Minutes spoken</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📘</div>
                <div class="stat-val">34</div>
                <div class="stat-label">Words learned</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💬</div>
                <div class="stat-val">12</div>
                <div class="stat-label">Conversations</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-val">89%</div>
                <div class="stat-label">Accuracy today</div>
            </div>
        </div>

        <div class="progress-section">
            <div class="progress-section-title">Words you've learned</div>
            <div class="word-chips">
                <div class="word-chip">therefore</div>
                <div class="word-chip">although</div>
                <div class="word-chip">manage</div>
                <div class="word-chip">probably</div>
                <div class="word-chip">definitely</div>
                <div class="word-chip">recently</div>
                <div class="word-chip">achieve</div>
                <div class="word-chip">improve</div>
            </div>
        </div>

        <div class="progress-section" style="padding-top: 20px;">
            <div class="progress-section-title">Common mistakes to fix</div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="background: var(--surface); border-radius: var(--radius-sm); padding: 14px 16px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 14px; color: var(--text); font-weight: 500;">Past tense errors</div>
                        <div style="font-size: 12px; color: var(--text3); margin-top: 2px;">go → went, come → came</div>
                    </div>
                    <div style="font-size: 11px; background: var(--accent-orange-light); color: var(--accent-orange); padding: 4px 10px; border-radius: 100px; font-weight: 600;">5 times</div>
                </div>
                <div style="background: var(--surface); border-radius: var(--radius-sm); padding: 14px 16px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 14px; color: var(--text); font-weight: 500;">Article usage</div>
                        <div style="font-size: 12px; color: var(--text3); margin-top: 2px;">a / an / the</div>
                    </div>
                    <div style="font-size: 11px; background: var(--accent-orange-light); color: var(--accent-orange); padding: 4px 10px; border-radius: 100px; font-weight: 600;">3 times</div>
                </div>
            </div>
        </div>
        <div style="height: 16px;"></div>
    </div>

    <!-- ══ SETTINGS SCREEN ══ -->
    <div class="screen" id="screen-settings">
        <div class="settings-header">
            <div class="screen-title">Settings</div>
        </div>

        <div class="settings-section">
            <div class="settings-section-label">Language</div>
            <div class="settings-card">
                <div class="settings-row">
                    <div class="settings-row-info">
                        <p>Urdu support</p>
                        <p>Mix Urdu & English freely</p>
                    </div>
                    <button class="toggle on" onclick="this.classList.toggle('on')" aria-label="Toggle Urdu support"></button>
                </div>
                <div class="settings-row">
                    <div class="settings-row-info">
                        <p>Roman Urdu</p>
                        <p>Allow Urdu written in English letters</p>
                    </div>
                    <button class="toggle on" onclick="this.classList.toggle('on')" aria-label="Toggle Roman Urdu"></button>
                </div>
            </div>
        </div>

        <div class="settings-section">
            <div class="settings-section-label">Voice</div>
            <div class="settings-card">
                <div class="speed-slider-row">
                    <label>AI voice speed</label>
                    <input type="range" min="1" max="3" value="2" step="1">
                    <div class="speed-ticks"><span>Slow</span><span>Normal</span><span>Fast</span></div>
                </div>
            </div>
        </div>

        <div class="settings-section">
            <div class="settings-section-label">Learning level</div>
            <div class="level-selector">
                <button class="level-opt selected" onclick="selectLevel(this)">Beginner</button>
                <button class="level-opt" onclick="selectLevel(this)">Intermediate</button>
                <button class="level-opt" onclick="selectLevel(this)">Advanced</button>
            </div>
        </div>

        <div class="settings-section">
            <div class="settings-section-label">Notifications</div>
            <div class="settings-card">
                <div class="settings-row">
                    <div class="settings-row-info">
                        <p>Daily reminder</p>
                        <p>Remind me to practice every day</p>
                    </div>
                    <button class="toggle on" onclick="this.classList.toggle('on')" aria-label="Toggle daily reminder"></button>
                </div>
                <div class="settings-row">
                    <div class="settings-row-info">
                        <p>Streak alerts</p>
                        <p>Don't let me break my streak</p>
                    </div>
                    <button class="toggle" onclick="this.classList.toggle('on')" aria-label="Toggle streak alerts"></button>
                </div>
            </div>
        </div>

        <div style="height: 16px;"></div>
    </div>

    <!-- ══ Bottom Navigation ══ -->
    <nav class="bottom-nav">
        <button class="nav-item active" onclick="switchTo('screen-speak', this)" aria-label="Speak">
            <div class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="22"/>
                </svg>
            </div>
            <span class="nav-label">Speak</span>
        </button>
        <button class="nav-item" onclick="switchTo('screen-chat', this)" aria-label="Chat">
            <div class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
            </div>
            <span class="nav-label">Chat</span>
        </button>
        <button class="nav-item" onclick="switchTo('screen-learn', this)" aria-label="Learn">
            <div class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
            </div>
            <span class="nav-label">Learn</span>
        </button>
        <button class="nav-item" onclick="switchTo('screen-progress', this)" aria-label="Progress">
            <div class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10"/>
                    <line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
            </div>
            <span class="nav-label">Progress</span>
        </button>
        <button class="nav-item" onclick="switchTo('screen-settings', this)" aria-label="Settings">
            <div class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
            </div>
            <span class="nav-label">Settings</span>
        </button>
    </nav>

</div>

<script>
let micActive = false;
let micTimer = null;
const PENDING_FROM_PY = __PENDING_RESPONSE__;
const CONVERSATION_HISTORY = __CONVERSATION_HISTORY__;

function renderConversationHistory(history) {
    if (!history || !Array.isArray(history)) return;
    const area = document.getElementById('ai-area');
    
    history.forEach(exchange => {
        // User bubble
        if (exchange.user) {
            const userRow = document.createElement('div');
            userRow.className = 'bubble-row user';
            userRow.innerHTML = `<div class="avatar user-av">👤</div><div class="bubble user">${exchange.user}</div>`;
            area.appendChild(userRow);
        }
        
        // AI bubble
        if (exchange.assistant) {
            const aiRow = document.createElement('div');
            aiRow.className = 'bubble-row';
            aiRow.innerHTML = `<div class="avatar">🤖</div><div class="bubble ai">${exchange.assistant}</div>`;
            area.appendChild(aiRow);
        }
    });
    
    area.scrollTop = area.scrollHeight;
}

function addAIReplyFromPython(incoming) {
    if (!incoming) return;
    try {
        const area = document.getElementById('ai-area');
        const row = document.createElement('div');
        row.className = 'bubble-row';
        const tipHTML = incoming.tip ? `<div class="tip-tag">💡 Tip</div><div class="tip-text">${incoming.tip}</div>` : '';
        const replyText = incoming.reply || incoming.reply_text || '';
        row.innerHTML = `<div class="avatar">🤖</div><div class="bubble ai">${replyText}${tipHTML}</div>`;
        area.appendChild(row);
        area.scrollTop = area.scrollHeight;
        if (incoming.audio_b64) {
            try {
                const audio = new Audio('data:audio/mpeg;base64,' + incoming.audio_b64);
                audio.play().catch(()=>console.warn('Audio playback blocked'));
            } catch (e) { console.warn('playback failed', e); }
        }
    } catch (e) { console.warn('addAIReplyFromPython failed', e); }
}

function addUserBubble(text) {
    if (!text) return;
    const area = document.getElementById('ai-area');
    const userRow = document.createElement('div');
    userRow.className = 'bubble-row user';
    userRow.innerHTML = `<div class="avatar user-av">👤</div><div class="bubble user">${text}</div>`;
    area.appendChild(userRow);
    area.scrollTop = area.scrollHeight;
}

const demoReplies = [
    { reply: "That sounds great! Can you tell me more about it?", tip: null },
    { reply: "I understand! In English you can also say: 'That's really interesting.'", tip: "Replace 'bahut acha' with 'very interesting' or 'quite fascinating.'" },
    { reply: "Good effort! Let's keep going — you're improving fast.", tip: null },
    { reply: "I see what you mean! Try saying: 'I was not able to come yesterday.'", tip: "Use 'was not able to' for past inability instead of 'could not came.'" },
];

function switchTo(screenId, navItem) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
    if (navItem) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        navItem.classList.add('active');
    } else {
        const idx = ['screen-speak','screen-chat','screen-learn','screen-progress','screen-settings'].indexOf(screenId);
        document.querySelectorAll('.nav-item').forEach((n,i) => n.classList.toggle('active', i===idx));
    }
}

function toggleMic() {
    micActive = !micActive;
    const btn = document.getElementById('mic-btn');
    const ring = document.getElementById('mic-ring');
    const label = document.getElementById('state-label');
    const waveform = document.getElementById('waveform');

    if (micActive) {
        btn.classList.add('listening');
        ring.classList.add('listening');
        label.textContent = 'Listening…';
        label.className = 'state-label listening';
        waveform.classList.add('active');
        startRecognition();
    } else {
        btn.classList.remove('listening');
        ring.classList.remove('listening');
        waveform.classList.remove('active');
        label.textContent = 'Thinking…';
        label.className = 'state-label thinking';
        stopRecognition();
    }
}

let recognition = null;
function startRecognition() {
    const label = document.getElementById('state-label');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        label.textContent = 'Microphone not supported in this browser';
        label.className = 'state-label';
        return;
    }
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        addUserBubble(text);
        // send transcript to Streamlit (parent) using streamlit-aware wrapper
        try { window.parent.postMessage({isStreamlitMessage: true, type: 'transcript', text: text}, '*'); } catch (e) { console.warn('postMessage failed', e); }
    };
    recognition.onerror = function(e) {
        console && console.warn && console.warn('recognition error', e);
        try { window.parent.postMessage({isStreamlitMessage: true, type: 'transcript', text: ''}, '*'); } catch (e) {}
    };
    recognition.onend = function() {
        // update UI to thinking state if still showing
        const label = document.getElementById('state-label');
        label.textContent = 'Thinking…';
        label.className = 'state-label thinking';
        // recognition will be stopped and the Python side will send back the AI reply
    };
    recognition.start();
}

function stopRecognition() {
    if (recognition) {
        try { recognition.stop(); } catch (e) {}
        recognition = null;
    }
}

function addAIReply() {
    const area = document.getElementById('ai-area');
    const r = demoReplies[Math.floor(Math.random() * demoReplies.length)];

    // typing indicator
    const typingRow = document.createElement('div');
    typingRow.className = 'bubble-row';
    typingRow.innerHTML = `<div class="avatar">🤖</div><div class="typing-dots"><span></span><span></span><span></span></div>`;
    area.appendChild(typingRow);
    area.scrollTop = area.scrollHeight;

    setTimeout(() => {
        typingRow.remove();
        const row = document.createElement('div');
        row.className = 'bubble-row';
        let tipHTML = r.tip ? `<div class="tip-tag">💡 Tip</div><div class="tip-text">${r.tip}</div>` : '';
        row.innerHTML = `<div class="avatar">🤖</div><div class="bubble ai">${r.reply}${tipHTML}</div>`;
        area.appendChild(row);
        area.scrollTop = area.scrollHeight;
    }, 1000);
}

function clearChat() {
    const area = document.getElementById('ai-area');
    area.innerHTML = `<div class="bubble-row"><div class="avatar">🤖</div><div class="bubble ai">Chat cleared! Ready when you are. Tap the mic and speak naturally.</div></div>`;
}

function selectLang(el, mode) {
    document.querySelectorAll('.lang-pill').forEach(p => p.classList.remove('selected'));
    el.classList.add('selected');
}

function selectLevel(el) {
    document.querySelectorAll('.level-opt').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
}

function toggleCard(card) {
    card.classList.toggle('expanded');
}

function handleChatKey(e) {
    if (e.key === 'Enter') sendChatMessage();
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    const area = document.getElementById('chat-area');

    // user bubble
    const userRow = document.createElement('div');
    userRow.className = 'bubble-row user';
    userRow.innerHTML = `<div class="avatar user-av">👤</div><div class="bubble user">${text}</div>`;
    area.appendChild(userRow);

    // typing
    const typingRow = document.createElement('div');
    typingRow.className = 'bubble-row';
    typingRow.innerHTML = `<div class="avatar">🤖</div><div class="typing-dots"><span></span><span></span><span></span></div>`;
    area.appendChild(typingRow);
    area.scrollTop = area.scrollHeight;

    // send to Python for a real reply
    try {
        window.parent.postMessage({isStreamlitMessage: true, type: 'chat', text: text}, '*');
    } catch (e) {
        console && console.warn && console.warn('chat postMessage failed', e);
        setTimeout(() => {
            typingRow.remove();
            const r = demoReplies[Math.floor(Math.random() * demoReplies.length)];
            const aiRow = document.createElement('div');
            aiRow.className = 'bubble-row';
            let tipHTML = r.tip ? `<div class="tip-tag">💡 Tip</div><div class="tip-text">${r.tip}</div>` : '';
            aiRow.innerHTML = `<div class="avatar">🤖</div><div class="bubble ai">${r.reply}${tipHTML}</div>`;
            area.appendChild(aiRow);
            area.scrollTop = area.scrollHeight;
        }, 1200);
    }
}

// Ensure mic button is bound even if inline handlers fail
try {
    const _btn = document.getElementById('mic-btn');
    if (_btn) {
        _btn.removeAttribute('onclick');
        _btn.addEventListener('click', toggleMic);
    }
} catch (e) {
    console && console.warn && console.warn('mic binding failed', e);
}

// Load conversation history first
try { 
    if (typeof CONVERSATION_HISTORY !== 'undefined' && CONVERSATION_HISTORY && Array.isArray(CONVERSATION_HISTORY)) { 
        renderConversationHistory(CONVERSATION_HISTORY); 
    } 
} catch(e) { 
    console && console.warn && console.warn('failed loading conversation history', e); 
}

// If Python provided a pending response when rendering, show it now
try { if (typeof PENDING_FROM_PY !== 'undefined' && PENDING_FROM_PY) { addAIReplyFromPython(PENDING_FROM_PY); } } catch(e) { console && console.warn && console.warn('failed injecting python reply', e); }

// Ping parent so Python knows the iframe is ready (debugging)
try { window.parent.postMessage({isStreamlitMessage: true, type: 'ping'}, '*'); } catch(e) {}
</script>
</body>
</html>
    """
    # Inject any pending response (from Python) into the demo HTML so the iframe can play it back.
    # Also inject the conversation history to maintain state across reruns
    try:
        injected_data = json.dumps(pending_from_py) if pending_from_py else 'null'
        # Create a sanitized conversation history (exclude sensitive data)
        sanitized_history = []
        for exchange in conversation_history[-10:]:  # Keep last 10 exchanges
            sanitized_history.append({
                'user': exchange.get('user', ''),
                'assistant': exchange.get('assistant', '')
            })
        history_json = json.dumps(sanitized_history)
        
        print('DEBUG: Attempting to inject PENDING_FROM_PY:', injected_data[:200])
        print('DEBUG: Injecting conversation history with', len(sanitized_history), 'exchanges')
        
        demo_html_filled = demo_html.replace(
            'const PENDING_FROM_PY = __PENDING_RESPONSE__;', 
            f'const PENDING_FROM_PY = {injected_data};'
        )
        demo_html_filled = demo_html_filled.replace(
            'const CONVERSATION_HISTORY = __CONVERSATION_HISTORY__;',
            f'const CONVERSATION_HISTORY = {history_json};'
        )
        
        if 'const PENDING_FROM_PY = __PENDING_RESPONSE__;' in demo_html:
            print('DEBUG: Placeholder found in demo_html')
        if 'const CONVERSATION_HISTORY = __CONVERSATION_HISTORY__;' in demo_html:
            print('DEBUG: Conversation history placeholder found in demo_html')
    except Exception as e:
        print('DEBUG: Exception during injection:', str(e))
        demo_html_filled = demo_html

    result = components.html(demo_html_filled, height=820, scrolling=True)
    # Debug print
    try:
        print('COMPONENTS.HTML returned:', result)
    except Exception:
        pass

    # Track whether iframe has ever communicated successfully. If not, auto-fallback
    # to the native Streamlit UI after a few attempts so the app remains functional.
    if not st.session_state.get('iframe_communicated'):
        st.session_state['iframe_attempts'] = st.session_state.get('iframe_attempts', 0) + 1
        if st.session_state['iframe_attempts'] >= 3:
            st.warning('Demo iframe did not connect — switching to the native interactive UI for reliability.')
            st.session_state['force_native'] = True
            st.experimental_rerun()
    # When the iframe posts a message (via window.parent.postMessage), Streamlit returns it
    # as the `result` value on the next run. Expect a dict-like object with {'type':'transcript'|'chat','text':...}
    if result:
        try:
            data = result if not isinstance(result, str) else json.loads(result)
        except Exception:
            data = result

        # Support wrapped messages from the iframe: look for direct fields or payload wrapper
        if isinstance(data, dict):
            # print for debugging
            print('Received component message:', data)
        if isinstance(data, dict) and ((data.get('type') in ('transcript', 'chat')) or data.get('isStreamlitMessage') or data.get('streamlitMessage')):
            # extract transcript flexibly
            transcript = ''
            if data.get('text'):
                transcript = data.get('text', '').strip()
            elif data.get('payload') and isinstance(data.get('payload'), dict):
                transcript = data.get('payload', {}).get('text', '').strip()
            elif data.get('payload') and isinstance(data.get('payload'), str):
                transcript = data.get('payload', '').strip()
            elif data.get('message'):
                transcript = data.get('message', '').strip()
            if transcript:
                # mark iframe as communicating
                st.session_state['iframe_communicated'] = True
                # Enqueue the transcript in session_state; it will be processed after
                # `process_user_text` is defined later in this script run.
                st.session_state['incoming_transcript'] = transcript
                st.session_state['pending_response'] = None
                st.experimental_rerun()

    # Clear the pending response after rendering so it doesn't persist across runs
    try:
        st.session_state['pending_response'] = None
    except Exception:
        pass

    # If not in demo mode anymore OR if we got a successful response, continue to native UI rendering
    # This allows responses to be displayed even if demo iframe injection fails
    if not st.session_state.get('iframe_communicated') or st.session_state.get('force_native'):
        # Continue to native UI rendering below
        pass
    else:
        st.stop()

# else: render the original Streamlit UI below (kept for advanced integration)

st.markdown('<div class="section-card"><div class="helper-text">One primary action: speak. One fallback: type. One optional view: progress.</div></div>', unsafe_allow_html=True)

# Keep primary conversation settings lightweight and visible only when needed.
learning_level = st.session_state.get("learning_level", "Intermediate")
focus_areas = st.session_state.get("focus_areas", ["Grammar ✏️", "Pronunciation 🎤"])
st.session_state.selected_model = st.session_state.get("selected_model", "Groq")
st.session_state.learning_mode = st.session_state.get("learning_mode", "Conversation")

st.markdown(
    """
    <div>
        <span class="quick-pill">1. Speak or type</span>
        <span class="quick-pill">2. Get a natural reply</span>
        <span class="quick-pill">3. Learn one small thing</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Helper function to create fast, specific system prompt
def create_system_prompt(level, focus_areas_list):
    """Create optimized system prompt for natural, conversational responses"""
    focus_text = ", ".join(focus_areas_list).replace(" ✏️", "").replace(" 📚", "").replace(" 🎤", "").replace(" 💬", "").replace(" 📝", "") if focus_areas_list else "General"
    
    return f"""You are a warm, friendly English-speaking friend. Your job is to help someone learn English through natural conversation—not by teaching, but by talking like a real person.

LEARNER LEVEL: {level}
FOCUS AREAS: {focus_text}

═════════════════════════════════════════════════════════════
🎯 THE GOLDEN RULE - DO THIS EVERY TIME
═════════════════════════════════════════════════════════════

STEP 1: RESPOND LIKE A HUMAN FIRST
  - Answer their message naturally (1-2 sentences)
  - Sound like a real friend, not a teacher
  - Be warm, genuine, conversational

STEP 2: OPTIONALLY ADD ONE LEARNING ELEMENT
  - Pick ONE of these:
    • Translation (if Urdu/mixed detected)
    • Correction (if grammar is wrong)
    • Word upgrade (if a better word exists)
    • Pronunciation tip (if asking how to pronounce)
  - Add it as a short note, not mixed into the main sentence
  
STEP 3: NEVER DO MORE THAN ONE
  - Don't combine translation + correction + alternatives all at once
  - That makes it feel "teaching-like" instead of natural
  
STEP 4: KEEP IT SHORT
  - Total response: 3 lines maximum
  - Each line: 1 thought, not stacked thoughts

═════════════════════════════════════════════════════════════
✅ RESPONSE PATTERN (FOLLOW THIS)
═════════════════════════════════════════════════════════════

GOOD NATURAL RESPONSE:

User: "hay kaise ho tum theek ho"

AI:
  I'm good, thanks! How are you?
  (In English, that means "I'm fine")

That's it. Natural, friendly, light learning.

---

BETTER WITH CONTEXT:

User: "He go yesterday school"

AI:
  I got it. He went to school yesterday.
  We say "went" for past tense.

Simple, clear, conversational.

---

EVEN BETTER - EMOTIONAL FIRST:

User: "Mujhe bahot dar lag raha hai exam"

AI:
  That's scary, I understand. When's your exam?
  (By the way, we say "I'm scared of the exam" in English)

The emotion is validated first, then light learning.

═════════════════════════════════════════════════════════════
❌ WHAT NOT TO DO (ANTI-PATTERNS)
═════════════════════════════════════════════════════════════

DON'T DO THIS (Too much at once):
"Nice to hear from you (translation here) you can also say (alternative) and remember (grammar rule)"

DON'T DO THIS (Teaching voice):
"You should use past tense here. The structure is..."

DON'T DO THIS (Robotic):
"[LAYER 1] I understand [LAYER 2] that means [LAYER 3] better version [LAYER 4] grammar insight"

DON'T DO THIS (Mixing everything):
Combine natural response + translation + correction + alternatives all in one sentence

✅ DO THIS INSTEAD:
Natural response first.
Then optionally: ONE light learning element.
That's all.

═════════════════════════════════════════════════════════════
🎬 HOW TO HANDLE EACH INPUT TYPE
═════════════════════════════════════════════════════════════

TYPE A: PURE URDU INPUT
User: "main aaj bohat thak gaya hoon"

AI:
  Aw, tough day? Get some rest!
  In English we'd say "I'm really tired today"

TYPE B: MIXED URDU + ENGLISH
User: "I kal school nahi gaya"

AI:
  Oh, why'd you miss school?
  We say "I didn't go to school yesterday" instead

TYPE C: BROKEN ENGLISH (GRAMMAR ERROR)
User: "He go yesterday school"

AI:
  He went to school yesterday, nice!
  Past tense is "went," not "go"

TYPE D: CORRECT ENGLISH (NO ERROR)
User: "I went to the market yesterday"

AI:
  That's great! What did you buy?
  (Optional: "You could also say 'I visited the market'" - ONLY if it adds value)

TYPE E: PRONUNCIATION REQUEST
User: "How to pronounce comfortable?"

AI:
  It's COMF-ter-bul (not com-FOR-ta-ble)
  Try saying each part slowly: comf... ter... bul

TYPE F: FREE CONVERSATION
User: "How was your day?"

AI:
  It's been good! How about yours?
  (Keep it light—don't force learning here)

TYPE G: EMOTIONAL INPUT (ESPECIALLY URDU)
User: "Mujhe kuch samajh nahi aa raha, main frustrate hoon"

AI:
  I get it, that's frustrating. What part's confusing?
  We say "I'm frustrated" or "I don't understand" in English

═════════════════════════════════════════════════════════════
💬 TONE & PERSONALITY
═════════════════════════════════════════════════════════════

✓ Sound like a REAL PERSON
  - Use contractions: "I'm", "you're", "we'll"
  - Use casual phrases: "Got it!", "Nice!", "Exactly!", "No worries"
  - Sound warm but natural, not overly cheerful

✓ Be a PATIENT FRIEND
  - Never judge mistakes
  - Always acknowledge what they said
  - Take them seriously
  - Be encouraging without being fake

✓ Teach INVISIBLY
  - Learning should feel incidental to the conversation
  - Not the main point, not a lecture
  - Just natural correction inside normal chat

✗ NEVER:
  - Say "You are wrong" or "mistake detected"
  - Explain grammar formally or in detail
  - Stack multiple corrections together
  - Use teacher-like language: "Let me explain," "The rule is," "You should use"
  - Be fake or overly formal
  - Lecture or make them feel dumb

═════════════════════════════════════════════════════════════
🔑 CONVERSATION RULES
═════════════════════════════════════════════════════════════

RULE 1: ALWAYS UNDERSTAND INTENT FIRST
  - Even if grammar is broken, understand what they mean
  - Respond meaningfully to the meaning, not just the errors
  - Make them feel heard

RULE 2: ONE ELEMENT PER RESPONSE
  - Pick ONE learning element: translation OR correction OR upgrade
  - Don't combine multiple at once
  - Let some small errors slide—it's okay

RULE 3: PRESERVE FLOW
  - Keep conversation natural and moving
  - Don't stop to "teach" mid-conversation
  - Learning is a side effect, not the main event

RULE 4: ADAPT TO LEVEL
  - {level.capitalize()}: 
    ("More Urdu support + simpler English" if level.lower() == "beginner" else "Some Urdu support + balanced" if level.lower() == "intermediate" else "Mostly English, subtle suggestions")
  - Match their language level
  - Meet them where they are

RULE 5: KEEP RESPONSES UNDER 3 LINES
  - Main reply: 1-2 lines
  - Optional learning note: 1 line
  - Total: Never more than 3 lines
  - Longer responses feel overwhelming

═════════════════════════════════════════════════════════════
🎯 RESPONSE STRUCTURE (SIMPLIFIED)
═════════════════════════════════════════════════════════════

Line 1 (Main):
  Natural human response to what they said
  
Line 2 (Optional):
  ONE learning element (translation OR correction OR upgrade)
  Format it as a short note, not a sentence
  
Example 1:
  "Got it! He went yesterday."
  (We use "went" for past tense)

Example 2:
  "I'm good, thanks! How are you?"
  (That means "I'm fine" in English)

Example 3:
  "Nice! What did you buy?"
  [no learning element needed - they were correct]

═════════════════════════════════════════════════════════════
🌍 USE THIS FOR ALL 14 MODES
═════════════════════════════════════════════════════════════

CONVERSATION: Just be a friend. Respond naturally. Optional light correction.

TRANSLATION: Main response naturally. Then translation note.

PRONUNCIATION: Main response + pronunciation breakdown. Keep it short.

GRAMMAR: Main response. Then one grammar note only.

ROLEPLAY: Be the character. Respond in-character. Minimal correction.

STORYTELLING: Respond to story. Ask questions. Minimal correction.

INTERVIEW PREP: Respond naturally as interviewer. Optional: professional version.

SENTENCE VERSIONS: Respond naturally. Optional: show one better version.

EMOTIONAL: Validate emotion first. Then light learning (if at all).

═════════════════════════════════════════════════════════════
✨ THE MOST IMPORTANT RULE
═════════════════════════════════════════════════════════════

Before you respond, ask yourself:

"Would a real friend say this?"

If yes → Keep it
If no → Rewrite it to sound more human

Does it feel like teaching? → It's too formal, simplify it
Does it feel natural? → Perfect, that's the goal
Is it short? → Good
Is it conversational? → Perfect

Remember: You're not a teacher. You're a friend who helps someone learn through talking.

The best response is one that doesn't feel like teaching at all."""


def add_natural_followup(user_input, response_text):
    """Add a human follow-up when it fits the conversation."""
    lowered_input = (user_input or "").lower().strip()
    lowered_response = (response_text or "").lower().strip()

    if any(phrase in lowered_input for phrase in ["how are you", "how r you", "how r u", "how are u"]):
        if "what about you" not in lowered_response:
            return f"{response_text.rstrip('. ')}. What about you?"

    return response_text


def build_recent_context(conversation, limit=3):
    """Summarize recent turns so replies can continue naturally."""
    if not conversation:
        return "No previous conversation yet."

    recent_turns = conversation[-limit:]
    lines = []
    for turn in recent_turns:
        user_text = turn.get("user", "").strip()
        assistant_text = turn.get("assistant", "").strip()
        if user_text:
            lines.append(f"User said: {user_text}")
        if assistant_text:
            lines.append(f"Assistant replied: {assistant_text}")

    return "\n".join(lines) if lines else "No previous conversation yet."


def create_conversational_prompt(level, focus_areas_list, recent_context, user_input, learning_mode="Conversation", roleplay_scenario=None):
    base_prompt = create_system_prompt(level, focus_areas_list)
    
    # Add learning mode specific instructions
    mode_instructions = {
        "Conversation": """FOCUS: Keep the conversation natural and flowing. Only correct important errors. Make the learner feel comfortable.""",
        "Translation": """FOCUS: The learner might mix Urdu and English. Help them understand the natural English version. Show the structure difference. Build their confidence with mixed language.""",
        "Pronunciation": """FOCUS: Point out pronunciation issues gently. Break words into syllables. Give simple mouth position guidance. Offer repetition opportunities.""",
        "Grammar": """FOCUS: Use conversations to teach grammar naturally. When there's a grammar error, explain it simply and show the correct version. Make grammar feel practical, not academic.""",
        "Roleplay": """FOCUS: You are in a roleplay scenario. Stay in character throughout the conversation. React naturally to what the learner says. Make it feel like a real interaction. Keep it engaging and fun.""",
        "Storytelling": """FOCUS: The learner is telling a story. Ask clarifying questions to help them expand. Celebrate descriptive language and emotion. When they finish, praise what they did well and gently suggest where they could add more detail.""",
        "Interview Prep": """FOCUS: You are a professional interviewer. The learner is practicing interview responses. Give constructive feedback on their professionalism, clarity, and confidence. Suggest more professional versions of casual language. Ask follow-up questions if their answer is too short.""",
        "Sentence Versions": """FOCUS: Show the learner their sentence in 3 versions: SIMPLE (basic words, short), NATURAL (conversational, casual), PROFESSIONAL (formal, business). Explain when each version is appropriate. Help them understand the differences.""",
        "Emotional Learning": """FOCUS: The learner is expressing emotions and feelings. First, acknowledge and validate their feelings. If they use Urdu, show the English translation in an emotionally expressive way. Teach them emotional vocabulary in context. Make them feel heard and understood."""
    }
    
    mode_instruction = mode_instructions.get(learning_mode, mode_instructions["Conversation"])
    
    # Add roleplay context if in roleplay mode
    roleplay_context = ""
    if learning_mode == "Roleplay" and roleplay_scenario:
        from language_utils import get_roleplay_scenario
        scenario = get_roleplay_scenario(roleplay_scenario)
        roleplay_context = f"\n\nROLEPLAY SCENARIO: {scenario['title']}\nYou are: {scenario['ai_character']}\nContext: {scenario['description']}"
    
    return f"""{base_prompt}

{mode_instruction}{roleplay_context}

RECENT CONVERSATION:
{recent_context}

CURRENT USER MESSAGE:
{user_input}

Remember: reply like a friendly human friend. First respond to what the user said, then gently correct only if needed, and end with one natural follow-up question to keep the chat moving."""


def generate_learning_insights(transcript, response, learning_mode="Conversation"):
    """
    Generate personalized learning insights from the interaction
    Shows user what they did well and what to work on
    """
    from language_utils import (extract_learning_context, detect_urdu_interference_patterns, 
                               create_personalized_learning_tip, suggest_vocabulary_alternatives,
                               suggest_fluency_coaching, analyze_story_quality, improve_interview_response,
                               improve_sentence_to_levels, detect_urdu_emotion, suggest_emotional_vocabulary)
    
    context = extract_learning_context(transcript)
    urdu_interference = detect_urdu_interference_patterns(transcript)
    
    insights = []
    
    # Interview Prep mode
    if learning_mode == "Interview Prep":
        improvement = improve_interview_response(transcript)
        if improvement["strengths"]:
            insights.append(f"✅ {improvement['strengths'][0]}")
        if improvement["length_feedback"]:
            insights.append(improvement["length_feedback"])
        if improvement["tone_feedback"]:
            insights.append(improvement["tone_feedback"])
        if improvement["improvements"]:
            insights.append(f"💡 {improvement['improvements'][0]}")
        return "\n".join(insights)
    
    # Sentence Versions mode
    if learning_mode == "Sentence Versions":
        versions = improve_sentence_to_levels(transcript)
        insights.append(f"📝 **Your sentence**: {versions['original']}")
        insights.append(f"✨ **Simple**: Easy to understand, beginner-friendly")
        insights.append(f"💬 **Natural**: How native speakers actually say it (casual)")
        insights.append(f"💼 **Professional**: Business and formal situations")
        if versions["tips"]["for_learning"]:
            insights.append(f"💡 {versions['tips']['for_learning']}")
        return "\n".join(insights)
    
    # Emotional Learning mode
    if learning_mode == "Emotional Learning":
        emotion_detection = detect_urdu_emotion(transcript)
        if emotion_detection["detected_emotions"]:
            insights.append(f"❤️ **Emotion detected**: {', '.join([e['english_translation'] for e in emotion_detection['detected_emotions']])}")
            insights.append(f"✨ In expressive English: \"{emotion_detection.get('emotional_english', 'Your feeling...')}\"")
            
            # Suggest vocabulary for the emotion
            if emotion_detection["detected_emotions"]:
                first_emotion = emotion_detection["detected_emotions"][0]
                vocab_suggestion = suggest_emotional_vocabulary(first_emotion["urdu"])
                if vocab_suggestion["emotion_type"]:
                    insights.append(f"\n📚 **Ways to express {vocab_suggestion['emotion_type']}:**")
                    insights.append(f"  • Subtle: {vocab_suggestion['english_versions']['subtle']}")
                    insights.append(f"  • Normal: {vocab_suggestion['english_versions']['moderate']}")
                    insights.append(f"  • Strong: {vocab_suggestion['english_versions']['intense']}")
        
        if emotion_detection["expression_analysis"]:
            for expr in emotion_detection["expression_analysis"]:
                if "aap" in expr["context_word"]:
                    insights.append(f"📌 You used formal language - great for respectful contexts!")
                elif "tum" in expr["context_word"]:
                    insights.append(f"💬 You used casual language - perfect with friends!")
        
        if insights:
            return "\n".join(insights)
        else:
            insights.append("Share how you're feeling! Use Urdu or English - I'll help you express it beautifully.")
            return "\n".join(insights)
    
    # Standard modes (Conversation, Translation, Pronunciation, Grammar, Roleplay, Storytelling)
    # Positive feedback first
    if context["error_count"] == 0:
        insights.append("✅ Perfect! Your sentence was grammatically correct.")
    else:
        insights.append(f"📝 Found {context['error_count']} thing(s) to work on - normal and expected!")
    
    # Language mix feedback
    if context["has_mixed_language"]:
        insights.append(f"🔄 Code-switching detected: You're mixing Urdu and English (good practice!)")
    else:
        insights.append("🎯 You spoke entirely in English - great confidence!")
    
    # Urdu interference insights
    if urdu_interference:
        for pattern in urdu_interference[:1]:  # Show top 1 pattern
            insights.append(f"💡 {pattern['urdu_interference']}")
    
    # Grammar/Pronunciation insights
    if context["grammar_errors"]:
        errors = context["grammar_errors"][:1]
        for error in errors:
            insights.append(f"📚 Grammar tip: {error['fix']}")
    
    if context["pronunciation_issues"]:
        issues = context["pronunciation_issues"][:1]
        for issue in issues:
            insights.append(f"🎤 Pronunciation: {issue['tip']}")
    
    # Vocabulary alternatives for simple words
    words = transcript.lower().split()
    for word in words[:3]:  # Check first 3 words
        vocab_alt = suggest_vocabulary_alternatives(word)
        if vocab_alt["found"]:
            insights.append(f"📚 {vocab_alt['suggestion']}")
            break
    
    # Fluency coaching for longer sentences
    if len(words) > 8:
        fluency = suggest_fluency_coaching(transcript)
        if fluency.get("chunking_suggestion"):
            insights.append(f"🎤 {fluency['rhythm_tip']}")
    
    # Storytelling analysis if in that mode
    if learning_mode == "Storytelling":
        story_analysis = analyze_story_quality(transcript)
        if story_analysis["strengths"]:
            insights.append(f"✨ {story_analysis['strengths'][0]}")
        if story_analysis.get("overall_assessment"):
            insights.append(story_analysis["overall_assessment"])
    
    return "\n".join(insights)

# Helper function to detect language mix
def detect_language_mix(text):
    """Detect if text contains Urdu"""
    urdu_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(urdu_pattern.search(text))


def get_gemini_model():
    return genai.GenerativeModel('gemini-flash-latest')


def extract_groq_text(response):
    if hasattr(response, 'choices') and response.choices:
        choice = response.choices[0]
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            return choice.message.content
        if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
            return choice.delta.content
    if hasattr(response, 'output_text'):
        return response.output_text
    return str(response)


def build_conversational_speech(response_text):
    """Turn the structured learning response into natural spoken English."""
    cleaned = response_text
    cleaned = cleaned.replace("✏️", "")
    cleaned = cleaned.replace("🎤", "")
    cleaned = cleaned.replace("💬", "")
    cleaned = cleaned.replace("💡", "")
    cleaned = cleaned.replace("**", "")
    cleaned = re.sub(r"(?im)^\s*(grammar|pronunciation|say this|tip)\s*:?\s*", "", cleaned)
    cleaned = re.sub(r"(?im)^\s*[-*•]\s*", "", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\btip\b\s*:?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bpronunciation\b\s*:?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bgrammar\b\s*:?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bsound\b\s*:?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[\r\n]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        cleaned = "You’re doing well. Try saying it again, nice and natural."

    # Only add "say it again" if response contains correction indicators and doesn't already have it
    has_correction_markers = re.search(r"(?i)(should be|instead|better|not quite|correction|right|proper|corrected|actually|would be)", cleaned)
    has_repeat_phrase = re.search(r"(?i)(try again|say it again|repeat|say that back|say it back|again after me)", cleaned)
    
    if has_correction_markers and not has_repeat_phrase:
        cleaned = f"{cleaned} Now say it again after me."

    return cleaned


def clean_text_for_speech(text):
    spoken_text = build_conversational_speech(text)
    spoken_text = re.sub(r"\s+", " ", spoken_text).strip()
    return spoken_text


def transcribe_audio_bytes(audio_bytes):
    if sr is None:
        return None, "MIC_UNAVAILABLE"

    recognizer = sr.Recognizer()
    sample_rate = 16000
    sample_width = 2

    if not audio_bytes:
        return None, "NO_SPEECH"

    try:
        with sr.AudioFile(BytesIO(audio_bytes)) as source:
            audio = recognizer.record(source)
            transcript = recognizer.recognize_google(audio, language="en-US")
            transcript = transcript.strip()
            return (transcript if transcript else None), (None if transcript else "NO_SPEECH")
    except sr.UnknownValueError:
        return None, "NO_SPEECH"
    except sr.RequestError as error:
        return None, f"STT_ERROR:{error}"
    except Exception:
        try:
            audio = sr.AudioData(audio_bytes, sample_rate, sample_width)
            transcript = recognizer.recognize_google(audio, language="en-US")
            transcript = transcript.strip()
            return (transcript if transcript else None), (None if transcript else "NO_SPEECH")
        except sr.UnknownValueError:
            return None, "NO_SPEECH"
        except sr.RequestError as error:
            return None, f"STT_ERROR:{error}"
        except Exception as error:
            return None, f"STT_ERROR:{error}"


def speech_to_audio_bytes(text):
    if gTTS is None:
        return None

    try:
        tts = gTTS(text=clean_text_for_speech(text), lang="en", slow=False)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


def render_spoken_audio(audio_bytes):
    if not audio_bytes:
        return

    encoded_audio = base64.b64encode(audio_bytes).decode("utf-8")
    st.markdown(
        f"""
        <audio autoplay controls style="width: 100%; margin-top: 0.5rem;">
            <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )

# Function to call Gemini API (faster endpoint configuration)
def call_gemini(user_input, gemini_api_key, level, focus_areas_list, recent_context, learning_mode="Conversation", roleplay_scenario=None):
    """Call Gemini API with streaming for low latency"""
    try:
        genai.configure(api_key=gemini_api_key)
        model = get_gemini_model()
        
        full_prompt = create_conversational_prompt(level, focus_areas_list, recent_context, user_input, learning_mode, roleplay_scenario)
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini error: {str(e)[:50]}"

# Function to call Groq API (FASTEST - recommended)
def call_groq(user_input, groq_api_key, level, focus_areas_list, recent_context, learning_mode="Conversation", roleplay_scenario=None):
    """Call Groq API - Ultra-fast responses (1-2 seconds)"""
    try:
        client = Groq(api_key=groq_api_key)
        system_prompt = create_conversational_prompt(level, focus_areas_list, recent_context, user_input, learning_mode, roleplay_scenario)
        
        start_time = time.time()
        
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=512,  # Reduced for faster response
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.5  # Reduced for faster, more consistent responses
        )
        
        response_time = time.time() - start_time
        response_text = extract_groq_text(message)
        
        return response_text, response_time
    except Exception as e:
        return f"⚠️ Groq error: {str(e)[:50]}", 0


# ============ SCREEN-BASED EXPERIENCE ============

screen_labels = ["🎤 Speak", "💬 Chat", "📘 Learn", "📊 Progress", "⚙ Settings"]
screen_map = {
    "🎤 Speak": "Speak",
    "💬 Chat": "Chat",
    "📘 Learn": "Learn",
    "📊 Progress": "Progress",
    "⚙ Settings": "Settings",
}
reverse_screen_map = {value: key for key, value in screen_map.items()}
current_screen = st.session_state.get("app_screen", "Speak")

learning_mode_options = ["Conversation", "Translation", "Pronunciation", "Grammar", "Roleplay", "Storytelling", "Interview Prep", "Sentence Versions", "Emotional Learning"]
learning_mode_help = {
    "Conversation": "Natural speaking first. One small tip only.",
    "Translation": "Urdu or mixed input becomes simple English.",
    "Pronunciation": "Show one sound or stress hint.",
    "Grammar": "One correction, one rule, no lecture.",
    "Roleplay": "Stay in character and keep it realistic.",
    "Storytelling": "Help the user expand one story clearly.",
    "Interview Prep": "Practice short, confident answers.",
    "Sentence Versions": "Show simple, natural, and professional.",
    "Emotional Learning": "Validate feelings first, then help with English."
}

def update_session_settings_from_screen():
    st.session_state.learning_level = st.session_state.get("learning_level", "Intermediate")
    st.session_state.focus_areas = st.session_state.get("focus_areas", ["Grammar ✏️", "Pronunciation 🎤"])
    st.session_state.selected_model = st.session_state.get("selected_model", "Groq")
    st.session_state.learning_mode = st.session_state.get("learning_mode", "Conversation")


def process_user_text(user_text: str):
    if not user_text or not user_text.strip():
        return
    print('DEBUG: process_user_text called with:', user_text[:200])
    print('DEBUG: selected_model:', st.session_state.get('selected_model'))
    print('DEBUG: groq_key present:', bool(os.getenv('GROQ_API_KEY') or globals().get('groq_key')))
    print('DEBUG: gemini_key present:', bool(os.getenv('GEMINI_API_KEY') or globals().get('gemini_key')))

    update_session_settings_from_screen()
    recent_context = build_recent_context(st.session_state.conversation, limit=3)

    if "Groq" in st.session_state.selected_model:
        response, resp_time = call_groq(
            user_text,
            groq_key,
            st.session_state.learning_level,
            st.session_state.focus_areas,
            recent_context,
            st.session_state.learning_mode,
            st.session_state.current_roleplay,
        )
        print('DEBUG: Groq response (raw):', str(response)[:300], 'resp_time:', resp_time)
    else:
        start = time.time()
        response = call_gemini(
            user_text,
            gemini_key,
            st.session_state.learning_level,
            st.session_state.focus_areas,
            recent_context,
            st.session_state.learning_mode,
            st.session_state.current_roleplay,
        )
        resp_time = time.time() - start
        print('DEBUG: Gemini response (raw):', str(response)[:300], 'resp_time:', resp_time)

    response = add_natural_followup(user_text, response)
    st.session_state.response_time = resp_time
    st.session_state.last_transcript = user_text
    st.session_state.last_spoken_reply = response
    print('DEBUG: stored last_spoken_reply:', response[:200])
    
    audio_bytes = speech_to_audio_bytes(response)
    print('DEBUG: speech_to_audio_bytes returned:', 'bytes' if audio_bytes else 'None')
    st.session_state.last_voice_audio = audio_bytes
    
    st.session_state.conversation.append({
        "user": user_text,
        "assistant": response,
        "has_urdu": detect_language_mix(user_text),
        "model": st.session_state.selected_model,
        "time": resp_time,
    })
    print('DEBUG: appended to conversation, total exchanges:', len(st.session_state.conversation))


# If a transcript was posted from the demo iframe earlier, process it now
if st.session_state.get('incoming_transcript'):
    _trans = st.session_state.pop('incoming_transcript')
    print('DEBUG: Processing incoming_transcript:', _trans[:100])
    if _trans:
        process_user_text(_trans)
        # prepare pending response for the iframe to consume (reply text + audio)
        audio_b64 = None
        if st.session_state.get('last_voice_audio'):
            audio_b64 = base64.b64encode(st.session_state.last_voice_audio).decode('utf-8')
        # mark iframe as communicating
        st.session_state['iframe_communicated'] = True
        reply_text = st.session_state.get('last_spoken_reply', '')
        st.session_state['pending_response'] = {
            'reply': reply_text,
            'audio_b64': audio_b64,
            'tip': None,
        }
        print('DEBUG: Set pending_response with reply:', reply_text[:200], 'has audio:', bool(audio_b64))
        st.experimental_rerun()


def render_conversation_history(limit=None):
    exchanges = st.session_state.conversation if limit is None else st.session_state.conversation[-limit:]
    for exchange in exchanges:
        with st.chat_message("user"):
            st.write(exchange["user"])
        with st.chat_message("assistant"):
            st.write(exchange["assistant"])


def render_voice_capture(key_name: str):
    if mic_recorder is None:
        st.warning("Voice recorder is not available in this environment.")
        return None

    return mic_recorder(
        start_prompt="🎙️ Tap to speak",
        stop_prompt="Stop",
        just_once=False,
        use_container_width=True,
        format="wav",
        key=key_name,
    )


def render_response_preview():
    if not st.session_state.last_transcript or not st.session_state.last_spoken_reply:
        return

    with st.chat_message("user"):
        st.write(st.session_state.last_transcript)
    with st.chat_message("assistant"):
        st.write(st.session_state.last_spoken_reply)


if current_screen == "Speak":
    st.markdown(
        """
        <div class="screen-card">
            <div class="screen-label">Voice first</div>
            <div class="screen-title">Speak naturally</div>
            <p class="screen-copy">Press the mic, talk like a friend, and get one calm improvement tip.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="quick-pill">Learning focus: {st.session_state.learning_mode}</div>', unsafe_allow_html=True)

    voice_bytes = None
    user_audio = render_voice_capture("speak_voice_recorder")
    if isinstance(user_audio, dict):
        voice_bytes = user_audio.get("bytes") or user_audio.get("audio") or user_audio.get("blob")
    elif isinstance(user_audio, (bytes, bytearray)):
        voice_bytes = bytes(user_audio)

    if voice_bytes:
        audio_hash = hash(voice_bytes)
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash

            with st.spinner("Listening…"):
                transcript, transcript_error = transcribe_audio_bytes(voice_bytes)

            if transcript_error == "NO_SPEECH" or not transcript:
                no_speech_reply = "I couldn’t hear that clearly. Try again a little louder."
                st.session_state.last_transcript = ""
                st.session_state.last_spoken_reply = no_speech_reply
                st.session_state.last_voice_audio = speech_to_audio_bytes(no_speech_reply)
                st.session_state.response_time = 0
            else:
                print('DEBUG: Calling process_user_text from Speak screen')
                process_user_text(transcript)
                print('DEBUG: After process_user_text, last_spoken_reply:', st.session_state.get('last_spoken_reply', '')[:100])
                # Don't rerun - display the response immediately in the current render

    print('DEBUG: Speak screen rendering, last_spoken_reply:', st.session_state.get('last_spoken_reply', '')[:50] if st.session_state.get('last_spoken_reply') else 'empty')
    
    if st.session_state.last_voice_audio:
        render_spoken_audio(st.session_state.last_voice_audio)

    if st.session_state.last_transcript:
        st.success("Speech understood")
        render_response_preview()

    typed_message = st.chat_input("Type instead of speaking")
    if typed_message:
        process_user_text(typed_message)
        st.rerun()

    if st.session_state.show_detailed_feedback and st.session_state.last_transcript and st.session_state.last_spoken_reply:
        insights = generate_learning_insights(st.session_state.last_transcript, st.session_state.last_spoken_reply, st.session_state.learning_mode)
        if insights:
            st.markdown('<div class="screen-card"><div class="screen-label">One small tip</div>', unsafe_allow_html=True)
            st.write(insights)
            st.markdown('</div>', unsafe_allow_html=True)

elif current_screen == "Chat":
    st.markdown(
        """
        <div class="screen-card">
            <div class="screen-label">Chat mode</div>
            <div class="screen-title">Talk in simple bubbles</div>
            <p class="screen-copy">Type or tap the mic. The AI replies like a calm friend.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_voice = render_voice_capture("chat_voice_recorder")
    chat_voice_bytes = None
    if isinstance(chat_voice, dict):
        chat_voice_bytes = chat_voice.get("bytes") or chat_voice.get("audio") or chat_voice.get("blob")
    elif isinstance(chat_voice, (bytes, bytearray)):
        chat_voice_bytes = bytes(chat_voice)

    if chat_voice_bytes:
        audio_hash = hash(chat_voice_bytes)
        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            with st.spinner("Listening…"):
                transcript, transcript_error = transcribe_audio_bytes(chat_voice_bytes)
            if transcript_error == "NO_SPEECH" or not transcript:
                st.info("I couldn’t hear that clearly. Try speaking a bit louder.")
            else:
                process_user_text(transcript)
                st.rerun()

    if st.session_state.conversation:
        render_conversation_history(limit=6)

    chat_text = st.chat_input("Send a message")
    if chat_text:
        print('DEBUG: Chat text input received:', chat_text[:100])
        process_user_text(chat_text)
        print('DEBUG: After process_user_text, last_spoken_reply:', st.session_state.get('last_spoken_reply', '')[:100])
        # Don't rerun - display the response immediately

elif current_screen == "Learn":
    st.markdown(
        """
        <div class="screen-card">
            <div class="screen-label">Light learning</div>
            <div class="screen-title">One concept at a time</div>
            <p class="screen-copy">Pick a focus, then see one correction and one short explanation only.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_mode = st.selectbox("Learning focus", learning_mode_options, index=learning_mode_options.index(st.session_state.learning_mode), key="learning_mode")
    st.caption(learning_mode_help.get(selected_mode, "Learn naturally."))

    if st.session_state.last_transcript and st.session_state.last_spoken_reply:
        insights = generate_learning_insights(st.session_state.last_transcript, st.session_state.last_spoken_reply, selected_mode)
        st.markdown('<div class="screen-card"><div class="screen-label">Latest turn</div>', unsafe_allow_html=True)
        st.write(f"**User:** {st.session_state.last_transcript}")
        st.write(f"**AI:** {st.session_state.last_spoken_reply}")
        if insights:
            tip_line = insights.split("\n")[0]
            st.markdown(f'<div class="quick-pill">💡 {tip_line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("How this mode works", expanded=False):
            st.write(learning_mode_help.get(selected_mode, "Talk naturally and learn one small thing."))

elif current_screen == "Progress":
    from language_utils import assess_learning_progress
    progress = assess_learning_progress(st.session_state.conversation)
    total_turns = progress.get("total_exchanges", 0)
    total_minutes = round(sum(turn.get("time", 0) for turn in st.session_state.conversation) / 60, 1)
    total_words = sum(len(turn.get("user", "").split()) for turn in st.session_state.conversation)
    speaking_minutes = round(max(0.1, total_words / 130), 1) if total_words else 0
    confidence_score = min(100, max(15, 45 + total_turns * 4 - int(progress.get("avg_errors_per_exchange", 0) * 10)))

    learned_words = []
    stopwords = {"the", "and", "you", "for", "that", "this", "with", "have", "your", "from", "are", "was", "were", "been", "will", "would", "could", "should", "about", "there", "their", "what", "when", "where", "they", "them", "then", "than", "good", "nice", "really", "like"}
    for exchange in reversed(st.session_state.conversation):
        for token in re.findall(r"\b[a-zA-Z]{5,}\b", exchange.get("assistant", "")):
            lower_token = token.lower()
            if lower_token not in stopwords and lower_token not in learned_words:
                learned_words.append(lower_token)
            if len(learned_words) >= 3:
                break
        if len(learned_words) >= 3:
            break

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔥 Practice turns", total_turns)
        st.metric("⏱ Speaking time", f"{speaking_minutes} min")
    with col2:
        st.metric("💪 Confidence", f"{confidence_score}%")
        st.metric("🧠 AI time", f"{total_minutes} min")

    st.progress(confidence_score / 100)
    st.markdown('<div class="screen-card"><div class="screen-label">Words learned</div>', unsafe_allow_html=True)
    if learned_words:
        st.write(", ".join(learned_words))
    else:
        st.write("Speak a little more to see words here.")
    st.markdown('</div>', unsafe_allow_html=True)

elif current_screen == "Settings":
    st.markdown(
        """
        <div class="screen-card">
            <div class="screen-label">Minimal settings</div>
            <div class="screen-title">Keep it simple</div>
            <p class="screen-copy">Only the essentials: level, Urdu support, reminder, and voice speed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.learning_level = st.select_slider(
        "Learning level",
        options=["Beginner", "Intermediate", "Advanced"],
        value=st.session_state.get("learning_level", "Intermediate")
    )
    st.session_state.selected_model = st.selectbox(
        "Response engine",
        ["Groq", "Gemini"],
        index=0 if st.session_state.get("selected_model", "Groq") == "Groq" else 1,
    )
    st.session_state.voice_speed = st.select_slider(
        "Voice speed",
        options=["Slow", "Normal", "Fast"],
        value=st.session_state.get("voice_speed", "Normal")
    )
    st.session_state.urdu_support = st.toggle("Urdu support", value=st.session_state.get("urdu_support", True))
    st.session_state.daily_reminder = st.toggle("Daily reminder", value=st.session_state.get("daily_reminder", False))
    st.session_state.focus_areas = st.multiselect(
        "What should the coach focus on?",
        ["Grammar ✏️", "Vocabulary 📚", "Pronunciation 🎤", "Conversation 💬", "Writing 📝"],
        default=st.session_state.get("focus_areas", ["Grammar ✏️", "Pronunciation 🎤"])
    )
    st.caption("All keys stay in `.env`. The page never shows them.")


nav_choice = st.radio(
    "Navigation",
    screen_labels,
    horizontal=True,
    index=screen_labels.index(reverse_screen_map.get(current_screen, "Speak")),
    key="bottom_nav"
)
st.session_state.app_screen = screen_map.get(nav_choice, "Speak")

st.markdown('<div class="screen-card"><div class="screen-label">Keep going</div><div class="screen-title">Speak first. Everything else stays quiet.</div><p class="screen-copy">The app is designed to feel calm, simple, and voice-first on mobile and desktop.</p></div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin: 0.5rem 0 5.2rem 0; color: #667085; font-size: 0.84rem;">
<small>English Learning Assistant • calm voice-first coach</small>
</div>
""", unsafe_allow_html=True)
