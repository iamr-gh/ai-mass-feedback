import random
import requests
import os
from agentmail import AgentMail

from utils import printColor, find_highest_number_in_string

emails = [
    "fb1@agentmail.to",
    "fb2@agentmail.to",
    "fb3@agentmail.to",
    "fb4@agentmail.to",
    "fb5@agentmail.to",
]

def random_prompt(email_data, email, message_id):
    tone = random.choice(["optimistic", "pessimistic", "cautious", "confident"])

    # input email should have a list of questions
    number = random.randint(1, max(find_highest_number_in_string(email_data), 3))

    prompt = f"""
    You are a member of the public who has just received the following email:
        {email_data}

    ONLY ANSWER question #{str(number)}, offering a {tone} perspective.
    """
    return prompt

client = AgentMail()
mcp_url = "http://localhost:8000"

for email in emails:
    # grab recent emails
    # for each one, grab all messages and run the prompt
    print(f"Getting emails from {email}")
    data = client.inboxes.messages.list(inbox_id=email,)

    for message in data.messages:
        # only respond to feedback agent currently
        if "feedback-agent@agentmail.to" not in message.from_:
            print(f"Skipping message from {message.from_}")
            continue

        if "random-responder" in message.labels:
            print(f"Skipping message from {message.from_} already responded")
            continue

        id = message.message_id

        msg_data = client.inboxes.messages.get(inbox_id=email, message_id=id)
        email_data = msg_data.text

        prompt = random_prompt(email_data, email,id)
        printColor(f"Prompt:\n{prompt}\n", "green")
        rsp = requests.post(mcp_url, json={"prompt": prompt})
        rsp.raise_for_status()
        data = rsp.json()
        printColor(data["stdout"], "blue")

        client.inboxes.messages.update(inbox_id=email,message_id=id,add_labels=["random-responder"])
