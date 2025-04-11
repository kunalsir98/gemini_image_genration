from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import requests
import pathlib
import uuid
from PIL import Image as PILImage
from io import BytesIO
from google import genai
from google.genai import types

# Load .env variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash-exp"

# FastAPI app
app = FastAPI()

# Static folder for images
app.mount("/images", StaticFiles(directory="images"), name="images")

# Route to edit the image using AI
@app.post("/image/ai_edit")
async def ai_edit_image(file_url: str = Form(...), user_prompt: str = Form(...)):
    try:
        # Step 1: Download the image from URL
        response = requests.get(file_url)
        if response.status_code != 200:
            return {"error": "Unable to download image from URL."}
        
        image_bytes = BytesIO(response.content)
        image = PILImage.open(image_bytes)

        # Step 2: Ask Gemini to edit the image
        edit_response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                user_prompt,
                image
            ],
            config=types.GenerateContentConfig(response_modalities=["Text", "Image"])
        )

        # Step 3: Extract edited image and save it
        for part in edit_response.candidates[0].content.parts:
            if part.inline_data:
                data = part.inline_data.data
                filename = f"images/edited_{uuid.uuid4().hex}.png"
                pathlib.Path(filename).write_bytes(data)

                # Step 4: Return image URL
                return {
                    "edited_image_url": f"/{filename.replace(os.sep, '/')}"
                }

        return {"error": "No image found in the response."}

    except Exception as e:
        return {"error": str(e)}
