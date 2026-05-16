# 📖 Usage Guide - English Learning Assistant

## Overview

This application helps English learners practice their English by:
1. **Processing mixed English-Urdu text** (code-switching)
2. **Providing intelligent corrections** with explanations
3. **Offering personalized feedback** based on learning level
4. **Tracking learning progress** over time

## Getting Started

### Launch the Application

**In PowerShell:**
```powershell
cd "c:\Users\Tech Mehal\Desktop\English\english_learning_app"
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

The app opens at: `http://localhost:8501`

## Interface Overview

### 1. Sidebar Configuration

#### API Keys
- **Gemini API Key:** Paste your Gemini API key here
- **Groq API Key:** Paste your Groq API key here

#### Select AI Model
- **Gemini:** Great for detailed explanations
- **Groq:** Very fast responses

#### English Level
- **Beginner:** A1-A2 (basic English)
- **Intermediate:** B1-B2 (intermediate proficiency)
- **Advanced:** C1-C2 (advanced proficiency)

#### Focus Areas (Select Multiple)
- **Grammar** - Sentence structure, tenses
- **Vocabulary** - New words and phrases
- **Pronunciation** - How to pronounce words
- **Conversation** - Natural dialogues
- **Writing** - Written expression

### 2. Main Input Area

**Your Input Section:**
- Text area for entering mixed English-Urdu text
- **"Get Correction & Explanation"** button
- Results appear below

### 3. Learning History

- View all previous exchanges
- Track your learning progress
- See patterns in your mistakes

## Usage Examples

### Example 1: Zoo (Given Example)

**Your Input:**
```
I am going to.....ohh usy kia kahty hain jha par janwar hoty hain
```

**AI Response:**
```
CORRECTION: I think you are going to the zoo

EXPLANATION: In English, we use "the zoo" (with the definite article) 
when referring to a specific place where animals are kept. The phrase 
"jha par janwar hoty hain" (where animals are) translates to "zoo" in English.

EXAMPLE: "Are you going to the zoo this weekend?"

LEARNING TIP: In English, we often use definite articles (the) before 
place nouns. Compare: "I'm going to school" vs "I'm going to the zoo"
```

---

### Example 2: Self-Introduction

**Your Input:**
```
Mera naam Ahmed hai, I am 25 years old, aur mein engineer hoon
```

**AI Response:**
```
CORRECTION: My name is Ahmed, I am 25 years old, and I am an engineer

EXPLANATION: 
- Add "My" before "name" (possessive pronoun)
- Use "an" before "engineer" (vowel sound)
- Use "I am" instead of "mein hoon" for consistency

EXAMPLE: "My name is Ahmed. I am an engineer."

LEARNING TIP: Articles (a/an) come before professions: 
"I am a teacher" (consonant sound)
"I am an engineer" (vowel sound)
```

---

### Example 3: Daily Activity

**Your Input:**
```
Main subah 7 baje uthta hoon, phir coffee pita hoon, then I go office
```

**AI Response:**
```
CORRECTION: I wake up at 7 AM in the morning. Then I drink coffee. 
After that, I go to the office.

EXPLANATION:
- "Main subah uthta hoon" → "I wake up in the morning"
- Time: Use "at" with specific times (at 7 AM)
- "Then" is better than "phir" - use English throughout when possible
- "go to the office" (needs "to")

EXAMPLE: "I wake up at 7 AM every morning."

LEARNING TIP: Practice using time expressions consistently. Common patterns:
- "at 7 AM" (specific time)
- "in the morning" (general time)
- "every day" (frequency)
```

---

### Example 4: Feelings and Preferences

**Your Input:**
```
Muje bahut pasand hai football khelnaa, lekin I am not very good
```

**AI Response:**
```
CORRECTION: I really like playing football, but I am not very good at it

EXPLANATION:
- "Muje bahut pasand hai" → "I really like/love"
- Use "playing" (gerund) after "like"
- Add "at it" to complete the thought
- "I am not very good at it" is more natural than "not good"

EXAMPLE: "I love playing football, but I'm not very good at it."

LEARNING TIP: Use gerunds (verb + ing) after like/love:
✅ "I like playing"
✅ "I love swimming"
❌ "I like to play" (less common in spoken English)
```

---

## Best Practices

### ✅ DO

1. **Write naturally** - Mix languages as you naturally would
2. **Express complete thoughts** - Include context
3. **Use recent examples** - From your daily life
4. **Review feedback** - Learn from corrections
5. **Practice consistently** - Daily practice builds skills

### ❌ DON'T

