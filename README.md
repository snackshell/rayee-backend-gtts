# Ra'yee Backend - Amharic Smart Glass Assistant

FastAPI backend for Ra'yee smart glass that provides image analysis and Amharic text-to-speech.

## Features

- **Gemini 2.0 Flash Exp**: Fast image analysis optimized for mobile
- **gTTS Amharic TTS**: Natural Amharic voice synthesis
- **Single Endpoint**: `/analyze-image` - send image, receive MP3 audio
- **CORS Enabled**: Works with Flutter mobile apps

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key from: https://aistudio.google.com/apikey

### 3. Run Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: http://localhost:8000

### 4. Test with Web Interface

Open `test.html` in your browser to test the backend with a visual interface:

```bash
# Just open the file in your browser
# Or use Python's built-in server:
python -m http.server 3000
# Then visit: http://localhost:3000/test.html
```

The test page allows you to:
- Upload images via click or drag-and-drop
- Send to backend for analysis
- Listen to Amharic audio response
- View the Amharic text

## API Documentation

### POST /analyze-image

Analyzes an image and returns Amharic audio description.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `image` (file) - JPEG image from ESP32-CAM

**Response:**
- Content-Type: `audio/mpeg`
- Body: MP3 audio file with Amharic description
- Header: `X-Amharic-Text` - Base64 encoded Amharic text

**Example with curl:**

```bash
curl -X POST http://localhost:8000/analyze-image \
  -F "image=@test_image.jpg" \
  --output response.mp3
```

**Example with Python:**

```python
import requests

with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/analyze-image',
        files={'image': f}
    )

with open('response.mp3', 'wb') as f:
    f.write(response.content)
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "model": "gemini-2.0-flash-exp",
  "tts_engine": "gTTS",
  "language": "Amharic (am)"
}
```

### GET /

Root endpoint for basic health check.

**Response:**
```json
{
  "status": "ok",
  "service": "Ra'yee Backend",
  "version": "1.0.0"
}
```

## Deployment

### Deploy to Koyeb

1. Create account at https://www.koyeb.com/
2. Push code to GitHub
3. In Koyeb dashboard, click "Create App"
4. Select "GitHub" as source
5. Configure:
   - **Build command**: `pip install -r requirements.txt`
   - **Run command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Port**: 8000
6. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key
7. Click "Deploy"

Your backend will be available at: `https://your-app.koyeb.app`

### Deploy to Render

1. Create account at https://render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key
6. Click "Create Web Service"

## Architecture

```
ESP32-CAM → Flutter App → FastAPI Backend → Gemini 2.0 Flash Exp
                                          ↓
                          MP3 Audio ← gTTS (Amharic)
```

## Prompt

The system uses this prompt for Gemini:

> "Explain this image for the blind person in fluent native Amharic"

This ensures the AI provides helpful navigation assistance in native Amharic language.

## Performance

- **Gemini 2.0 Flash Exp**: ~1-2 seconds for image analysis
- **gTTS**: ~0.5-1 second for audio generation
- **Total latency**: ~2-3 seconds from image to audio

## Troubleshooting

### "GEMINI_API_KEY environment variable not set"

Make sure you've created `.env` file with your API key.

### "Gemini returned empty response"

Check your API key is valid and has quota remaining.

### CORS errors from Flutter app

The backend is configured to allow all origins. If you still see CORS errors, check your network connection.

## Testing

Test the endpoint with a sample image:

```bash
# Download a test image
curl -o test.jpg https://picsum.photos/640/480

# Send to backend
curl -X POST http://localhost:8000/analyze-image \
  -F "image=@test.jpg" \
  --output response.mp3

# Play the audio (macOS)
afplay response.mp3

# Play the audio (Linux)
mpg123 response.mp3
```

## License

MIT
