# app.py (updated)
from flask import Flask, render_template, request, send_from_directory
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import pathlib
import base64
from PIL import Image
import uuid

load_dotenv()
app = Flask(__name__)

# Configure GenAI client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_ID = "gemini-2.0-flash-exp"

# Ensure directories exist
UPLOAD_FOLDER = os.path.join('static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_image(prompt, existing_image_path=None):
    """Generate image using GenAI model"""
    if existing_image_path:
        # Handle path correctly across OS
        full_image_path = os.path.join(UPLOAD_FOLDER, os.path.basename(existing_image_path))
        image = Image.open(full_image_path)
        contents = [
            prompt,
            image
        ]
    else:
        contents = prompt

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )
    
    # Save image and get text response
    text_response = ""
    image_filename = None
    for part in response.candidates[0].content.parts:
        if part.text:
            text_response += part.text + "\n"
        elif part.inline_data:
            # Generate unique filename
            image_filename = f"{uuid.uuid4()}.png"
            # Decode base64 image data
            decoded_data = base64.b64decode(part.inline_data.data)
            # Save to file
            with open(os.path.join(UPLOAD_FOLDER, image_filename), 'wb') as f:
                f.write(decoded_data)
    
    return text_response, image_filename

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prompt = request.form['prompt']
        text_response, image_filename = generate_image(prompt)
        return render_template('result.html', 
                             text_response=text_response,
                             image_filename=image_filename)
    return render_template('index.html')

@app.route('/modify', methods=['POST'])
def modify_image():
    original_filename = request.form['original_image']
    modification_prompt = request.form['modification_prompt']
    
    text_response, modified_filename = generate_image(
        modification_prompt,
        original_filename
    )
    
    return render_template('result.html',
                         text_response=text_response,
                         image_filename=modified_filename,
                         original_image=original_filename)

@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)