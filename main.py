"""
Ra'yee Backend - Amharic Smart Glass Assistant
FastAPI backend for image analysis with GROQ Llama 4 + Vercel Translator + gTTS
Production-ready deployment for Koyeb
"""
import os
import io
import base64
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
from groq import Groq
from PIL import Image
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ra'yee Backend",
    version="2.0.0",
    description="Amharic Smart Glass Assistant - Image Analysis with GROQ Llama 4 + Vercel Translator + gTTS"
)

# Configure CORS for Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure GROQ API from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY environment variable not set")
    raise ValueError("GROQ_API_KEY environment variable not set")

# Initialize GROQ client
groq_client = Groq(api_key=GROQ_API_KEY)

# Vercel translator API endpoint
TRANSLATOR_API = "https://selam-trans.vercel.app/api/translate"

# Vision prompt for GROQ (in English)
VISION_PROMPT = """You are "Ra'yee", a smart glass assistant for a blind person.
Describe this image focusing on navigation and obstacles.

Focus on:
- Obstacles directly ahead and their distance (estimate in meters)
- Path/walkway conditions
- Objects on left and right sides
- Potential hazards or dangers
- Safe directions to move
- If a person is very close (about to collide), mention it
- If the area is crowded, mention it

Keep the description concise (2-3 sentences) and practical for navigation.
Use simple, clear language."""

logger.info("Ra'yee Backend initialized with GROQ + Vercel Translator")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Ra'yee Backend",
        "version": "2.0.0",
        "status": "running",
        "description": "Amharic Smart Glass Assistant API (GROQ + Vercel Translator)",
        "endpoints": {
            "POST /analyze-image": "Analyze image and return Amharic audio",
            "GET /health": "Health check endpoint"
        }
    }


@app.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyzes an image using GROQ Llama 4 and returns Amharic audio description
    
    Args:
        image: JPEG/PNG image file from ESP32-CAM or mobile app
        
    Returns:
        MP3 audio file with Amharic description
        
    Headers:
        X-Amharic-Text: Base64 encoded Amharic text response
        X-English-Text: Base64 encoded English text response
    """
    try:
        # Validate image file
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        logger.info(f"Received image: {image.filename}, content_type: {image.content_type}")
        
        # Read image bytes
        image_bytes = await image.read()
        logger.info(f"Image size: {len(image_bytes)} bytes")
        
        # Encode image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Analyze image with GROQ Llama 4
        logger.info("Sending image to GROQ Llama 4...")
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0.7,
            max_tokens=150,
        )
        
        english_text = chat_completion.choices[0].message.content
        logger.info(f"GROQ response (English): {english_text[:100]}...")
        
        # Translate to Amharic using Vercel API
        logger.info("Translating to Amharic...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            translation_response = await client.post(
                TRANSLATOR_API,
                json={
                    "text": english_text,
                    "source_language": "en",
                    "target_language": "am"
                }
            )
            
            if translation_response.status_code != 200:
                logger.error(f"Translation failed: {translation_response.status_code}")
                raise HTTPException(status_code=500, detail="Translation service error")
            
            translation_data = translation_response.json()
            amharic_text = translation_data.get("translated_text", "")
            
            if not amharic_text:
                logger.error("Empty translation response")
                raise HTTPException(status_code=500, detail="Translation returned empty")
        
        logger.info(f"Amharic translation: {amharic_text[:100]}...")
        
        # Generate Amharic audio with gTTS
        logger.info("Generating Amharic audio with gTTS...")
        tts = gTTS(text=amharic_text, lang='am', slow=False)
        
        # Save to BytesIO buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        logger.info("Audio generated successfully")
        
        # Return MP3 audio as streaming response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=rayee_response.mp3",
                "X-Amharic-Text": base64.b64encode(amharic_text.encode('utf-8')).decode('utf-8'),
                "X-English-Text": base64.b64encode(english_text.encode('utf-8')).decode('utf-8')
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "groq_configured": bool(GROQ_API_KEY),
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "translator": "Vercel Selam-Trans API",
        "tts_engine": "gTTS",
        "language": "Amharic (am)",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Ra'yee Backend on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
