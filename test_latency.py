"""
Quick latency test script
Shows response times for both Groq and Gemini
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import time

load_dotenv()

TEST_CASES = [
    "i going to school",
    "He are very nice",
    "I think you are going to the zoo",
]


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

def test_groq_speed():
    """Test Groq response speed"""
    print("\n" + "="*60)
    print("⚡ GROQ SPEED TEST (Expected: 1-2 seconds)")
    print("="*60)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found")
        return
    
    client = Groq(api_key=api_key)
    
    for i, test_input in enumerate(TEST_CASES, 1):
        print(f"\n📝 Test {i}: '{test_input}'")
        
        start = time.time()
        try:
            message = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": f"Fix grammar errors: {test_input}"
                    }
                ]
            )
            elapsed = time.time() - start
            
            response_text = extract_groq_text(message)
            response_text = response_text[:100] + "..." if len(response_text) > 100 else response_text
            
            print(f"⚡ Time: {elapsed:.2f} seconds")
            print(f"📌 Response: {response_text}")
            
            # Show speed rating
            if elapsed < 1.5:
                print("🟢 EXCELLENT (< 1.5s)")
            elif elapsed < 2.0:
                print("🟡 GOOD (1.5-2.0s)")
            else:
                print("🔴 SLOW (> 2.0s)")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")

def test_gemini_speed():
    """Test Gemini response speed"""
    print("\n" + "="*60)
    print("🧠 GEMINI SPEED TEST (Expected: 3-5 seconds)")
    print("="*60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    model = get_gemini_model()
    
    for i, test_input in enumerate(TEST_CASES, 1):
        print(f"\n📝 Test {i}: '{test_input}'")
        
        start = time.time()
        try:
            response = model.generate_content(f"Fix grammar errors: {test_input}")
            elapsed = time.time() - start
            
            response_text = response.text[:100] + "..." if len(response.text) > 100 else response.text
            
            print(f"🧠 Time: {elapsed:.2f} seconds")
            print(f"📌 Response: {response_text}")
            
            # Show speed rating
            if elapsed < 3:
                print("🟢 EXCELLENT (< 3s)")
            elif elapsed < 5:
                print("🟡 GOOD (3-5s)")
            else:
                print("🔴 SLOW (> 5s)")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")

def compare_speed():
    """Compare speed of both models"""
    print("\n" + "="*60)
    print("📊 MODEL COMPARISON")
    print("="*60)
    
    results = {"groq_times": [], "gemini_times": []}
    
    api_key_groq = os.getenv("GROQ_API_KEY")
    api_key_gemini = os.getenv("GEMINI_API_KEY")
    
    if api_key_groq:
        print("\n🚀 Testing Groq (3 requests)...")
        client = Groq(api_key=api_key_groq)
        
        for test_input in TEST_CASES:
            start = time.time()
            try:
                message = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    max_tokens=512,
                    messages=[{"role": "user", "content": test_input}]
                )
                elapsed = time.time() - start
                results["groq_times"].append(elapsed)
                print(f"  ✓ {elapsed:.2f}s")
            except:
                pass
    
    if api_key_gemini:
        print("\n🧠 Testing Gemini (3 requests)...")
        genai.configure(api_key=api_key_gemini)
        model = get_gemini_model()
        
        for test_input in TEST_CASES:
            start = time.time()
            try:
                response = model.generate_content(test_input)
                elapsed = time.time() - start
                results["gemini_times"].append(elapsed)
                print(f"  ✓ {elapsed:.2f}s")
            except:
                pass
    
    # Show summary
    print("\n" + "="*60)
    print("📈 SUMMARY")
    print("="*60)
    
    if results["groq_times"]:
        avg_groq = sum(results["groq_times"]) / len(results["groq_times"])
        print(f"\n⚡ Groq Average: {avg_groq:.2f} seconds")
        print(f"   Speed: {'🟢 FAST (< 2s)' if avg_groq < 2 else '🟡 OKAY' if avg_groq < 5 else '🔴 SLOW'}")
    
    if results["gemini_times"]:
        avg_gemini = sum(results["gemini_times"]) / len(results["gemini_times"])
        print(f"\n🧠 Gemini Average: {avg_gemini:.2f} seconds")
        print(f"   Speed: {'🟢 FAST' if avg_gemini < 3 else '🟡 OKAY' if avg_gemini < 8 else '🔴 SLOW'}")
    
    if results["groq_times"] and results["gemini_times"]:
        avg_groq = sum(results["groq_times"]) / len(results["groq_times"])
        avg_gemini = sum(results["gemini_times"]) / len(results["gemini_times"])
        speedup = avg_gemini / avg_groq
        print(f"\n⚡ Groq is {speedup:.1f}x FASTER than Gemini ⚡")

def main():
    """Main menu"""
    print("\n" + "="*60)
    print("⚡ ENGLISH LEARNING ASSISTANT - LATENCY TEST")
    print("="*60)
    
    while True:
        print("\n📋 Choose test:")
        print("1. Test Groq Speed")
        print("2. Test Gemini Speed")
        print("3. Compare Both Models")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ").strip()
        
        if choice == "1":
            test_groq_speed()
        elif choice == "2":
            test_gemini_speed()
        elif choice == "3":
            compare_speed()
        elif choice == "4":
            print("\n✅ Test completed!")
            print("👉 For the app: streamlit run app.py")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    print("⚠️  Make sure your API keys are in .env file")
    print("💡 Tip: Groq is MUCH faster for this task")
    
    main()
