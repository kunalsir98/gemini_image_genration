from flask import Flask, request, jsonify, send_file
import base64
from google import genai
from google.genai import types
import io

app = Flask(__name__)

client = genai.Client(api_key="AIzaSyDC_KALlH7KORnOfm5bEyQzv6fG8FXXnsQ")

@app.route('/edit_image', methods=['POST'])
def edit_image():
    prompt = request.form.get('prompt')  # Fix typo: 'prompt' instead of 'prompt'
    image_file = request.files.get('image')

    if not image_file:
        return jsonify({'error': 'No image file provided'}), 400

    try:
        # Read and encode image
        image_bytes = image_file.read()
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        # Create request parts
        text_part = types.Part(text=prompt)
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=image_file.content_type,
                data=encoded_image
            )
        )

        # Generate content
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[text_part, image_part],
            config=types.GenerateContentConfig(
                response_modalities=['Image']
            )
        )

        # Extract image data from response
        image_data = None
        mime_type = 'image/png'  # default
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                    image_data = base64.b64decode(part.inline_data.data)
                    mime_type = part.inline_data.mime_type
                    break

        if not image_data:
            return jsonify({'error': 'Image generation failed'}), 500

        # Return image
        return send_file(
            io.BytesIO(image_data),
            mimetype=mime_type
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)