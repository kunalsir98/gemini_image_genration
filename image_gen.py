from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import pathlib
import uuid

from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash-exp"

# Create FastAPI app
app = FastAPI()

# Serve static images
app.mount("/images", StaticFiles(directory="images"), name="images")

# Home form page
@app.get("/", response_class=HTMLResponse)
async def form():
    return """
    <html>
        <head>
            <title>Image Generator</title>
        </head>
        <body style="text-align:center;">
            <h2>Prompt to Image Generator</h2>
            <form action="/generate" method="post">
                <input type="text" name="prompt" style="width:300px;" placeholder="Enter your prompt here" required>
                <button type="submit">Generate Image</button>
            </form>
        </body>
    </html>
    """

# Handle image generation
@app.post("/generate", response_class=HTMLResponse)
async def generate(prompt: str = Form(...)):
    try:
        # Generate content
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
        )

        # Save image with unique filename
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                data = part.inline_data.data
                filename = f"{uuid.uuid4().hex}.png"
                image_path = f"images/{filename}"
                pathlib.Path(image_path).write_bytes(data)

                # Return the image in HTML
                return f"""
                <html>
                    <head><title>Generated Image</title></head>
                    <body style="text-align:center;">
                        <h3>Prompt: {prompt}</h3>
                        <img src="/images/{filename}" alt="Generated Image" style="max-width:500px;">
                        <br><br>
                        <a href="/">Try another prompt</a>
                    </body>
                </html>
                """
        return "Image generation failed: No image data in response."

    except Exception as e:
        return f"<h3>Error generating image: {str(e)}</h3>"

