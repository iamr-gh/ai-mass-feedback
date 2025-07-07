import os
import re
from threading import Thread

import ngrok
import requests
from flask import Flask, request, Response

from utils import printColor

from agentmail import AgentMail

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

def ask_llm(prompt):
    payload = {"prompt": prompt}
    printColor(f"Prompt:\n{prompt}\n", "green")
    try:
        response = requests.post(mcp_url, json=payload)
        response.raise_for_status()
        data = response.json()
        printColor(data["stdout"], "blue")
        return data["stdout"]
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

# write a wrapper for this back and forth 
def send_initial_email(email_data):
    # for email extraction, use regex
    email_list = re.findall(r"[\w\.-]+@[\w\.-]+", email_data["text"])
    print("Found emails:")
    print(email_list)

    # remove all emails from the email text
    email_cleaned = re.sub(r"[\w\.-]+@[\w\.-]+", "", email_data["text"])
    email_cleaned = re.sub(r"\n", " ", email_cleaned)

    initial_prompt = "You are an assistant tasked with gathering feedback. The following message contains a list of questions.\n\n"
    initial_prompt += f"{email_cleaned}"
    initial_prompt += "\nSummarize the questions into a numbered list."

    try:
        initial_rsp = ask_llm(initial_prompt)

        # could add a uniqueness check later
        label_prompt = f"Output a fitting label for these questions:\n {initial_rsp}\n. ONLY RESPOND WITH ONE WORD, no spaces."
        label_rsp = ask_llm(label_prompt)

        label = label_rsp.strip().split(" ")[0]
        printColor(f"Label: {label}", "green")

        # now can manually write the for loop(this is kind of lame)
        for email in email_list:
            sender_prompt = f"You are an assistant tasked with gathering feedback. You are surveying users with the following questions:\n"
            sender_prompt += f"{initial_rsp}\n"
            sender_prompt += f"Using the agent mail tool, send an email from the inbox id {inbox} to the email {email} with the label {label}."
            # printColor(sender_prompt, "green")
            ask_llm(sender_prompt)


        # printColor(data["stdout"], "blue")
        
        # code that sends emails to the specific agents
        # followup_prompt = data["stdout"]
        # followup_prompt += f"\nUsing the agent mail tool, send an email from the inbox id {inbox} to the previously mentioned emails. USE A NEW TOOL CALL FOR EACH EMAIL IN THE LIST." 
        #
        # printColor(followup_prompt, "green")
        #
        # payload = {"prompt": followup_prompt}
        # response = requests.post(mcp_url, json=payload)
        # response.raise_for_status()
        # data = response.json()
        # printColor(data["stdout"], "blue")
    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


def send_summarize_email(email):
    prompt = "You are an assistant tasks with summarizing feedback. The following message contains a topic to search the inbox for:"
    prompt += f"email: {email['text']}"
    prompt += "Summarize the questions and the email list."

    printColor(f"Prompt:\n{prompt}\n", "green")



    payload = {"prompt": prompt}
    # try:


        # refactor to pull the email list out of the prompt, and then use for loop manually(remove the mcp from the loop)
        
        # code that sends emails to the specific agents
        # followup_prompt = data["stdout"]
        # followup_prompt += f"\nUsing the agent mail tool, send an email from the inbox id {inbox} to the previously mentioned emails. USE A NEW TOOL CALL FOR EACH EMAIL IN THE LIST." 
        #
        # printColor(followup_prompt, "green")
        #
        # payload = {"prompt": followup_prompt}
        # response = requests.post(url, json=payload)
        # response.raise_for_status()
        # data = response.json()
        # printColor(data["stdout"], "blue")

    # except requests.RequestException as e:
    #     print(f"HTTP Request failed: {e}")
    # except Exception as e:
    #     print(f"Error: {e}")

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
            send_initial_email()
        elif 'summarize' in email['subject'].lower():
            printColor(f"Received summarize email:\n", "yellow")


if __name__ == "__main__":
    print(f"Inbox: {inbox}\n")

    # app.run(port=port)

    # for testing, input directly into summarize email

    email = f"""
Emails: 
fb1@agentmail.to
fb2@agentmail.to
fb3@agentmail.to
fb4@agentmail.to
fb5@agentmail.to

Questions:
Who is your favorite actor?
What is your favorite movie?
At what age do you feel most comfortable watching movies?
How many movies do you watch per week?
Where is the best place to watch movies?
"""
    send_initial_email({"text": email})
