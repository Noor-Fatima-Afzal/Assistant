# 🚀 Quick Start Guide - Windows PowerShell

## One-Line Setup

If you're comfortable with PowerShell, run these commands:

```powershell
# Navigate to project directory
cd "c:\Users\Tech Mehal\Desktop\English\english_learning_app"

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy and edit with your API keys)
copy .env.example .env

# Run the app
streamlit run app.py
```

## Step-by-Step Setup (if you prefer clarity)

### Step 1: Open PowerShell
1. Press `Win + X` and select "Windows PowerShell" or "Terminal"
2. Navigate to the project: 
```powershell
cd "c:\Users\Tech Mehal\Desktop\English\english_learning_app"
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**Note:** If you get an error about execution policies, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activation again.

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

This will install:
- streamlit
- google-generativeai
- groq
- python-dotenv

### Step 5: Setup Environment Variables

**Option A: GUI Method**
1. Right-click on `.env.example` → Open with Notepad
2. Replace placeholder values with your actual API keys:
   - `GEMINI_API_KEY=your_actual_key_here`
   - `GROQ_API_KEY=your_actual_key_here`
3. Save As → Filename: `.env` (note the dot at the start)

**Option B: PowerShell Method**
```powershell
# Copy the example file
Copy-Item .env.example .env

# Edit the .env file with Notepad
notepad .env

# Add your API keys and save
```

### Step 6: Run the Application
```powershell
streamlit run app.py
```

Your browser should automatically open to `http://localhost:8501`

## Getting Your API Keys (Windows)

### Gemini API Key
1. Open your browser and go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste it into your `.env` file

### Groq API Key
1. Open: https://console.groq.com
2. Sign up or login
3. Create an API key
4. Copy and paste into `.env`

## Useful PowerShell Commands

### Deactivate Virtual Environment
```powershell
deactivate
```

### Check Python Version
```powershell
python --version
```

### Check Installed Packages
```powershell
pip list
```

### View File Contents
```powershell
Get-Content .env
```

### Delete Virtual Environment (if needed)
```powershell
Remove-Item -Path venv -Recurse
```

## Troubleshooting on Windows

### Issue: "scripts are disabled on this system"
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "python command not found"
**Solution:** 
- Make sure Python is installed and added to PATH
- Restart PowerShell after installing Python
- Or use full path: `C:\Python39\python.exe`

### Issue: "pip command not found"
**Solution:**
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Issue: "ModuleNotFoundError" when running app
**Solution:**
- Make sure virtual environment is activated (look for `(venv)` in prompt)
- Reinstall packages:
```powershell
pip install --force-reinstall -r requirements.txt
```

### Issue: Port 8501 already in use
**Solution:**
```powershell
streamlit run app.py --server.port 8502
```

## Tips for Best Experience

1. **Keep terminal open** - Don't close PowerShell while the app is running
2. **Use Ctrl+C to stop** - Stop the app by pressing Ctrl+C in PowerShell
3. **Clear cache occasionally** - If app acts weird, restart PowerShell
4. **Keep .env secure** - Never commit `.env` to version control

## Development Tips

### Update Dependencies
```powershell
pip install --upgrade -r requirements.txt
```

### Create Requirements from Installed Packages
```powershell
pip freeze > requirements.txt
```

### Run Python File Directly
```powershell
python language_utils.py
```

## Next Steps

✅ Setup complete! Now:
1. Open the app at `http://localhost:8501`
2. Enter your API keys in the sidebar
3. Select your learning level
4. Start typing mixed English-Urdu text
5. Get instant feedback from AI!

---

**Happy Learning! 🎓**

For more details, see [README.md](README.md)
