from flask import Flask,render_template, request, jsonify
import os
import boto3
import botocore
import json 

bedrock_runtime = boto3.client('bedrock-runtime')

# If you'd like to try your own prompt, edit this parameter!
# prompt_data = []
usermsg = []


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

@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')
    usermsg.append({
        "role":'user',
        "content": [
            {
                "type": "text",
                "text": userText
            }
        ]
    })
    # response = chat.send_message(userText, **parameters) # for the bison model
    response = inv_md(usermsg) # for the gemini AI model
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



if __name__ == "__main__":
    app.run(debug=True, port=8000)
