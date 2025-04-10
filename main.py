import os
import requests
from flask import Flask, request, send_file, jsonify
from io import BytesIO

app = Flask(__name__)

GEMINI_API_KEY = 'AIzaSyDC_KALlH7KORnOfm5bEyQzv6fG8FXXnsQ'  # Replace this

@app.route('/image/ai_edit', methods=['POST'])
def ai_image_edit():
    data = request.get_json()
    image_url = data.get("file_url")
    user_prompt = data.get("user_prompt")

    if not image_url or not user_prompt:
        return jsonify({"error": "Missing file_url or user_prompt"}), 400

    try:
        # Step 1: Download the image
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return jsonify({"error": "Could not fetch image from URL"}), 400
        image_bytes = image_response.content

        # Step 2: Prepare Gemini API request
        gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        # Encode image in base64
        import base64
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        body = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": encoded_image
                            }
                        },
                        {
                            "text": user_prompt
                        }
                    ]
                }
            ]
        }

        # Step 3: Send request to Gemini
        gemini_response = requests.post(gemini_endpoint, headers=headers, json=body)
        gen_data = gemini_response.json()

        # 🔍 Debug: Print the entire response so we can fix any issues
        print("Gemini response:", gen_data)

        if gemini_response.status_code != 200:
            return jsonify({"error": "Gemini API call failed", "details": gen_data}), 500

        # Step 4: Try to extract the image (may fail if format is different)
        try:
            image_b64 = gen_data['candidates'][0]['content']['parts'][0]['inline_data']['data']
        except Exception as e:
            return jsonify({
                "error": "Could not extract image from Gemini response.",
                "reason": str(e),
                "raw_response": gen_data
            }), 500

        image_data = base64.b64decode(image_b64)

        # Step 5: Return the image
        return send_file(BytesIO(image_data), mimetype='image/jpeg', download_name='edited_image.jpg')

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
