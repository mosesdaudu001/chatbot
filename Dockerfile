from python:3.8-slim-buster

RUN apt-get upgrade && apt-get update

RUN apt update -y && apt install awscli -y
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG AWS_DEFAULT_OUTPUT


ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
ENV AWS_DEFAULT_OUTPUT=$AWS_DEFAULT_OUTPUT

COPY . .

EXPOSE 7000

RUN pip install -r requirements.txt

# CMD ["python3", "app.py"]
ENTRYPOINT [ "gunicorn",  "--timeout=600", "--bind=0.0.0.0:7000", "app:app" ]


# # Build the image
# sudo docker build --build-arg AWS_ACCESS_KEY_ID="....." --build-arg AWS_SECRET_ACCESS_KEY="....." --build-arg AWS_DEFAULT_REGION="......" --build-arg AWS_DEFAULT_OUTPUT="......" -t mosesdaudu001/demo-chatbot .

# # Deploy the image
# sudo docker run -it --rm -p 7000:7000 mosesdaudu001/demo-chatbot