1. **Don't memorize responses** - Focus on understanding patterns
2. **Don't be perfect** - Mistakes are learning opportunities
3. **Don't avoid mixing languages** - That's the whole point!
4. **Don't skip explanations** - Read why corrections are made
5. **Don't practice passive only** - Actually try to use what you learn

## Tips by Learning Level

### For Beginners

- Focus on **Grammar** and **Vocabulary**
- Use **simple, short sentences**
- Practice **common phrases daily**
- Don't worry about perfection

Example:
```
"Main school jati hoon. I study maths"
```

### For Intermediate Learners

- Focus on **Conversation** and **Pronunciation**
- Practice **more complex sentences**
- Learn **idiomatic expressions**
- Connect ideas with **linking words**

Example:
```
"Although it was raining, I decided to go out because the meeting was important"
```

### For Advanced Learners

- Focus on **Writing** and subtle **Grammar**
- Practice **professional communication**
- Learn **colloquialisms** and **regional variations**
- Refine **pronunciation nuances**

Example:
```
"Despite the inclement weather, I proceeded with the scheduled appointment"
```

## Common Phrases Reference

### Greetings
| English | Urdu | Pronunciation |
|---------|------|---|
| Hello | السلام علیکم | Assalamu alaikum |
| Good morning | صبح بخیر | Subah bakhair |
| How are you? | آپ کیسے ہو؟ | Aap kaisay ho? |
| I'm fine | میں ٹھیک ہوں | Main theek hoon |

### Daily Activities
| English | Urdu | Example |
|---------|------|---------|
| Wake up | اٹھنا | I wake up at 7 AM |
| Have breakfast | ناشتہ کرنا | I have breakfast at 8 AM |
| Go to work | کام پر جانا | I go to work at 9 AM |
| Have lunch | دوپہر کا کھانا | I have lunch at 1 PM |

## Troubleshooting

### Issue: App doesn't respond

**Solution:**
1. Check internet connection
2. Verify API keys are correct
3. Wait a moment and try again
4. Refresh the browser

### Issue: API Key errors

**Solution:**
1. Ensure keys are copied completely
2. Remove any extra spaces before/after key
3. Verify key is active (hasn't expired)
4. Try regenerating the key

### Issue: Responses are irrelevant

**Solution:**
1. Provide more context in your input
2. Check your learning level setting
3. Try switching AI model
4. Ensure focus areas match your needs

## Learning Path

### Week 1-2: Foundation
- Focus: **Grammar + Vocabulary**
- Level: **Beginner**
- Practice: Basic sentences (10-15 minutes daily)

### Week 3-4: Building Confidence
- Focus: **Conversation**
- Level: **Beginner → Intermediate**
- Practice: Short conversations (15-20 minutes daily)

### Week 5-8: Expansion
- Focus: **Vocabulary + Pronunciation**
- Level: **Intermediate**
- Practice: Longer exchanges (20-30 minutes daily)

### Week 9+: Mastery
- Focus: **Writing + Advanced Grammar**
- Level: **Advanced**
- Practice: Complex writing tasks (30+ minutes daily)

## Track Your Progress

### Metrics to Monitor

1. **Correction Frequency** - Are you making fewer mistakes?
2. **Response Quality** - Are your sentences more complex?
3. **Vocabulary Growth** - Are you using new words?
4. **Confidence Level** - Are you more comfortable expressing ideas?

### Review Checklist

Every week, check:
- ✅ How many exchanges have you done?
- ✅ What are common mistakes?
- ✅ What vocabulary have you learned?
- ✅ Are you feeling more confident?

## Advanced Features

### Code-Switching Detection
The app automatically detects when you're mixing English and Urdu and provides appropriate feedback.

### Context Awareness
The AI understands cultural context and provides relevant examples.

### Progress Tracking
Review your conversation history to see improvement over time.

### Model Comparison
Try both Gemini and Groq to see which works best for you.

## Getting More Help

1. **Check examples** - Review the conversation history
2. **Adjust level** - Switch learning level if too easy/hard
3. **Change focus** - Select different focus areas
4. **Try different model** - Switch between Gemini and Groq
5. **Restart session** - Refresh browser and start fresh

---

## Remember

> **Language learning is a marathon, not a sprint!**

- Consistency matters more than intensity
- Small daily practice beats cramming
- Mistakes are stepping stones, not failures
- Your mixed language use is natural and valid
- Every conversation brings you closer to fluency

**Happy learning! 🎓📚🌍**

For technical support, see [README.md](README.md) troubleshooting section.
For quick setup help, see [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md).
