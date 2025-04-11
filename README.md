This project is an AI-powered image editor built with FastAPI and Gemini (Google GenAI). It allows users to input an image URL and a prompt describing what they want to change in the image. The app then uses Gemini to apply the edit and returns the newly generated image.

🚀 Features
🔗 Accepts an image via URL input

✍️ Takes a text prompt describing the desired edit

🧠 Uses Gemini 2.0 Flash to generate AI-edited images

🖼️ Saves and serves the output image via FastAPI

🧾 Easy-to-use POST endpoint (/image/ai_edit)


The main code is in (image_editor.py)