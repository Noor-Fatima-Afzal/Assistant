"""
Utility functions for English-Urdu language processing
Optimized for real-time, low-latency feedback
"""

import re
from typing import Dict, Tuple, List

# Urdu character ranges
URDU_PATTERN = re.compile(r'[\u0600-\u06FF]+')

# Common Urdu-English phrase mappings for learning
COMMON_PHRASES = {
    "janwar": "animal",
    "ghar": "home/house",
    "school": "school",
    "park": "park",
    "kitaab": "book",
    "dost": "friend",
    "khana": "food",
    "paani": "water",
    "beta": "son",
    "beti": "daughter",
    "maa": "mother",
    "baap": "father",
    "bhaia": "brother",
    "bahan": "sister",
}

# Grammar patterns that often cause errors
COMMON_GRAMMAR_ERRORS = {
    r"\bi\b": "should be 'I' (capital)",
    r"\byou\s+is\b": "should be 'you are'",
    r"\the\s+are\b": "should be 'he is'",
    r"\bshe\s+are\b": "should be 'she is'",
    r"\bi\s+am\s+going\s+in\b": "should be 'going to' not 'going in'",
}

# Common pronunciation patterns (phonetic difficulties)
PRONUNCIATION_PATTERNS = {
    r"\bth\w+\b": "Check: TH sound (like 'think' or 'this')",
    r"\b\w*tion$": "Check: -TION sounds like 'shun'",
    r"\bwh\w+\b": "Check: WH sounds like 'w' (not 'h')",
}

def detect_grammar_errors(text: str) -> List[Dict]:
    """
    Detect common grammar patterns that might be errors
    
    Args:
        text (str): Input text
        
    Returns:
        List of detected potential grammar errors
    """
    errors = []
    
    # Check for lowercase 'i'
    if re.search(r'\bi\b', text):
        errors.append({
            "type": "GRAMMAR",
            "pattern": "Lowercase 'I'",
            "fix": "Always capitalize 'I': 'I am...' not 'i am...'",
            "severity": "high"
        })
    
    # Check for subject-verb agreement issues
    if re.search(r'\b(you|they)\s+is\b', text, re.IGNORECASE):
        errors.append({
            "type": "GRAMMAR",
            "pattern": "Subject-verb agreement",
            "fix": "Use 'are' with 'you/they': 'You are' not 'You is'",
            "severity": "high"
        })
    
    if re.search(r'\b(he|she|it)\s+are\b', text, re.IGNORECASE):
        errors.append({
            "type": "GRAMMAR",
            "pattern": "Subject-verb agreement",
            "fix": "Use 'is' with he/she/it: 'He is' not 'He are'",
            "severity": "high"
        })
    
    # Check for missing 'to' in going to
    if re.search(r'\bgoing\s+(in|at|on)\b', text, re.IGNORECASE):
        errors.append({
            "type": "GRAMMAR",
            "pattern": "Missing 'to'",
            "fix": "Use 'going to' not 'going in': 'I'm going to school'",
            "severity": "medium"
        })
    
    # Check for double subjects (Urdu interference)
    if re.search(r'\b(main|mera|main\s+)\w+\s+i\s+', text, re.IGNORECASE):
        errors.append({
            "type": "GRAMMAR",
            "pattern": "Double subject (Urdu interference)",
            "fix": "Use either Urdu or English: 'Main jata hoon' OR 'I go' (not both)",
            "severity": "medium"
        })
    
    return errors

def detect_pronunciation_issues(text: str) -> List[Dict]:
    """
    Detect words that commonly have pronunciation issues
    
    Args:
        text (str): Input text
        
    Returns:
        List of words with potential pronunciation issues
    """
    issues = []
    words = text.split()
    
    # TH sounds (common for Urdu speakers)
    th_words = [w for w in words if 'th' in w.lower()]
    if th_words:
        issues.append({
            "type": "PRONUNCIATION",
            "pattern": "TH sound",
            "words": th_words[:2],
            "tip": "TH = like between your teeth (think, this, that, with)",
            "severity": "high"
        })
    
    # R sounds (often difficult)
    r_words = [w for w in words if w.lower().startswith('r') or 'r' in w.lower()]
    if r_words:
        issues.append({
            "type": "PRONUNCIATION",
            "pattern": "R sound",
            "words": r_words[:2],
            "tip": "Roll your tongue slightly: 'rahhh' (not rolled R)",
            "severity": "medium"
        })
    
    # W/V distinction
    if any(w.lower().startswith('w') for w in words):
        issues.append({
            "type": "PRONUNCIATION",
            "pattern": "W sound",
            "tip": "W = lips rounded, V = teeth on lip",
            "severity": "low"
        })
    
    return issues

def detect_urdu_words(text: str) -> list:
    """
    Detect Urdu words in mixed text
    
    Args:
        text (str): Mixed English-Urdu text
        
    Returns:
        list: List of Urdu words found
    """
    urdu_words = URDU_PATTERN.findall(text)
    return urdu_words

def detect_language_mix_ratio(text: str) -> Dict[str, float]:
    """
    Calculate the ratio of English to Urdu in text
    
    Args:
        text (str): Mixed text
        
    Returns:
        Dict: Ratio of English and Urdu
    """
    total_chars = len(text.replace(" ", ""))
    urdu_chars = sum(len(word) for word in detect_urdu_words(text))
    english_chars = total_chars - urdu_chars
    
    return {
        "urdu_ratio": urdu_chars / total_chars if total_chars > 0 else 0,
        "english_ratio": english_chars / total_chars if total_chars > 0 else 0,
        "has_urdu": urdu_chars > 0,
        "has_english": english_chars > 0
    }

def extract_learning_context(text: str) -> Dict:
    """
    Extract comprehensive learning context from mixed text
    
    Args:
        text (str): Mixed English-Urdu text
        
    Returns:
        Dict: Context information including error analysis
    """
    urdu_words = detect_urdu_words(text)
    mix_ratio = detect_language_mix_ratio(text)
    grammar_errors = detect_grammar_errors(text)
    pronunciation_issues = detect_pronunciation_issues(text)
    
    # Detect sentence types
    is_question = text.strip().endswith('?')
    is_exclamation = text.strip().endswith('!')
    
    return {
        "urdu_words": urdu_words,
        "mix_ratio": mix_ratio,
        "is_question": is_question,
        "is_exclamation": is_exclamation,
        "text_length": len(text.split()),
        "has_mixed_language": mix_ratio["has_urdu"] and mix_ratio["has_english"],
        "grammar_errors": grammar_errors,
        "pronunciation_issues": pronunciation_issues,
        "error_count": len(grammar_errors) + len(pronunciation_issues)
    }

