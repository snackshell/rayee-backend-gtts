# Files Needed for Koyeb Deployment

## Required Files (Must Upload)

These files MUST be in your GitHub repository for Koyeb deployment:

### 1. `main.py` ✅
- Production-ready FastAPI application
- No test.html serving
- Environment variable for API key
- Proper logging

### 2. `requirements.txt` ✅
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
gtts==2.5.3
google-generativeai==0.8.3
Pillow==11.0.0
python-dotenv==1.0.1
```

### 3. `.gitignore` ✅
```
__pycache__/
*.py[cod]
.env
.venv
venv/
```

## Optional Files (For Documentation)

These files are helpful but not required for deployment:

- `README.md` - Documentation
- `DEPLOY_KOYEB.md` - Deployment guide
- `QUICKSTART.md` - Local testing guide
- `.env.example` - Environment variable template

## Files to EXCLUDE (Do Not Upload)

These files should NOT be in your GitHub repository:

- ❌ `.env` - Contains your API key (security risk!)
- ❌ `test.html` - Only for local testing
- ❌ `test_backend.py` - Only for local testing
- ❌ `test_audio.mp3` - Generated test files
- ❌ `__pycache__/` - Python cache files

## Minimal Deployment

For the absolute minimum deployment, you only need:

```
backend/
├── main.py              # FastAPI app
├── requirements.txt     # Dependencies
└── .gitignore          # Git ignore rules
```

That's it! Koyeb will:
1. Read `requirements.txt` and install dependencies
2. Run `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Expose your API to the internet

## Environment Variables in Koyeb

Set these in Koyeb dashboard (NOT in code):

```
GEMINI_API_KEY=your_actual_api_key_here
```

## Verification Checklist

Before deploying, verify:

- [ ] `main.py` uses `os.getenv("GEMINI_API_KEY")`
- [ ] No hardcoded API keys in code
- [ ] `.env` is in `.gitignore`
- [ ] `requirements.txt` has all dependencies
- [ ] No test files in repository

## Quick Deploy Command

```bash
# 1. Create GitHub repo
git init
git add main.py requirements.txt .gitignore
git commit -m "Production-ready Ra'yee Backend"
git remote add origin https://github.com/YOUR_USERNAME/rayee-backend.git
git push -u origin main

# 2. Go to Koyeb and deploy from GitHub
# 3. Add GEMINI_API_KEY environment variable
# 4. Deploy!
```

Done! 🚀
