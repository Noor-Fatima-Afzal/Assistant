"""
Configuration settings for the English Learning Assistant
"""

# Model Configuration
MODELS = {
    "Gemini": {
        "name": "Google Gemini Pro",
        "model_id": "gemini-flash-latest",
        "max_tokens": 2048,
        "temperature": 0.7,
        "description": "Best for context understanding and detailed explanations"
    },
    "Groq": {
        "name": "Groq Mixtral 8x7B",
        "model_id": "llama-3.1-8b-instant",
        "max_tokens": 1024,
        "temperature": 0.7,
        "description": "Very fast response times, excellent for quick feedback"
    }
}

# Learning Levels
LEARNING_LEVELS = {
    "Beginner": {
        "description": "A1-A2 (CEFR) - Basic English knowledge",
        "vocabulary_size": "500-1500 words",
        "focus": "Basic grammar, simple conversations, essential vocabulary"
    },
    "Intermediate": {
        "description": "B1-B2 (CEFR) - Intermediate proficiency",
        "vocabulary_size": "1500-4000 words",
        "focus": "Complex sentences, nuanced conversations, idiomatic expressions"
    },
    "Advanced": {
        "description": "C1-C2 (CEFR) - Advanced proficiency",
        "vocabulary_size": "4000+ words",
        "focus": "Subtle language use, advanced writing, professional communication"
    }
}

# Focus Areas with Descriptions
FOCUS_AREAS = {
    "Grammar": {
        "description": "Sentence structure, tenses, parts of speech",
        "example": "Using present perfect vs simple past correctly"
    },
    "Vocabulary": {
        "description": "Learning new words, phrases, and expressions",
        "example": "Synonyms, antonyms, colloquial terms"
    },
    "Pronunciation": {
        "description": "Correct pronunciation and phonetic guidance",
        "example": "How to pronounce challenging words"
    },
    "Conversation": {
        "description": "Natural dialogue, responses, and interactions",
        "example": "Common phrases, turn-taking, politeness strategies"
    },
    "Writing": {
        "description": "Written expression, formal letters, essays",
        "example": "Email writing, punctuation, paragraph structure"
    }
}

# Example Mixed English-Urdu Conversations
EXAMPLE_CONVERSATIONS = [
    {
        "user_input": "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain",
        "expected_response": "I think you are going to the zoo",
        "urdu_phrase": "جہاں پر جانور ہوتے ہیں",
        "meaning": "where animals are",
        "english_equivalent": "zoo"
    },
    {
        "user_input": "Mera naam sara hai, aur main english seekh rahi hoon",
        "expected_response": "My name is Sara, and I am learning English",
        "urdu_phrase": "میرا نام سارہ ہے، اور میں انگریزی سیکھ رہی ہوں",
        "english_equivalent": "My name is Sara, and I am learning English"
    },
    {
        "user_input": "Aaj weather bahut garrum hai, so I am staying inside",
        "expected_response": "Today the weather is very hot, so I am staying inside",
        "urdu_phrase": "آج موسم بہت گرم ہے",
        "english_equivalent": "Today's weather is very hot"
    },
    {
        "user_input": "I love playing cricket, especially badminton... nahi wait, do alag hain",
        "expected_response": "I love playing cricket. Wait, I think I mean badminton - those are two different sports",
        "correction": "Cricket and badminton are different sports"
    }
]

# Urdu Character Ranges for Detection
URDU_CHAR_RANGES = {
    "start": 0x0600,
    "end": 0x06FF,
    "description": "Unicode range for Urdu/Arabic script"
}

# System Prompt Templates - Optimized for Speed & Accuracy
SYSTEM_PROMPTS = {
    "base": """You are a real-time English tutor (like a texting friend). Keep ALL responses under 3 sentences!

Analyze ONLY:
1. Grammar errors (tense, articles, verb forms, capitalization)
2. Pronunciation issues (difficult sounds)
3. Word order problems

Format EXACTLY like this (very brief):
✏️ **GRAMMAR:** [Error name + fix] OR "none"
🎤 **PRONUNCIATION:** [Difficult words + how to say] OR "none"
💬 **SAY THIS:** [The correct version - natural English]
💡 **TIP:** [One learning point - 1 sentence max]

SPEED IS KEY! Don't explain - just correct.""",

    "beginner": """Real-time English tutor for beginners. Be VERY SHORT (2 sentences max per section).

Focus on:
- Basic grammar (I/you/he/she, is/are, simple tenses)
- Common pronunciation (TH, R sounds)
- Essential structure

Format:
✏️ **GRAMMAR:** [Simple fix]
🎤 **PRONUNCIATION:** [1-2 words that are hard]
💬 **SAY THIS:** [Better way]
💡 **TIP:** [Easy rule]""",

    "intermediate": """Real-time tutor for intermediate learners. Keep it FAST (3 sentences max total).

Focus on:
- Advanced grammar (perfect tenses, conditionals, passive)
- Word choice accuracy
- Pronunciation nuances

Format:
✏️ **GRAMMAR:** [Pattern + why]
🎤 **PRONUNCIATION:** [Technical tip]
💬 **SAY THIS:** [More natural]
💡 **TIP:** [Advanced pattern]""",

    "advanced": """Expert English coach for advanced learners. Stay under 3 sentences!

Focus on:
- Subtle grammar distinctions
- Formal vs informal registers
- Pronunciation precision
- Idiomatic accuracy

Format:
✏️ **GRAMMAR:** [Nuance + context]
🎤 **PRONUNCIATION:** [Advanced technique]
💬 **SAY THIS:** [Precise version]
💡 **TIP:** [Register/style point]"""
}

# Response Evaluation Criteria
EVALUATION_CRITERIA = [
    "Grammar correctness",
    "Vocabulary appropriateness",
    "Natural flow and idiomaticity",
    "Cultural and contextual awareness",
    "Pronunciation guidance (if applicable)"
]

# API Configuration
API_CONFIG = {
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com",
        "model": "gemini-flash-latest",
        "timeout": 30,
        "max_retries": 2
    },
    "groq": {
        "base_url": "https://api.groq.com",
        "model": "llama-3.1-8b-instant",
        "timeout": 20,
        "max_retries": 2
    }
}

# Supported Languages (for future expansion)
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "ur", "name": "Urdu"},
]

# UI Configuration
UI_CONFIG = {
    "page_title": "English Learning Assistant",
    "page_icon": "🌍",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Feature Flags (for development)
FEATURES = {
    "conversation_history": True,
    "progress_tracking": True,
    "vocabulary_suggestions": True,
    "learning_metrics": True,
    "dual_model_support": True,
    "code_switching_detection": True
}

if __name__ == "__main__":
    print("Configuration loaded successfully!")
    print(f"Available models: {list(MODELS.keys())}")
    print(f"Learning levels: {list(LEARNING_LEVELS.keys())}")
    print(f"Focus areas: {list(FOCUS_AREAS.keys())}")
