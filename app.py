from flask import Flask,render_template, request, jsonify
import vertexai
from vertexai.language_models import CodeChatModel
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')
CODE_CHAT_MODEL = os.getenv('CODE_CHAT_MODEL')

app = Flask(__name__)

vertexai.init(project=PROJECT_ID, location=LOCATION)
chat_model = CodeChatModel.from_pretrained(CODE_CHAT_MODEL)
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2
}
chat = chat_model.start_chat()


@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')
    response = chat.send_message(userText, **parameters)
    # print(f"Response from Model: {response.text}")

    return response.text



if __name__ == "__main__":
    app.run(debug=True)