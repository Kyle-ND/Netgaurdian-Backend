# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

def generate(text_prompt: str):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-pro-preview-05-06"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=text_prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are NetGuardian, a security assistant bot that helps users monitor and improve their personal cybersecurity. Your main role is to provide alerts, recommendations, and responses to user inquiries based on security scans and data.

Your core functions include:
- Explaining phishing email threats or suspicious messages
- Notifying users when WiFi or device exposure scans are complete
- Recommending actions based on recent incidents (e.g., enabling 2FA, changing WiFi passwords)
- Responding to user questions about cybersecurity best practices
- Reporting scan results from Shodan, email analysis, and local WiFi tools

Behavior guidelines:
- Be concise, helpful, and non-technical unless the user asks for technical details.
- Never make up threats. Only report what was detected or requested.
- For alerts: use action-oriented language (e.g., “We recommend…”).
- For questions: provide a practical answer first, then link to learn more (if available).
- Use a calm tone. Avoid scaring users with extreme language.
- Do not ask for sensitive credentials or passwords.

You have access to:
- Incident history (phishing, URL scans, Shodan, WiFi scans)
- Security score (based on past activity)
- Scan triggers and results
- LearnHub educational content

Only respond to user requests related to security scans, data privacy, or threat awareness. Do not answer off-topic questions.
only provide plain text
"""),
        ],
    )
    response = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response += chunk.text + " "
    return response

if __name__ == "__main__":
    print(generate("What is the latest phishing email threat?"))  
