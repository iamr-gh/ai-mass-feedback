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

listener = ngrok.forward(port, domain=domain, authtoken_from_env=True)
app = Flask(__name__)

client = AgentMail()


@app.route("/webhooks", methods=["POST"])
def receive_webhook():
    Thread(target=process_webhook, args=(request.json,)).start()
    return Response(status=200)


def process_webhook(payload):
    global messages

    email = payload["message"]

    # print(f"Received {email}")

    prompt = "You are an assistant tasks with gathering feedback. The following message contains a list of questions to ask various emails. Summarize the questions and the email list."
    prompt += f"email: {email['text']}"
    prompt += "Summarize the questions and the email list."
    # one strategy could be to make the agent summarize things first

    # prompt += f"Using the agent mail tool, send an email from the inbox id {inbox} to the previously mentioned emails. USE A NEW TOOL CALL FOR EACH EMAIL IN THE LIST."

    # print prompt in a different color
    printColor(prompt, "green")

    # there's a refactor chance here
    url = "http://localhost:8000"
    payload = {"prompt": prompt}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        printColor(data["stdout"], "blue")
        printColor(data["stdout"], "blue")
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


#     prompt = f"""
# From: {email["from"]}
# Subject: {email["subject"]}
# Body:\n{email["text"]}
# """
# print("Prompt:\n\n", prompt, "\n")

# response = asyncio.run(Runner.run(agent, messages + [{"role": "user", "content": prompt}]))
# print("Response:\n\n", response.final_output, "\n")

# client.messages.reply(inbox_id=inbox, message_id=email["message_id"], text=response.final_output)

# messages = response.to_input_list()


if __name__ == "__main__":
    print(f"Inbox: {inbox}\n")

    app.run(port=port)
