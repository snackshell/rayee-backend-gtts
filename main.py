"""
Ra'yee Backend - Amharic/Tigrinya Smart Glass Assistant
FastAPI backend for image analysis with Google Gemini 2.5 Flash Lite + gTTS
Production-ready deployment for Koyeb
"""
import os
import io
import base64
import logging
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ra'yee Backend",
    version="3.2.0",
    description="Amharic/Tigrinya Smart Glass Assistant - Gemini 2.5 Flash Lite + gTTS (Multi-Key Support)"
)

# Configure CORS for Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API Keys
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5"),
]

# Filter out None values (in case you only set 3 keys, for example)
VALID_API_KEYS = [key for key in API_KEYS if key]

if not VALID_API_KEYS:
    logger.error("No GEMINI_API_KEYS found in environment variables")
    raise ValueError("At least one GEMINI_API_KEY must be set")

logger.info(f"Loaded {len(VALID_API_KEYS)} Gemini API keys for fallback redundancy.")

# Generation Config
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 150,
    "response_mime_type": "text/plain",
}

# --- SYSTEM INSTRUCTIONS ---

AMHARIC_INSTRUCTIONS = """
You are "Ra'yee", a smart glass assistant for a blind person.
Analyze the provided image and describe it directly in fluent, native Amharic Language.

CRITICAL RULES:
1. Output ONLY in the Ge'ez (Fidel) script.
2. Keep the description concise, urgent, and practical.

Focus on:
- Obstacles directly ahead and their approximate distance in meters.
- Path/walkway conditions.
- Objects on the left and right sides.
- Potential hazards or dangers.
- Safe directions to move.

-- TRANSLATED INSTRUCTIONS (AMHARIC) --
አንተ "ራዕይ" (Ra'yee) የተሰኘህ ለዓይነ ስውራን ድጋፍ የሚሰጥ ስማርት መነጽር (Smart Glass) አጋር ነህ።
የቀረበውን ምስል በመተንተን ውጤቱን በቀጥታ፣ በአማርኛ ቋንቋ ግለጽ።

ወሳኝ ህጎች፡
1. ውጤቱን በግዕዝ (ፊደል) ብቻ አቅርብ።
2. መግለጫው አጭር፣ አጣዳፊ እና ተግባራዊ ይሁን።

በሚከተሉት ላይ አተኩር፡
- ከፊት ለፊት ያሉ እንቅፋቶች እና ግምታዊ ርቀታቸው በሜትር።
- የመንገዱ ወይም የእግረኛ መንገድ ሁኔታ።
- በግራ እና በቀኝ በኩል ያሉ ነገሮች።
- ሊያጋጥሙ የሚችሉ አደጋዎች።
- ለመንቀሳቀስ አስተማማኝ እና ክፍት አቅጣጫዎች።
"""

TIGRINYA_INSTRUCTIONS = """
You are "Ra'yee", a smart glass assistant for a blind person.
Analyze the provided image and describe it directly in fluent, native Tigrinya Language.

CRITICAL RULES:
1. Output ONLY in Tigrinya (Fidel) script.
2. Keep the description concise, urgent, and practical.

Focus on:
- Obstacles directly ahead and their approximate distance in meters.
- Path/walkway conditions.
- Objects on the left and right sides.
- Potential hazards or dangers.
- Safe directions to move.

-- TRANSLATED INSTRUCTIONS (TIGRINYA) --
ንስኻ "ራእይ" (Ra'yee) ዝተብሃልካ ንዓይነ-ስውራን እትሕግዝ "ስማርት ግላስ" (Smart Glass) ኢኻ።
ነቲ ዝተወሃበ ስእሊ ብምትንታን ኩነታቱ ብቐጥታ፣ ብጽሬት ብትግርኛ ቋንቋ ግለጾ።

ወሳኒ ሕግታት፡
1. መልሲ ብፊደል (ግእዝ) ጥራይ ይኹን።
2. እቲ መግለጺ ሓጺር፣ ህጹጽን ግብራውን ይኹን።

ኣብዞም ዝስዕቡ ኣተኩር፡
- ብቐጥታ ኣብ ቅድሚት ዘለዉ ዕንቅፋታትን ብሜትሮ ዝግመት ርሕቀቶምን።
- ኩነታት እቲ መገዲ ወይ ማርሻ-ፔደ።
- ብጸጋምን የማንን ዘለዉ ነገራት።
- ከጋጥሙ ዝኽእሉ ሓደጋታት።
- ንምስጉም ዘተአማምኑን ክፉታትን ኣንፈታት።
"""

async def process_image_with_gemini(image_bytes: bytes, instructions: str) -> str:
    """
    Helper function to process image with Gemini.
    Iterates through VALID_API_KEYS until one works.
    """
    image_part = {"mime_type": "image/jpeg", "data": image_bytes}
    last_error = None

    for index, api_key in enumerate(VALID_API_KEYS):
        try:
            # Configure global GenAI with the current key
            genai.configure(api_key=api_key)
            
            # Initialize model
            model = genai.GenerativeModel(
                model_name="gemini-3-flash",
                generation_config=generation_config,
                system_instruction=instructions
            )

            logger.info(f"Attempting generation with API Key #{index + 1}...")
            
            # Generate content
            response = model.generate_content([image_part])
            
            # If successful, return immediately
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"API Key #{index + 1} failed: {str(e)}")
            last_error = e
            # Continue to the next key in the loop
            continue

    # If we exit the loop, all keys failed
    logger.error("All Gemini API keys failed.")
    raise last_error or Exception("All API keys failed to generate a response.")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "Ra'yee Backend",
        "version": "3.2.0",
        "status": "running",
        "model": "gemini-3-flash",
        "keys_loaded": len(VALID_API_KEYS),
        "endpoints": {
            "POST /api-am": "Amharic Audio Analysis",
            "POST /api-ti": "Tigrinya Audio Analysis"
        }
    }


@app.post("/api-am")
async def analyze_image_amharic(image: UploadFile = File(...)):
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        image_bytes = await image.read()
        
        # 1. Get Text (with fallback logic)
        amharic_text = await process_image_with_gemini(image_bytes, AMHARIC_INSTRUCTIONS)
        
        if not amharic_text:
            raise HTTPException(status_code=500, detail="AI returned empty response")

        # 2. Generate Audio
        tts = gTTS(text=amharic_text, lang='am', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # 3. Stream Response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=rayee_am.mp3",
                "X-Amharic-Text": base64.b64encode(amharic_text.encode('utf-8')).decode('utf-8'),
                "X-English-Text": "" # Safety fix for app compatibility
            }
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api-ti")
async def analyze_image_tigrinya(image: UploadFile = File(...)):
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        image_bytes = await image.read()
        
        # 1. Get Text (with fallback logic)
        tigrinya_text = await process_image_with_gemini(image_bytes, TIGRINYA_INSTRUCTIONS)
        
        if not tigrinya_text:
            raise HTTPException(status_code=500, detail="AI returned empty response")

        # 2. Generate Audio (using 'am' voice for Ge'ez script)
        tts = gTTS(text=tigrinya_text, lang='am', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # 3. Stream Response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=rayee_ti.mp3",
                "X-Tigrinya-Text": base64.b64encode(tigrinya_text.encode('utf-8')).decode('utf-8'),
                "X-English-Text": "" # Safety fix for app compatibility
            }
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "keys_configured": len(VALID_API_KEYS),
        "model": "gemini-3-flash",
        "version": "3.2.0"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Ra'yee Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

