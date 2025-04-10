I am giving image to my gemini-2.0-flash-exp or any other gemin model but it is unable to edit the image only giving the image in worng format 


You CANNOT do image editing using Gemini 2.0 Flash Exp via API or on your local machine.
✅ It works only in Google AI Studio or special Google Colab notebooks (because they use Google’s internal, experimental image editing tools).

❌ The public Gemini API (used with Python or Node.js SDKs) does not support image generation or editing — only image analysis, like captioning or question answering.

✅ What You CAN Do with Gemini API:
Task	Gemini API	AI Studio
Text generation	✅	✅
Image analysis (input)	✅	✅
Image editing/output	❌	✅