def suggest_vocabulary(urdu_word: str) -> str:
    """
    Suggest English translation for Urdu word
    
    Args:
        urdu_word (str): Urdu word (transliterated)
        
    Returns:
        str: English equivalent
    """
    return COMMON_PHRASES.get(urdu_word.lower(), None)

def format_error_report(context: Dict) -> str:
    """
    Format error report for display
    
    Args:
        context (Dict): Learning context with errors
        
    Returns:
        str: Formatted error report
    """
    report = ""
    
    if context["grammar_errors"]:
        report += "**Grammar Issues:**\n"
        for error in context["grammar_errors"][:2]:
            report += f"- {error['pattern']}: {error['fix']}\n"
    
    if context["pronunciation_issues"]:
        report += "\n**Pronunciation Tips:**\n"
        for issue in context["pronunciation_issues"][:2]:
            if "words" in issue:
                report += f"- {issue['pattern']} in {issue['words']}: {issue['tip']}\n"
            else:
                report += f"- {issue['tip']}\n"
    
    return report

def validate_input(text: str) -> Tuple[bool, str]:
    """
    Validate user input
    
    Args:
        text (str): User input text
        
    Returns:
        Tuple: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Please type something!"
    
    if len(text) < 3:
        return False, "Too short - write a bit more"
    
    if len(text) > 1000:
        return False, "Too long - keep it under 1000 characters"
    
    return True, ""


# ============ ENHANCED USE CASE FUNCTIONS ============

def analyze_code_switching(text: str) -> Dict:
    """
    Analyze code-switching patterns (Urdu + English mixing)
    Helps provide targeted assistance for mixed language input
    
    Args:
        text (str): Mixed language text
        
    Returns:
        Dict: Analysis of code-switching patterns
    """
    mix_ratio = detect_language_mix_ratio(text)
    urdu_words = detect_urdu_words(text)
    
    # Split text into tokens to find switching points
    tokens = text.split()
    switching_points = []
    prev_lang = None
    
    for token in tokens:
        has_urdu = bool(re.search(r'[\u0600-\u06FF]', token))
        curr_lang = 'urdu' if has_urdu else 'english'
        
        if prev_lang and curr_lang != prev_lang:
            switching_points.append(token)
        prev_lang = curr_lang
    
    return {
        "is_code_switched": mix_ratio["has_urdu"] and mix_ratio["has_english"],
        "urdu_ratio": mix_ratio["urdu_ratio"],
        "english_ratio": mix_ratio["english_ratio"],
        "urdu_words_detected": len(urdu_words),
        "switching_frequency": len(switching_points),
        "urdu_words": urdu_words,
        "switching_pattern": "alternating" if len(switching_points) > 2 else "clustered" if len(switching_points) > 0 else "none"
    }


def suggest_pronunciation_coaching(word: str, word_type: str = "general") -> Dict:
    """
    Generate detailed pronunciation coaching for a specific word
    Helps learners master difficult sounds
    
    Args:
        word (str): The word to coach on
        word_type (str): Type of difficulty (th, r, v, s, general)
        
    Returns:
        Dict: Detailed pronunciation guidance
    """
    word_lower = word.lower()
    coaching = {
        "word": word,
        "syllables": [],
        "phonetic": "",
        "mouth_position": "",
        "practice_sentence": "",
        "difficulty_level": "medium"
    }
    
    # TH sound coaching
    if 'th' in word_lower:
        coaching.update({
            "syllables": ["TH" if 'th' in w else w for w in re.findall(r'th|\w+', word_lower)],
            "phonetic": word_lower.replace('th', 'TH'),
            "mouth_position": "Place your tongue between your teeth. Make a soft hissing sound.",
            "practice_sentence": f"Practice: {word} is an important English sound",
            "difficulty_level": "high",
            "tip": "TH in 'the', 'think', 'that', 'with' - tongue stays between teeth"
        })
    
    # R sound coaching
    elif 'r' in word_lower:
        coaching.update({
            "syllables": re.findall(r'r|\w+', word_lower),
            "phonetic": word_lower,
            "mouth_position": "Slightly roll your tongue. Not heavily rolled like Spanish.",
            "practice_sentence": f"Practice: {word} with a smooth R sound, not rolled",
            "difficulty_level": "high",
            "tip": "Curl your tongue slightly up in your mouth. Say it smoothly."
        })
    
    # W vs V distinction
    elif word_lower.startswith('w'):
        coaching.update({
            "mouth_position": "Round your lips for W sound. Not sharp like V.",
            "practice_sentence": f"Practice: {word} with rounded lips",
            "difficulty_level": "medium",
            "tip": "W = lips rounded and pushed out. V = bite your lower lip gently"
        })
    
    # S sound coaching
    elif 's' in word_lower:
        coaching.update({
            "mouth_position": "Your teeth should be close. Air flows over your teeth.",
            "practice_sentence": f"Practice: {word} with a clear S sound",
            "difficulty_level": "medium",
            "tip": "S = soft hissing sound, not like Urdu 'seen'"
        })
    
    return coaching


def suggest_urdu_to_english_conversion(text: str) -> Dict:
    """
    Suggest natural English equivalent for Urdu/mixed input
    Shows how native speakers would say it
    
    Args:
        text (str): Mixed or Urdu text
        
    Returns:
        Dict: Suggested English conversion with explanation
    """
    code_switching = analyze_code_switching(text)
    
    if not code_switching["is_code_switched"]:
        return {"original": text, "suggestion": text, "is_conversion_needed": False}
    
    # Common Urdu-English patterns and their natural conversions
    urdu_english_patterns = {
        r"main\s+(\w+)\s+gaya": lambda m: f"I went {m.group(1)}",
        r"main\s+(\w+)\s+nahi\s+gaya": lambda m: f"I didn't go {m.group(1)}",
        r"mujhe\s+(\w+)\s+ho\s+rahi\s+hai": lambda m: f"I'm feeling {m.group(1)}",
        r"kya\s+tum\s+(\w+)\s+karte\s+ho": lambda m: f"Do you {m.group(1)}?",
        r"mera\s+(\w+)": lambda m: f"My {m.group(1)}",
        r"tera\s+(\w+)": lambda m: f"Your {m.group(1)}",
        r"kal": "yesterday/tomorrow",
        r"aaj": "today",
        r"haan": "yes",
        r"nahi": "no",
        r"thanak": "tired",
        r"thakan": "tiredness"
    }
    
    return {
        "original": text,
        "has_code_switching": True,
        "urdu_words_count": len(code_switching["urdu_words"]),
        "suggestion": "This is a mix of Urdu and English! Here's how a native speaker would say it naturally...",
        "switching_pattern": code_switching["switching_pattern"],
        "learning_note": "Good mixing! Now let's build your confidence speaking all in English."
    }


def detect_urdu_interference_patterns(text: str) -> List[Dict]:
    """
    Detect grammar mistakes that are likely due to Urdu language interference
    Helps tailor explanations to learner's native language patterns
    
    Args:
        text (str): Input text
        
    Returns:
        List: Urdu interference patterns detected
    """
    patterns = []
    
    # Missing articles (Urdu doesn't have 'a', 'an', 'the')
    if re.search(r'\b(boy|girl|man|woman|book|school|teacher)\s+(?!is|are|have|has|can|will)', text, re.IGNORECASE):
        patterns.append({
            "type": "MISSING_ARTICLE",
            "urdu_interference": "Urdu doesn't use 'a', 'an', or 'the'",
            "example": "I see boy → I see a boy",
            "severity": "medium"
        })
    
    # Object pronoun as subject (Urdu structure: "Mujhe pasand hai" = "To me it is liked")
    if re.search(r'\b(me|him|her|them)\s+(?:is|am|are|like|dislike)', text, re.IGNORECASE):
        patterns.append({
            "type": "OBJECT_PRONOUN_AS_SUBJECT",
            "urdu_interference": "Urdu uses object pronouns where English uses subjects",
            "example": "Me is happy → I am happy",
            "severity": "high"
        })
    
    # Postposition structures (Urdu word order)
    if re.search(r'\b\w+\s+(me|him|her)\s+(in|at|on|from)', text, re.IGNORECASE):
        patterns.append({
            "type": "URDU_WORD_ORDER",
            "urdu_interference": "Urdu word order differs from English",
            "example": "He from India → He is from India",
            "severity": "medium"
        })
    
    # Missing verb 'to be'
    if re.search(r'\b(I|You|He|She|It|We|They)\s+[a-z]+\s+(very|so|quite)', text, re.IGNORECASE):
        patterns.append({
            "type": "MISSING_TO_BE",
            "urdu_interference": "Urdu sometimes omits the equivalent of 'to be'",
            "example": "He very smart → He is very smart",
            "severity": "high"
        })
    
    return patterns


def create_personalized_learning_tip(context: Dict, user_level: str) -> str:
    """
    Create personalized learning tips based on user's patterns and level
    
    Args:
        context (Dict): Learning context from extract_learning_context
        user_level (str): User's learning level (Beginner/Intermediate/Advanced)
        
    Returns:
        str: Personalized learning tip
    """
    tips = []
    
    if context["has_mixed_language"]:
        tips.append("You're mixing Urdu and English! Each time you speak English, your brain is training to think in English. Keep going!")
    
    if context["error_count"] == 0:
        tips.append("Perfect! Your sentence was great. Try adding more details next time.")
    
    if context["error_count"] > 0:
        if user_level == "Beginner":
            tips.append("You're learning! Each mistake helps your brain learn better. Try again, and this time focus on one thing at a time.")
        elif user_level == "Intermediate":
            tips.append("Nice effort! You're connecting ideas well. Just polish a few small things.")
        else:
            tips.append("Almost perfect! Native speakers would say it this way.")
    
    if context["is_question"]:
        tips.append("Great question! Keep asking - that's how you learn.")
    
    return tips[0] if tips else "Keep practicing! Every sentence makes you stronger."


def assess_learning_progress(conversation_history: List[Dict]) -> Dict:
    """
    Assess user's learning progress based on conversation history
    Tracks improvement across grammar, vocabulary, and confidence
    
    Args:
        conversation_history (List[Dict]): List of conversation exchanges
        
    Returns:
        Dict: Progress assessment
    """
    if not conversation_history:
        return {"total_exchanges": 0, "assessment": "Just starting!"}
    
    total_exchanges = len(conversation_history)
    total_errors = sum(len(extract_learning_context(ex.get("user", "")).get("grammar_errors", [])) 
                       for ex in conversation_history if "user" in ex)
    
    avg_errors_per_exchange = total_errors / total_exchanges if total_exchanges > 0 else 0
    
    # Assess progress
    if avg_errors_per_exchange < 0.5:
        assessment = "🎉 Excellent! You're speaking confidently"
    elif avg_errors_per_exchange < 1:
        assessment = "👍 Very good progress! Small improvements coming"
    elif avg_errors_per_exchange < 2:
        assessment = "✅ Good effort! Keep practicing"
    else:
        assessment = "💪 You're learning! Each try gets better"
    
    return {
        "total_exchanges": total_exchanges,
        "total_errors_detected": total_errors,
        "avg_errors_per_exchange": round(avg_errors_per_exchange, 2),
        "assessment": assessment,
        "trending": "improving" if total_exchanges > 3 and total_errors < 5 else "developing"
    }


# ============ ROLEPLAY SCENARIOS (Use Case 6) ============

ROLEPLAY_SCENARIOS = {
    "Restaurant": {
        "title": "Ordering Food at a Restaurant",
        "description": "Practice ordering food, asking about dishes, and making reservations",
        "ai_character": "A friendly restaurant server who is attentive and helpful",
        "opening_prompt": "Welcome! What can I get started for you today?",
        "vocabulary": ["menu", "special", "recommendation", "allergies", "reservation", "bill/check"]
    },
    "Job Interview": {
        "title": "Job Interview",
        "description": "Practice answering interview questions confidently",
        "ai_character": "A professional recruiter conducting a job interview",
        "opening_prompt": "Tell me about yourself and why you're interested in this position.",
        "vocabulary": ["experience", "skills", "strengths", "challenge", "team", "goals"]
    },
    "Directions": {
        "title": "Asking for Directions",
        "description": "Learn to ask and give directions, understand landmarks",
        "ai_character": "A helpful local who knows the area well",
        "opening_prompt": "Hi there! Are you looking for something? I can help you find your way.",
        "vocabulary": ["left", "right", "straight", "intersection", "block", "landmark"]
    },
    "Doctor": {
        "title": "Visiting a Doctor",
        "description": "Practice describing symptoms and medical concerns",
        "ai_character": "A caring doctor who listens carefully",
        "opening_prompt": "What seems to be the problem? Can you describe your symptoms?",
        "vocabulary": ["symptom", "pain", "fever", "prescription", "medicine", "appointment"]
    },
    "Bank": {
        "title": "Bank Services",
        "description": "Learn banking vocabulary and transactions",
        "ai_character": "A professional bank officer",
        "opening_prompt": "Good morning. How can I help you with your banking needs today?",
        "vocabulary": ["account", "deposit", "withdrawal", "transfer", "balance", "statement"]
    },
    "School": {
        "title": "School Presentation",
        "description": "Practice giving presentations and speaking confidently",
        "ai_character": "Your teacher or classmates listening to your presentation",
        "opening_prompt": "Alright class, let's hear your presentation! You have the floor.",
        "vocabulary": ["topic", "main point", "conclusion", "question", "audience", "slide"]
    },
    "Friend Chat": {
        "title": "Casual Chat with a Foreign Friend",
        "description": "Have a relaxed conversation about life, interests, culture",
        "ai_character": "A friendly person from another country who's curious about your life",
        "opening_prompt": "Hey! How's everything going with you? What have you been up to?",
        "vocabulary": ["hobby", "weekend", "experience", "culture", "tradition", "interest"]
    }
}


def get_roleplay_scenario(scenario_name: str) -> Dict:
    """
    Get roleplay scenario details
    
    Args:
        scenario_name (str): Name of the scenario
        
    Returns:
        Dict: Scenario details with character and vocabulary
    """
    return ROLEPLAY_SCENARIOS.get(scenario_name, ROLEPLAY_SCENARIOS["Restaurant"])


def get_all_roleplay_scenarios() -> List[str]:
    """Get list of all available roleplay scenarios"""
    return list(ROLEPLAY_SCENARIOS.keys())


# ============ VOCABULARY EXPANSION (Use Case 8) ============

VOCABULARY_SYNONYMS = {
    "happy": ["delighted", "joyful", "cheerful", "content", "pleased", "thrilled"],
    "sad": ["unhappy", "sorrowful", "gloomy", "melancholy", "down", "blue"],
    "big": ["large", "huge", "enormous", "vast", "immense", "spacious"],
    "small": ["tiny", "little", "compact", "miniature", "petite", "diminutive"],
    "good": ["excellent", "great", "wonderful", "fantastic", "superb", "outstanding"],
    "bad": ["poor", "terrible", "awful", "dreadful", "disappointing", "inferior"],
    "tired": ["exhausted", "fatigued", "weary", "drained", "sleepy", "worn out"],
    "hungry": ["starving", "famished", "ravenous", "peckish"],
    "beautiful": ["gorgeous", "stunning", "lovely", "exquisite", "attractive", "radiant"],
    "ugly": ["unattractive", "unsightly", "hideous", "repulsive", "unpleasant"],
    "smart": ["intelligent", "clever", "bright", "sharp", "brilliant", "astute"],
    "stupid": ["foolish", "dumb", "silly", "dim", "unintelligent"],
    "angry": ["furious", "enraged", "livid", "irate", "irritated", "annoyed"],
    "scared": ["frightened", "terrified", "afraid", "nervous", "anxious", "panicked"],
    "cold": ["chilly", "freezing", "frigid", "icy", "cool"],
    "hot": ["burning", "scorching", "boiling", "sweltering", "warm"],
}


def suggest_vocabulary_alternatives(word: str) -> Dict:
    """
    Suggest better vocabulary alternatives in context
    Helps learners expand vocabulary naturally
    
    Args:
        word (str): The word to find alternatives for
        
    Returns:
        Dict: Alternatives with definitions hints
    """
    word_lower = word.lower()
    
    if word_lower in VOCABULARY_SYNONYMS:
        alternatives = VOCABULARY_SYNONYMS[word_lower]
        return {
            "original_word": word,
            "alternatives": alternatives,
            "tip": f"These words have similar meanings to '{word}' but some are stronger!",
            "suggestion": f"You could also say you're {alternatives[0]}, {alternatives[1]}, or {alternatives[2]}!",
            "found": True
        }
    
    # Generic suggestion if not in dictionary
    return {
        "original_word": word,
        "alternatives": [],
        "found": False,
        "suggestion": f"Great word! '{word}' is perfect here."
    }


# ============ FLUENCY & ACCENT TRAINING (Use Case 9) ============

STRESS_PATTERNS = {
    "happiness": "HAP-pi-ness (stress first syllable)",
    "important": "im-POR-tant (stress second syllable)",
    "photograph": "PHO-to-graph (stress first syllable)",
    "information": "in-for-MA-tion (stress third syllable)",
    "different": "DIF-fer-ent (stress first syllable)",
    "interesting": "IN-ter-est-ing (stress first syllable)",
}


def suggest_fluency_coaching(sentence: str) -> Dict:
    """
    Provide fluency and accent training guidance
    Teaches rhythm, stress, and chunking
    
    Args:
        sentence (str): The sentence to analyze
        
    Returns:
        Dict: Fluency coaching tips
    """
    words = sentence.lower().split()
    
    coaching = {
        "original": sentence,
        "chunking_suggestion": "",
        "stress_tips": [],
        "rhythm_tip": "",
        "practice_slowly": ""
    }
    
    # Suggest natural chunking
    if len(words) > 5:
        coaching["chunking_suggestion"] = "Break this into 2-3 chunks:\n"
        # Simple chunking by comma or natural pause points
        mid = len(words) // 2
        chunk1 = " ".join(words[:mid])
        chunk2 = " ".join(words[mid:])
        coaching["chunking_suggestion"] += f"  1. '{chunk1}'\n  2. '{chunk2}'"
        coaching["rhythm_tip"] = "Don't rush! Say each chunk, pause briefly, then continue."
    
    # Check for words with stress patterns
    stress_words = [w for w in words if w in STRESS_PATTERNS]
    if stress_words:
        coaching["stress_tips"] = [STRESS_PATTERNS[w] for w in stress_words[:2]]
    
    # Practice suggestion
    coaching["practice_slowly"] = f"Say it slowly: '{sentence}'\nNow faster, keeping the same rhythm."
    
    return coaching


# ============ STORYTELLING PRACTICE (Use Case 10) ============

STORYTELLING_PROMPTS = [
    "What did you do yesterday? Tell me the story from morning to evening.",
    "Describe your dream vacation. Where would you go and what would you do?",
    "Tell me a childhood memory that makes you smile.",
    "What's an interesting experience you had recently?",
    "Describe your favorite person and why they're special to you.",
    "Tell me about a time you felt proud of yourself.",
    "What's your favorite holiday? Describe how you celebrate it.",
    "Tell me about your family. Who are the key people and what are they like?",
    "Describe a challenge you faced and how you overcame it.",
    "What's your biggest dream and why do you want to achieve it?"
]


def get_storytelling_prompt() -> str:
    """Get a random storytelling prompt"""
    import random
    return random.choice(STORYTELLING_PROMPTS)


def analyze_story_quality(story_text: str) -> Dict:
    """
    Analyze the quality of a user's story
    Shows what they did well and areas for improvement
    
    Args:
        story_text (str): The story told by the user
        
    Returns:
        Dict: Story quality analysis
    """
    words = story_text.split()
    sentences = re.split(r'[.!?]+', story_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Analyze story elements
    analysis = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
        "strengths": [],
        "improvements": [],
        "overall_assessment": ""
    }
    
    # Check for varied vocabulary
    unique_words = len(set(words))
    vocab_ratio = unique_words / len(words) if words else 0
    
    if vocab_ratio > 0.6:
        analysis["strengths"].append("Great vocabulary variety!")
    else:
        analysis["improvements"].append("Try using different words - avoid repeating the same ones.")
    
    # Check for story length
    if len(words) < 30:
        analysis["improvements"].append("Make your story longer - add more details!")
    elif len(words) > 150:
        analysis["strengths"].append("Excellent detail and length!")
    
    # Check for punctuation/structure
    if len(sentences) < 2:
        analysis["improvements"].append("Break your story into multiple sentences.")
    else:
        analysis["strengths"].append("Nice use of sentence structure!")
    
    # Check for emotion/description
    emotion_words = ["felt", "was", "excited", "happy", "sad", "beautiful", "amazing", "incredible"]
    has_emotion = any(word in story_text.lower() for word in emotion_words)
    
    if has_emotion:
        analysis["strengths"].append("Great use of feelings and description!")
    else:
        analysis["improvements"].append("Add more emotion or description to make your story more engaging.")
    
    # Generate overall assessment
    strength_count = len(analysis["strengths"])
    if strength_count >= 3:
        analysis["overall_assessment"] = "🌟 Excellent storytelling! Your story has great details and emotion."
    elif strength_count >= 2:
        analysis["overall_assessment"] = "✅ Good job! Your story is clear and engaging. Keep adding more details!"
    else:
        analysis["overall_assessment"] = "💪 Nice start! With more description and emotion, your stories will be amazing!"
    
    return analysis


def refine_story(story_text: str) -> Dict:
    """
    Provide refined version and teaching suggestions
    
    Args:
        story_text (str): Original story
        
    Returns:
        Dict: Refined suggestions and teaching points
    """
    analysis = analyze_story_quality(story_text)
    
    return {
        "original_story": story_text,
        "analysis": analysis,
        "teaching_points": analysis["improvements"],
        "praise": analysis["strengths"],
        "next_step": "Try telling another story and add more detail next time!",
        "vocabulary_opportunities": "Look for places where you can use stronger, more descriptive words."
    }


# ============ JOB INTERVIEW PREPARATION (Use Case 12) ============

INTERVIEW_QUESTIONS = [
    {
        "question": "Tell me about yourself",
        "tips": [
            "Start with your background/current role",
            "Mention 2-3 key skills or achievements",
            "Connect to why you want this job",
            "Keep it 1-2 minutes"
        ],
        "poor_example": "um... i am working... and i like... many things are good about me...",
        "good_example": "I'm currently working as a software developer. I have 5 years of experience in web development, and I'm passionate about creating user-friendly applications. I'm excited about this opportunity because your company aligns with my goals of building innovative solutions."
    },
    {
        "question": "Why should we hire you?",
        "tips": [
            "Highlight unique skills that match the job",
            "Give a specific achievement or example",
            "Show understanding of company/role",
            "Be confident but humble"
        ],
        "poor_example": "because i am good person and i work hard",
        "good_example": "You should hire me because I bring both technical expertise and proven leadership skills. In my previous role, I led a team of 8 developers and delivered projects 20% ahead of schedule. I'm specifically interested in your company because of your commitment to innovation, and I believe my experience aligns perfectly with your needs."
    },
    {
        "question": "What are your strengths?",
        "tips": [
            "Choose 2-3 relevant strengths",
            "Back each up with an example or story",
            "Make it specific to the job",
            "Avoid generic answers"
        ],
        "poor_example": "my strengths are that i am nice, and working",
        "good_example": "My key strengths are problem-solving and communication. For example, I recently resolved a complex technical issue that was blocking the team by breaking it into smaller parts and collaborating with colleagues. I also excel at explaining technical concepts to non-technical stakeholders, which has helped streamline our project planning."
    },
    {
        "question": "What is your biggest weakness?",
        "tips": [
            "Choose a real but manageable weakness",
            "Show awareness and improvement efforts",
            "Connect it to learning and growth",
            "Don't say 'I'm a perfectionist'!"
        ],
        "poor_example": "i have many weaknesses, i am not good with anything",
        "good_example": "I tend to take on too many projects at once, which sometimes affects my focus. However, I've learned to manage this by prioritizing better and saying no when needed. Now I use project management tools and set clear deadlines for myself, which has significantly improved my productivity."
    },
    {
        "question": "Describe a challenge you overcome",
        "tips": [
            "Use the STAR method: Situation, Task, Action, Result",
            "Show problem-solving skills",
            "Highlight teamwork if relevant",
            "End with concrete results"
        ],
        "poor_example": "one time something was difficult and i fix it",
        "good_example": "In my previous role, our team was struggling with project delays. I identified that our communication between departments was the issue. I proposed and led the implementation of a weekly sync meeting with clear agendas. As a result, we reduced project delays by 40% and improved team morale significantly."
    }
]


def get_interview_question(index: int = None) -> Dict:
    """
    Get an interview question with tips and examples
    
    Args:
        index (int): Optional specific question index (0-4)
        
    Returns:
        Dict: Interview question with tips and examples
    """
    if index is not None and 0 <= index < len(INTERVIEW_QUESTIONS):
        return INTERVIEW_QUESTIONS[index]
    
    import random
    return random.choice(INTERVIEW_QUESTIONS)


def improve_interview_response(user_response: str, question: str = None) -> Dict:
    """
    Analyze and improve an interview response
    
    Args:
        user_response (str): User's interview answer
        question (str): The interview question asked
        
    Returns:
        Dict: Analysis and improved version
    """
    words = user_response.split()
    sentences = re.split(r'[.!?]+', user_response)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    improvement = {
        "original": user_response,
        "length_feedback": "",
        "structure_feedback": "",
        "tone_feedback": "",
        "strengths": [],
        "improvements": [],
        "professional_version": ""
    }
    
    # Check length
    word_count = len(words)
    if word_count < 20:
        improvement["length_feedback"] = "⚠️ Too short! Add more detail and examples."
        improvement["improvements"].append("Expand your answer - aim for 5-7 sentences")
    elif word_count > 150:
        improvement["length_feedback"] = "⚠️ Too long! Keep it concise."
        improvement["improvements"].append("Trim unnecessary details - aim for 30-80 words")
    else:
        improvement["length_feedback"] = "✅ Good length!"
        improvement["strengths"].append("Appropriate length for an interview")
    
    # Check structure
    if len(sentences) < 2:
        improvement["structure_feedback"] = "⚠️ Add more sentences for better structure."
        improvement["improvements"].append("Break into multiple sentences for clarity")
    else:
        improvement["structure_feedback"] = "✅ Good sentence variety!"
        improvement["strengths"].append("Good sentence structure")
    
    # Check for confidence indicators
    hesitation_words = ["um", "uh", "like", "i think", "maybe", "perhaps", "i guess"]
    has_hesitation = any(word in user_response.lower() for word in hesitation_words)
    
    if has_hesitation:
        improvement["tone_feedback"] = "⚠️ Remove filler words for more confidence."
        improvement["improvements"].append("Remove 'um', 'like', 'maybe' - sound more confident")
    else:
        improvement["tone_feedback"] = "✅ Confident tone!"
        improvement["strengths"].append("Confident, clear tone")
    
    # Check for specific examples
    specific_words = ["example", "specific", "achieved", "accomplished", "delivered", "led", "managed"]
    has_examples = any(word in user_response.lower() for word in specific_words)
    
    if not has_examples:
        improvement["improvements"].append("Add a specific example or achievement")
    else:
        improvement["strengths"].append("Includes specific examples")
    
    # Generate professional version (basic template)
    improvement["professional_version"] = (
        "Strong answer! Here's a more professional version:\n\n"
        f"[Start with your current situation]\n"
        f"{user_response[:50]}...\n"
        f"[Add specific achievement]\n"
        f"[Connect to the role/company]\n"
        f"[End on confident, forward-looking note]"
    )
    
    return improvement


# ============ INSTANT "BETTER SENTENCE SUGGESTIONS" MODE (Use Case 13) ============

def generate_sentence_versions(sentence: str) -> Dict:
    """
    Generate three versions of a sentence at different English levels
    
    Args:
        sentence (str): User's sentence
        
    Returns:
        Dict: Simple, natural, and professional versions with explanations
    """
    words = sentence.split()
    
    versions = {
        "original": sentence,
        "simple": {
            "version": sentence,  # Placeholder - would be generated
            "explanation": "Uses basic grammar and common words",
            "use_case": "Great for beginners, everyday casual chat",
            "examples": [
                "Use 'big' instead of 'substantial'",
                "Use 'important' instead of 'significant'",
                "Use 'good' instead of 'excellent'"
            ]
        },
        "natural": {
            "version": sentence,  # Placeholder
            "explanation": "Natural, spoken English - how native speakers talk",
            "use_case": "Perfect for daily conversations, informal settings",
            "examples": [
                "Use contractions: 'I'm' instead of 'I am'",
                "Use phrases: 'kind of' instead of 'somewhat'",
                "Use casual expressions: 'pretty good' instead of 'quite good'"
            ]
        },
        "professional": {
            "version": sentence,  # Placeholder
            "explanation": "Formal, professional English for business/formal settings",
            "use_case": "Interviews, presentations, formal writing",
            "examples": [
                "Use 'I would' instead of 'I'll'",
                "Use 'facilitate' instead of 'help with'",
                "Use 'regarding' instead of 'about'"
            ]
        },
        "learning_points": []
    }
    
    # Analyze the sentence to generate learning points
    if len(words) > 0:
        # Check for contractions
        if "'m" in sentence or "'re" in sentence or "'ve" in sentence:
            versions["learning_points"].append({
                "point": "Contractions found - perfect for natural English!",
                "formal_version": sentence.replace("'m", " am").replace("'re", " are")
            })
        
        # Check for professional markers
        professional_words = ["therefore", "furthermore", "regarding", "facilitate", "leverage", "synergy"]
        has_professional = any(word in sentence.lower() for word in professional_words)
        if has_professional:
            versions["learning_points"].append({
                "point": "Professional vocabulary detected - great for business English!",
                "casual_version": "Replace with simpler alternatives for natural English"
            })
        
        # Check for passive voice
        if "is" in sentence.lower() and "by" in sentence.lower():
            versions["learning_points"].append({
                "point": "Passive voice detected",
                "tip": "In casual English, active voice is more natural"
            })
    
    return versions


def improve_sentence_to_levels(sentence: str) -> Dict:
    """
    Improve a sentence and show it at all three levels
    
    Args:
        sentence (str): User's sentence
        
    Returns:
        Dict: Improved versions at simple, natural, and professional levels
    """
    # Generate basic improvements at each level
    improvements = {
        "original": sentence,
        "analysis": {
            "word_count": len(sentence.split()),
            "complexity": "moderate",  # Would be calculated
            "errors": []  # Would be populated
        },
        "levels": {
            "simple": {
                "version": sentence,
                "changes": ["Use basic words", "Keep sentences short"],
                "good_for": "Learning basics, speaking with children"
            },
            "natural": {
                "version": sentence,
                "changes": ["Use contractions", "Sound relaxed", "Use common phrases"],
                "good_for": "Everyday chat, making friends, casual situations"
            },
            "professional": {
                "version": sentence,
                "changes": ["Formal structure", "Professional vocabulary", "Complete sentences"],
                "good_for": "Job interviews, presentations, formal writing"
            }
        },
        "tips": {
            "for_learning": "Practice the natural version first - that's how real people speak!",
            "when_to_use": {
                "simple": "With beginners or very young people",
                "natural": "With friends, colleagues, most situations",
                "professional": "In interviews, formal meetings, official writing"
            }
        }
    }
    
    return improvements


# ============ EMOTIONAL CONVERSATION PARTNER (Use Case 14) ============

# Comprehensive Urdu emotional expressions mapped to English
URDU_EMOTIONAL_EXPRESSIONS = {
    # Stress/Worry
    "tension": "stress/anxiety",
    "mujhe tension ho rahi hai": "I'm feeling really stressed/anxious",
    "tension ho gaya": "I'm stressed out",
    "fikir": "worry/concern",
    "mujhe fikir hai": "I'm worried",
    "par tu mat kar": "don't worry",
    "tension mat ley": "don't stress about it",
    
    # Happiness/Joy
    "khush": "happy",
    "main khush hoon": "I'm really happy",
    "bahot khush": "very happy/excited",
    "khushi": "happiness/joy",
    "mujhe khushi hai": "I'm so happy",
    "bash": "wonderful/great",
    "wah": "wow!/great!",
    
    # Sadness/Disappointment
    "uday": "sad/upset",
    "main utay hoon": "I'm sad",
    "dukh": "sorrow/sadness",
    "mujhe dukh hua": "It made me sad",
    "toota hua": "broken/devastated",
    "bura laga": "felt bad/hurt",
    "disappointment": "let down",
    
    # Anger/Frustration
    "gussa": "anger",
    "main gussa ho gaya": "I'm angry",
    "bahot gussa": "very angry/furious",
    "irritated": "annoyed",
    "frustrated": "frustrated",
    "mujhe gussa dilwaya": "made me angry",
    "uttej": "aggressive/agitated",
    
    # Fear/Nervousness
    "dar": "fear",
    "mujhe dar hai": "I'm afraid/scared",
    "ghab raha hoon": "I'm nervous",
    "ghabi": "nervous/anxious",
    "takleef": "discomfort/unease",
    "darr laga": "got scared",
    
    # Love/Affection
    "pyar": "love",
    "mujhe pyar hai": "I love",
    "piyara": "dear/beloved",
    "mohabbat": "love/affection",
    "pasand": "like/love",
    "mujhe pasand hai": "I like/love",
    
    # Confidence/Pride
    "garwida": "proud",
    "mujhe garwida hoon": "I'm proud",
    "himmat": "courage",
    "himmat hay": "I have courage",
    "capable": "able/confident",
    
    # Shame/Embarrassment
    "sharam": "shame/embarrassment",
    "mujhe sharam aai": "I felt embarrassed",
    "sharminda": "ashamed",
    "badmashi": "wrongdoing",
    
    # Confusion
    "confuse": "confused",
    "samaj nai aya": "didn't understand",
    "mixed up": "mixed up",
    "mushkil": "difficult/confusing",
}

# Additional emotional context converters
URDU_EMOTIONAL_CONTEXTS = {
    "beta/beti": "son/daughter",  # Term of endearment or actual relation
    "jan": "dear (term of endearment)",
    "habibi": "my love",
    "tum": "you (intimate/casual)",
    "aap": "you (formal/respectful)",
    "haan": "yes (affirmative)",
    "nahi": "no",
    "bilkul": "absolutely/definitely",
    "thik hai": "okay/alright",
    "shukriya": "thank you",
    "koi baat nahi": "it's okay/no problem",
}


def detect_urdu_emotion(text: str) -> Dict:
    """
    Detect Urdu emotional expressions and convert to expressive English
    
    Args:
        text (str): User's input containing Urdu expressions
        
    Returns:
        Dict: Detected emotions and English conversions
    """
    text_lower = text.lower()
    
    emotion_detection = {
        "original": text,
        "detected_emotions": [],
        "emotional_english": "",
        "expression_analysis": [],
        "intensity_level": "moderate",
        "learning_opportunity": ""
    }
    
    # Detect emotions
    for urdu_phrase, emotion in URDU_EMOTIONAL_EXPRESSIONS.items():
        if urdu_phrase.lower() in text_lower:
            emotion_detection["detected_emotions"].append({
                "urdu": urdu_phrase,
                "english_translation": emotion,
                "type": classify_emotion_type(emotion)
            })
    
    # Detect context (informal vs formal)
    for context_word, meaning in URDU_EMOTIONAL_CONTEXTS.items():
        if context_word.lower() in text_lower:
            emotion_detection["expression_analysis"].append({
                "context_word": context_word,
                "meaning": meaning,
                "tone": "formal" if context_word == "aap" else "casual"
            })
    
    # Determine intensity
    intensity_markers = {
        "bahot": "high",
        "bohat": "high",
        "main": "high",
        "bohot": "high",
        "thora": "low",
        "thodi": "low",
    }
    
    for marker, intensity in intensity_markers.items():
        if marker in text_lower:
            emotion_detection["intensity_level"] = intensity
    
    # Generate emotional English translation
    if emotion_detection["detected_emotions"]:
        emotions_list = [e["english_translation"] for e in emotion_detection["detected_emotions"]]
        emotion_detection["emotional_english"] = (
            f"You're expressing: {', '.join(emotions_list)}\n\n"
            f"In expressive English: \"{build_emotional_english(text, emotion_detection['detected_emotions'])}\""
        )
        
        emotion_detection["learning_opportunity"] = (
            "Great emotional expression! You used native vocabulary to express feelings. "
            "Here's how to say it in expressive English for native speakers:"
        )
    
    return emotion_detection


def classify_emotion_type(emotion_text: str) -> str:
    """Classify emotion as positive, negative, or neutral"""
    emotion_lower = emotion_text.lower()
    
    positive = ["happy", "love", "proud", "joy", "excited", "confident"]
    negative = ["sad", "angry", "fear", "scared", "stressed", "anxious", "worried", "disappointed"]
    
    if any(word in emotion_lower for word in positive):
        return "positive"
    elif any(word in emotion_lower for word in negative):
        return "negative"
    else:
        return "neutral"


def build_emotional_english(urdu_text: str, emotions: List[Dict]) -> str:
    """
    Build an emotionally expressive English sentence
    
    Args:
        urdu_text (str): Original Urdu text
        emotions (List[Dict]): Detected emotions
        
    Returns:
        str: Emotionally expressive English sentence
    """
    if not emotions:
        return "I'm expressing feelings."
    
    # Get the primary emotion
    primary_emotion = emotions[0]["english_translation"]
    
    # Map to expressive English phrases
    emotional_phrases = {
        "stress/anxiety": "I'm feeling really overwhelmed and stressed right now.",
        "happy": "I'm feeling so happy and excited!",
        "sadness": "I'm feeling really sad and down.",
        "anger": "I'm feeling quite frustrated and angry.",
        "fear/scared": "I'm feeling anxious and a bit scared.",
        "love": "I really care about this.",
        "proud": "I'm feeling really proud of myself!",
        "nervous": "I'm feeling a bit nervous.",
        "confused": "I'm feeling confused and uncertain.",
    }
    
    # Return matching phrase or generate generic
    for emotion_type, phrase in emotional_phrases.items():
        if emotion_type in primary_emotion.lower():
            return phrase
    
    return f"I'm feeling quite {primary_emotion}."


def suggest_emotional_vocabulary(urdu_emotion: str) -> Dict:
    """
    Suggest multiple English expressions for an emotion
    
    Args:
        urdu_emotion (str): Urdu emotional expression
        
    Returns:
        Dict: Multiple English expressions at different intensity levels
    """
    suggestion = {
        "urdu_original": urdu_emotion,
        "emotion_type": "",
        "english_versions": {
            "subtle": "",
            "moderate": "",
            "intense": "",
        },
        "usage_tips": []
    }
    
    # Map to emotion type and intensity levels
    emotion_mapping = {
        "tension": {
            "type": "Stress/Anxiety",
            "subtle": "I'm a bit concerned about this.",
            "moderate": "I'm feeling stressed.",
            "intense": "I'm absolutely overwhelmed right now!"
        },
        "khush": {
            "type": "Happiness",
            "subtle": "I'm quite content.",
            "moderate": "I'm really happy!",
            "intense": "I'm over the moon! Absolutely thrilled!"
        },
        "uday": {
            "type": "Sadness",
            "subtle": "I'm feeling a bit down.",
            "moderate": "I'm sad and disappointed.",
            "intense": "I'm devastated. Completely heartbroken."
        },
        "gussa": {
            "type": "Anger",
            "subtle": "I'm mildly frustrated.",
            "moderate": "I'm quite angry about this.",
            "intense": "I'm absolutely furious! This is infuriating!"
        },
    }
    
    # Find matching emotion
    for key, mapping in emotion_mapping.items():
        if key in urdu_emotion.lower():
            suggestion["emotion_type"] = mapping["type"]
            suggestion["english_versions"] = {
                "subtle": mapping["subtle"],
                "moderate": mapping["moderate"],
                "intense": mapping["intense"],
            }
            suggestion["usage_tips"] = [
                f"Use subtle version for mild feelings",
                f"Use moderate version for normal conversations",
                f"Use intense version when you really feel it strongly",
                f"Native speakers often use intensifiers: 'absolutely', 'really', 'so'"
            ]
            break
    
    return suggestion


def detect_input_type(text: str) -> Dict[str, str]:
    """
    Detect the input type from user message.
    
    Returns one of 7 types:
    - "pure_urdu": Primarily Urdu text
    - "mixed_urdu_english": Urdu + English mixed
    - "broken_english": English with grammar errors
    - "correct_english": Grammatically correct English
    - "pronunciation_request": Asking how to pronounce something
    - "free_conversation": General conversation
    - "emotional_personal": Personal/emotional content (often Urdu)
    
    Args:
        text (str): User input text
        
    Returns:
        Dict with "input_type" and "confidence" (0-1 score)
    """
    
    if not text or len(text.strip()) < 2:
        return {"input_type": "free_conversation", "confidence": 0.5}
    
    text_lower = text.lower().strip()
    
    # Check for pronunciation request patterns (highest priority)
    pronunciation_keywords = [
        "pronounce", "pronunciation", "how to say", "say this", "how do i say",
        "rhyme", "sound", "syllable", "stress", "accent", "phonetic"
    ]
    for keyword in pronunciation_keywords:
        if keyword in text_lower:
            return {"input_type": "pronunciation_request", "confidence": 0.95}
    
    # Analyze language composition
    urdu_matches = URDU_PATTERN.findall(text)
    urdu_count = len(urdu_matches)
    urdu_ratio = len(''.join(urdu_matches)) / len(text) if text else 0
    
    # Extract words (English-like tokens)
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    english_word_count = len(words)
    total_chars = len(text)
    
    # Check for emotional/personal markers
    emotional_keywords = [
        "feel", "sad", "happy", "angry", "scared", "worried", "excited",
        "frustrated", "confused", "nervous", "anxious", "love", "hate",
        "like", "dislike", "enjoy", "suffer", "pain", "hurt", "dear",
        "miss", "want", "hope", "fear", "khush", "gussa", "dar", "tension",
        "problem", "help", "tired", "exhausted", "overwhelm"
    ]
    has_emotional = any(keyword in text_lower for keyword in emotional_keywords)
    
    # Detect grammar errors (simple patterns)
    error_patterns = [
        r'\bi\s+(?:is|are|was|were|am|have)',  # "I is", "I are"
        r'\b(?:he|she|it)\s+(?:are|am)',        # "he are", "she am"
        r'\b(?:you|we|they)\s+(?:is)',          # "you is", "we is"
        r'\bgo\s+(?:yesterday|last|tomorrow)',   # "go yesterday"
        r'\b(?:he|she|it)\s+go\b',              # "he go"
        r'\b(?:not|don\'?t|doesn\'?t)\s+\w+ing', # "not going" (should be "not going to")
    ]
    
    error_count = 0
    for pattern in error_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            error_count += 1
    
    # Decision logic based on composition
    
    # TYPE 1: Pure Urdu (>70% Urdu characters)
    if urdu_ratio > 0.7 and english_word_count < 5:
        confidence = min(0.95, 0.7 + (urdu_ratio * 0.25))
        return {"input_type": "pure_urdu", "confidence": confidence}
    
    # TYPE 2: Mixed Urdu + English (15-70% Urdu + significant English)
    if urdu_ratio > 0.15 and urdu_ratio <= 0.7 and english_word_count >= 3:
        confidence = min(0.95, 0.85)
        return {"input_type": "mixed_urdu_english", "confidence": confidence}
    
    # TYPE 7: Emotional/Personal (mostly English but with emotional markers)
    if has_emotional and english_word_count >= 5:
        # Could be pure Urdu emotions too
        if urdu_ratio > 0.2:
            return {"input_type": "emotional_personal", "confidence": 0.90}
        # Or English emotional input
        return {"input_type": "emotional_personal", "confidence": 0.75}
    
    # TYPE 3: Broken English (>0 grammar errors + mostly English)
    if error_count > 0 and english_word_count >= 3 and urdu_ratio < 0.15:
        confidence = min(0.95, 0.6 + (error_count * 0.15))
        return {"input_type": "broken_english", "confidence": confidence}
    
    # TYPE 4: Correct English (English, few/no errors)
    if english_word_count >= 3 and urdu_ratio < 0.1 and error_count == 0:
        confidence = 0.85
        return {"input_type": "correct_english", "confidence": confidence}
    
    # TYPE 6: Free Conversation (anything else with English)
    if english_word_count >= 2:
        confidence = 0.70
        return {"input_type": "free_conversation", "confidence": confidence}
    
    # Default: Free conversation
    return {"input_type": "free_conversation", "confidence": 0.5}


# Example usage
if __name__ == "__main__":
    # Test mixed text
    test_cases = [
        "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain",
        "i is going to the school",
        "He are very smart and nice person"
    ]
    
    for test_text in test_cases:
        print(f"\nAnalyzing: {test_text}")
        context = extract_learning_context(test_text)
        print(f"Grammar Errors: {len(context['grammar_errors'])}")
        print(f"Pronunciation Issues: {len(context['pronunciation_issues'])}")
        print(context)
