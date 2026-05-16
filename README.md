# 🌍 English Learning Assistant

A Streamlit web application that helps English learners practice and improve their English by understanding mixed English-Urdu input and providing intelligent corrections and explanations.

## Features

✨ **Smart Language Understanding**
- Detects and processes mixed English-Urdu text
- Understands context and intent
- Provides natural corrections

📚 **Intelligent Feedback**
- Corrects grammar and vocabulary
- Explains why corrections are needed
- Provides relevant examples
- Gives pronunciation and learning tips

🎯 **Personalized Learning**
- Adjustable difficulty levels (Beginner, Intermediate, Advanced)
- Multiple focus areas (Grammar, Vocabulary, Pronunciation, Conversation, Writing)
- Maintains conversation history for progress tracking

🤖 **Dual AI Models**
- Google Gemini integration
- Groq API integration
- Switch between models based on preference

## Example Usage

**Learner Input:**
> "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain"

**AI Response:**
> **CORRECTION:** "I think you are going to the zoo"
> **EXPLANATION:** "In English, we use 'the zoo' (with definite article) when referring to a specific place..."
> **TIP:** Animals in English: lion (شیر), elephant (ہاتھی), monkey (بندر)...

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))
- Groq API Key (from [Groq Console](https://console.groq.com))

### Installation

1. **Clone or download the project**
```bash
cd c:\Users\Tech Mehal\Desktop\English\english_learning_app
```

2. **Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Keys**

Create a `.env` file in the project directory:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

**⚠️ SECURITY WARNING:** Never commit `.env` file to version control!

5. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Getting API Keys

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key
4. Add to `.env` file

### Groq API
1. Go to [Groq Console](https://console.groq.com)
2. Sign up or login
3. Create an API key
4. Copy your API key
5. Add to `.env` file

## How to Use

1. **Select Learning Level** - Choose between Beginner, Intermediate, or Advanced
2. **Select Focus Areas** - Choose what you want to focus on (Grammar, Vocabulary, etc.)
3. **Choose AI Model** - Pick between Gemini or Groq (or try both!)
4. **Enter Text** - Type or paste your mixed English-Urdu text
5. **Get Feedback** - Receive instant corrections and explanations
6. **Track Progress** - Review your learning history in the app

## Language Support

- ✅ **English** - Full support
- ✅ **Urdu** - Full support
- ✅ **Mixed (Code-switching)** - Primary feature
- 🎯 **Context-aware** - Understands cultural and linguistic nuances

## Tips for Better Learning

1. **Practice Daily** - Even 10 minutes helps!
2. **Express Naturally** - Don't try to be perfect; mix languages as you speak
3. **Review History** - Look at previous corrections to track patterns
4. **Use Focus Areas** - Tailor learning to your specific needs
5. **Experiment with Models** - Different models may provide different insights

## Common Phrases for Learning

| English | Urdu | Usage |
|---------|------|-------|
| Hello | السلام علیکم | Greeting |
| How are you? | آپ کیسے ہو؟ | Common question |
| Thank you | شکریہ | Expression of gratitude |
| Good morning | صبح بخیر | Morning greeting |
| See you later | بعد میں ملتے ہیں | Farewell |

## Troubleshooting

**Issue: "API Key Error"**
- Check that your API key is correctly entered
- Ensure the key is active and has quota remaining
- Try regenerating the key

**Issue: "Rate Limit Exceeded"**
- Wait a few moments before trying again
- Both Gemini and Groq have rate limits

**Issue: "Connection Error"**
- Check your internet connection
- Verify API endpoints are accessible in your region

## Model Comparison

| Feature | Gemini | Groq |
|---------|--------|------|
| Speed | Fast | Very Fast |
| Context Understanding | Excellent | Very Good |
| Multilingual | Excellent | Good |
| Token Limits | High | High |
| Free Tier | Yes | Yes |

## Privacy

- Conversations are stored locally in your session
- API keys are read from environment variables
- No data is stored on external servers (except API provider logs)
- Clear browser cache/session data to remove history

## Future Enhancements

- 🎤 Voice input support
- 📊 Progress dashboard with analytics
- 📱 Mobile app version
- 🌐 Support for more languages
- 🎮 Gamified learning modes
- 👥 Community practice groups

## Contributing

Feel free to fork, modify, and improve this application!

## License

MIT License - Feel free to use for personal and educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API documentation for your chosen model
3. Ensure all dependencies are correctly installed

---

**Happy Learning! 🎓**

Remember: The goal is progress, not perfection. Every sentence you practice makes you better!
