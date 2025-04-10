from flask import Flask,request,jsonify,send_file
import base64
from google import genai
from google.genai import types
import io
from PIL import Image
import pathlib

app=Flask(__name__)

client=genai.Client(api_key="AIzaSyDC_KALlH7KORnOfm5bEyQzv6fG8FXXnsQ")

@app.route('/edit_image', methods=['POST'])
def edit_image():
    prompt = request.form.get('prompt')
    image_file = request.files.get('image')  

    if image_file is None:
        return jsonify({'error': 'No image file provided'}), 400

    image = Image.open(io.BytesIO(image_file.read()))

    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[
            prompt,
            image
        ],
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            data = part.inline_data.data
            decoded_data = base64.b64decode(data)
            image_path = "edited_image.png"
            pathlib.Path(image_path).write_bytes(decoded_data)

    if image_path:
        return send_file(image_path, mimetype='image/png')
    else:
        return jsonify({'error': "Image generation failed"}), 500

    

if __name__=='__main__':
      app.run(debug=True)




        
