import os
import asyncio
from threading import Thread

import ngrok
import requests
from flask import Flask, request, Response

from agentmail import AgentMail

def printColor(text, color):
    if color == "green":
        color_code = "\033[92m"
    elif color == "red":
        color_code = "\033[91m"
    elif color == "blue":
        color_code = "\033[94m"
    elif color == "yellow":
        color_code = "\033[93m"
    else:
        color_code = "\033[0m"

    print(color_code)
    print(text)
    print("\033[0m")



port = 8080
domain = os.getenv("WEBHOOK_DOMAIN")
inbox = f"feedback-agent@agentmail.to"

mcp_url = "http://localhost:8000"

listener = ngrok.forward(port, domain=domain, authtoken_from_env=True)
app = Flask(__name__)

client = AgentMail()


@app.route("/webhooks", methods=["POST"])
def receive_webhook():
    Thread(target=process_webhook, args=(request.json,)).start()
    return Response(status=200)

# currently has agent resummarize first
def send_initial_email(email):
    prompt = "You are an assistant tasked with gathering feedback. The following message contains a list of questions to ask various emails. Summarize the questions and the email list."
    prompt += f"email: {email['text']}"
    prompt += "Summarize the questions and the email list."

    printColor(f"Prompt:\n{prompt}\n", "green")

    # there's a refactor chance here
    url = "http://localhost:8000"
    payload = {"prompt": prompt}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        printColor(data["stdout"], "blue")
        printColor(data["stdout"], "blue")
        
        # code that sends emails to the specific agents
        followup_prompt = data["stdout"]
        followup_prompt += f"\nUsing the agent mail tool, send an email from the inbox id {inbox} to the previously mentioned emails. USE A NEW TOOL CALL FOR EACH EMAIL IN THE LIST." 

        printColor(followup_prompt, "green")

        payload = {"prompt": followup_prompt}
        response = requests.post(mcp_url, json=payload)
        response.raise_for_status()
        data = response.json()
        printColor(data["stdout"], "blue")

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


def send_summarize_email(email):
    prompt = "You are an assistant tasks with summarizing feedback. The following message contains a topic to search the inbox for:"
    prompt += f"email: {email['text']}"
    prompt += "Summarize the questions and the email list."

    printColor(f"Prompt:\n{prompt}\n", "green")

    # there's a refactor chance here
    payload = {"prompt": prompt}
    try:
        response = requests.post(mcp_url, json=payload)
        response.raise_for_status()
        data = response.json()
        printColor(data["stdout"], "blue")
        printColor(data["stdout"], "blue")
        
        # code that sends emails to the specific agents
        followup_prompt = data["stdout"]
        followup_prompt += f"\nUsing the agent mail tool, send an email from the inbox id {inbox} to the previously mentioned emails. USE A NEW TOOL CALL FOR EACH EMAIL IN THE LIST." 

        printColor(followup_prompt, "green")

        payload = {"prompt": followup_prompt}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        printColor(data["stdout"], "blue")

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

# multiple hooks will be going through this endpoint
def process_webhook(payload):
    global messages

    email = payload["message"]
    print(f"Received {email}")
    print(f"from: {email['from']}")
    print(f"subject: {email['subject']}")
    print(f"to: {email['to']}")

    if "feedback-agent@agentmail.to" in email['to']:
        print("email to feedback agent")
        if 'survey' in email['subject'].lower() and 'Re:' not in email['subject']:
            printColor(f"Received survey email:\n", "yellow")
            # send_initial_email()
        elif 'summarize' in email['subject'].lower():
            printColor(f"Received summarize email:\n", "yellow")





    # building a stateful situation to handle multiple kinds of commands

    # print(f"Received {email}")


#     prompt = f"""

if __name__ == "__main__":
    print(f"Inbox: {inbox}\n")

    app.run(port=port)
