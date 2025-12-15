"""
Ra'yee Backend - Amharic Smart Glass Assistant
FastAPI backend for image analysis with Gemini 2.0 Flash Exp and Amharic TTS with gTTS
Production-ready deployment for Koyeb
"""
import os
import io
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import google.generativeai as genai
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
    version="1.0.0",
    description="Amharic Smart Glass Assistant - Image Analysis with Gemini 2.0 Flash Exp + gTTS"
)

# Configure CORS for Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set")
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini 2.0 Flash Exp model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Amharic prompt for blind person assistance
AMHARIC_PROMPT = "Explain this image for the blind person in fluent native Amharic"

logger.info("Ra'yee Backend initialized successfully")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Ra'yee Backend",
        "version": "1.0.0",
        "status": "running",
        "description": "Amharic Smart Glass Assistant API",
        "endpoints": {
            "POST /analyze-image": "Analyze image and return Amharic audio",
            "GET /health": "Health check endpoint"
        }
    }


@app.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyzes an image using Gemini 2.0 Flash Exp and returns Amharic audio description
    
    Args:
        image: JPEG/PNG image file from ESP32-CAM or mobile app
        
    Returns:
        MP3 audio file with Amharic description
        
    Headers:
        X-Amharic-Text: Base64 encoded Amharic text response
    """
    try:
        # Validate image file
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        logger.info(f"Received image: {image.filename}, content_type: {image.content_type}")
        
        # Read image bytes
        image_bytes = await image.read()
        logger.info(f"Image size: {len(image_bytes)} bytes")
        
        # Open image with PIL
        pil_image = Image.open(io.BytesIO(image_bytes))
        logger.info(f"Image format: {pil_image.format}, size: {pil_image.size}")
        
        # Generate description with Gemini 2.0 Flash Exp
        logger.info("Sending image to Gemini 2.0 Flash Exp...")
        response = model.generate_content([AMHARIC_PROMPT, pil_image])
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Gemini returned empty response")
        
        amharic_text = response.text
        logger.info(f"Gemini response: {amharic_text[:100]}...")
        
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
                "X-Amharic-Text": base64.b64encode(amharic_text.encode('utf-8')).decode('utf-8')
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "model": "gemini-2.0-flash-exp",
        "tts_engine": "gTTS",
        "language": "Amharic (am)",
        "version": "1.0.0"
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
