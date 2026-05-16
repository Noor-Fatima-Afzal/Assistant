"""
Demo script to test the English Learning Assistant without Streamlit UI
Useful for testing and debugging API connections
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from language_utils import detect_language_mix_ratio, extract_learning_context

# Load environment variables
load_dotenv()

def demo_gemini():
    """Test Gemini API with a sample input"""
    print("\n" + "="*60)
    print("🔷 Testing GEMINI API")
    print("="*60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Test input
        test_input = "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain"
        print(f"\n📝 Input: {test_input}")
        print("\n⏳ Generating response...")
        
        response = model.generate_content(
            f"You are an English tutor. A learner said: '{test_input}'. "
            f"Provide a correction and brief explanation."
        )
        
        print("\n✅ Response from Gemini:")
        print("-" * 60)
        print(response.text)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_groq():
    """Test Groq API with a sample input"""
    print("\n" + "="*60)
    print("🟢 Testing GROQ API")
    print("="*60)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return False
    
    try:
        client = Groq(api_key=api_key)
        
        # Test input
        test_input = "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain"
        print(f"\n📝 Input: {test_input}")
        print("\n⏳ Generating response...")
        
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"You are an English tutor. A learner said: '{test_input}'. "
                             f"Provide a correction and brief explanation."
                }
            ]
        )
        
        print("\n✅ Response from Groq:")
        print("-" * 60)
        print(message.choices[0].message.content)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_language_detection():
    """Test language detection functionality"""
    print("\n" + "="*60)
    print("🌐 Testing LANGUAGE DETECTION")
    print("="*60)
    
    test_cases = [
        "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain",
        "Mera naam Ahmed hai, aur main engineer hoon",
        "I love playing cricket and badminton",
        "Main subah 7 baje uthta hoon",
        "Hello, how are you today?"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Text: '{test_text}'")
        
        # Detect mix ratio
        mix_ratio = detect_language_mix_ratio(test_text)
        print(f"   English: {mix_ratio['english_ratio']*100:.1f}%")
        print(f"   Urdu: {mix_ratio['urdu_ratio']*100:.1f}%")
        print(f"   Has Urdu: {mix_ratio['has_urdu']}")
        print(f"   Has English: {mix_ratio['has_english']}")
        
        # Extract context
        context = extract_learning_context(test_text)
        print(f"   Is Question: {context['is_question']}")
        print(f"   Is Exclamation: {context['is_exclamation']}")
        print(f"   Word Count: {context['text_length']}")
        print(f"   Mixed Language: {context['has_mixed_language']}")

def demo_full_workflow():
    """Run a full workflow demo"""
    print("\n" + "="*60)
    print("🚀 FULL WORKFLOW DEMO")
    print("="*60)
    
    test_inputs = [
        ("Beginner", "I am going to.....ohh usy kia kahty hain jha par janwar hoty hain"),
        ("Intermediate", "Mera naam sara hai, aur main english seekh rahi hoon"),
    ]
    
    model_choice = input("\nSelect model to test:\n1. Gemini\n2. Groq\nChoice (1 or 2): ")
    
    if model_choice == "1":
        for level, test_input in test_inputs:
            print(f"\n📚 Level: {level}")
            print(f"📝 Input: {test_input}")
            demo_gemini() if model_choice == "1" else demo_groq()
    elif model_choice == "2":
        for level, test_input in test_inputs:
            print(f"\n📚 Level: {level}")
            print(f"📝 Input: {test_input}")
            demo_groq()
    else:
        print("Invalid choice")

def main():
    """Main demo menu"""
    print("\n" + "="*60)
    print("🌍 ENGLISH LEARNING ASSISTANT - DEMO")
    print("="*60)
    
    while True:
        print("\n📋 Choose a test to run:")
        print("1. Test Gemini API")
        print("2. Test Groq API")
        print("3. Test Language Detection")
        print("4. Run Full Workflow Demo")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            success = demo_gemini()
            if not success:
                print("\n💡 Tip: Make sure your Gemini API key is in .env file")
                
        elif choice == "2":
            success = demo_groq()
            if not success:
                print("\n💡 Tip: Make sure your Groq API key is in .env file")
                
        elif choice == "3":
            demo_language_detection()
            
        elif choice == "4":
            demo_full_workflow()
            
        elif choice == "5":
            print("\n✅ Demo completed!")
            print("👉 Now run: streamlit run app.py")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  WARNING: .env file not found!")
        print("📝 Please create .env file with your API keys:")
        print("   - Copy .env.example to .env")
        print("   - Add your GEMINI_API_KEY and GROQ_API_KEY")
        print("\n" + "="*60)
    
    main()
