from flask import Flask,render_template, request, jsonify, session
from flask_session import Session
import os
import boto3
import botocore
import json 
import fitz  # PyMuPDF
import base64

bedrock_runtime = boto3.client('bedrock-runtime')

# If you'd like to try your own prompt, edit this parameter!
# prompt_data = []
usermsg = []
extracted_data = []
text_data = []




def inv_md(prompt_data):

    messages_API_body = {
        "anthropic_version": "bedrock-2023-05-31", 
        "max_tokens": int(500/0.75),
        "messages": prompt_data
    }
    body = json.dumps(messages_API_body)
    modelId = "anthropic.claude-3-haiku-20240307-v1:0"  # (Change this to try different model versions)
    accept = "application/json"
    contentType = "application/json"

    try:
        response = bedrock_runtime.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())
        # response_body = json.loads(chunk.get('bytes').decode())

        return response_body.get("content")[0].get("text")
        # print(response_body)

    except botocore.exceptions.ClientError as error:

        if error.response['Error']['Code'] == 'AccessDeniedException':
            print(f"\x1b[41m{error.response['Error']['Message']}\
                    \nTo troubeshoot this issue please refer to the following resources.\
                    \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                    \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")

        else:
            raise error




app = Flask(__name__)
# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # Can also use 'redis', 'mongodb', etc., for production
app.config['SECRET_KEY'] = 'your_secret_key'
Session(app)


@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')
    
    extracted_data = session.get('extracted_data', [])
    text_data = session.get('text_data', [])
    
    ini_prompt = f"""
    The below consists of information on a particular document. I want to
    look through the document and answer the prompt based solely on the 
    information provided. It is also possible that images would be attached 
    as well. But if no images are attached, then provide information on what
    you see here alone
    
    Information Provided: {text_data}
    
    
    the prompt: {userText}
    """


    # print("extracted_data: ", extracted_data)
    # print("extracted_data: ", extracted_data[0])
    usermsg.append({
        "role":'user',
        "content": [
            # {
            #     "type": "image",
            #     "source": {
            #         "type": "base64",
            #         "media_type": "image/jpeg",
            #         "data": extracted_data[0]['image_1_base64']
            #         }
            # },
            {
                "type": "text",
                "text": ini_prompt
            }
        ]
    })
    # Add each image to the content
    for image_dict in extracted_data:
        for _, base64_image in image_dict.items():
            usermsg[-1]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image
                    }                
            })
        
    # response = chat.send_message(userText, **parameters) # for the bison model
    response = inv_md(usermsg) # for the gemini AI model
    # response = extracted_data[0]
    # print(f"Response from Model: {response.text}")
    
    usermsg.append({
        "role":'assistant',
        "content": [
            {
                "type": "text",
                "text": response
            }
        ]
        
    })
    return response


@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400
    
    pdf_file = request.files['pdf']
    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({'message': 'Only PDF files are supported'}), 400

    pdf_content = pdf_file.read()
    doc = fitz.open(stream=pdf_content, filetype="pdf")

    extracted_data = []

    # Extract text
    text_data = []
    for page in doc:
        text_data.append(page.get_text())
    # if text_data:
    #     extracted_data.append({"text": "\n".join(text_data)})

    # Extract images
    image_data = {}
    image_count = 1
    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_data[f"image_{image_count}_base64"] = image_base64
            image_count += 1

    if image_data:
        extracted_data.append(image_data)
        
    # print("text_data: ", text_data)
    # print("extracted_data: ", extracted_data)
    # Store data in the session
    session['extracted_data'] = extracted_data
    session['text_data'] = text_data

    return jsonify({'message': 'File processed successfully', 'data': extracted_data})



if __name__ == "__main__":
    app.run(debug=True, port=8000)
