import streamlit as st
import openai
import json
import requests
import os
openai.api_key = "OpenAI api key"

def send_email(email_id,subject,content):
  import smtplib
  from email.mime.text import MIMEText
  from email.mime.multipart import MIMEMultipart
  
  # Email configuration
  sender_email = 'Your gmail id'
  receiver_email = email_id
  password = 'Use an app-specific password for security'
  subject = subject
  message_body = content
  
  # Create a MIMEText object for the email message
  message = MIMEMultipart()
  message['From'] = sender_email
  message['To'] = receiver_email
  message['Subject'] = subject
  message.attach(MIMEText(message_body, 'plain'))
  
  # Connect to the SMTP server (for Gmail, use 'smtp.gmail.com')
  smtp_server = 'smtp.gmail.com'
  smtp_port = 587  # Use 465 for SSL or 587 for TLS
  
  try:
      server = smtplib.SMTP(smtp_server, smtp_port)
      server.starttls()
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message.as_string())
      server.quit()
      return('Email sent successfully')
  except Exception as e:
      return('Error sending email:', str(e))
  # Attach the message body

def run_conversation():
    functions = [
        {
            "name": "send_email",
            "description": "send an email to given email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_id":{
                        "type":"string",
                        "description":"The id of email."
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the email.",
                    },
                    "content":
                    {"type": "string", "description": "The content of the email."},
                },
                "required": ["email_id","subject","content"],
            },
        }]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=st.session_state.messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response["choices"][0]["message"]
    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "send_email": send_email
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response=function_to_call(
        email_id=function_args.get("email_id"),
        subject=function_args.get("subject"),
        content=function_args.get("content"))
        # Step 4: send the info on the function call and function response to GPT
        # extend conversation with assistant's reply
        st.session_state.messages.append(response_message)
        st.session_state.messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            })
        import time
        time.sleep(5)
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=st.session_state.messages)
        second_response=second_response["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": second_response})
        return second_response
    else:
        response_message = response_message["content"]
        st.session_state.messages.append({"role":"assistant","content":response_message})
        return response_message


if "messages" not in st.session_state.keys():
  st.session_state.messages = [{"role": "assistant", "content": "WellCome To AI Email Sender!"}]

if prompt := st.chat_input("Send Query..."): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
  
for message in st.session_state.messages: # Display the prior chat messages
      with st.chat_message(message["role"]):
        st.write(message["content"])


if st.session_state.messages[-1]["role"] != "assistant":
  with st.chat_message("assistant"):
    with st.spinner("Thinking..."):
      response_message = run_conversation()
      st.write(response_message)
