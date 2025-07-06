import random
import os
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

emails = [
    "fb1@agentmail.to",
    "fb2@agentmai.to",
    "fb3@agentmail.to",
    "fb4@agentmail.to",
    "fb5@agentmail.to",
]


def random_prompt(email):
    tone = random.choice(["optimistic", "pessimistic", "cautious", "confident"])

    # definitely a smarter way to do this without needing to do anything custom
    number = random.randint(1, 10)

    prompt = f"""
    You are a member of the public who has just received the following email:
        {email}

    ONLY ANSWER question #{str(number)}, offering a {tone} perspective.
    """

    return prompt

# don't need to serve anything, just basically myself give the current situation
client = AgentMail()

print(client.inboxes.list())
print(client.inboxes.messages.list(inbox_id="fb1@agentmail.to",))

for email in emails:
    # grab recent emails
    # for each one, grab all messages and run the prompt
    print(f"Getting emails from {email}")
    data = client.inboxes.messages.list(inbox_id=email,)

    for message in data["messages"]:
        # if message["timestamp"] < datetime.datetime.now() - datetime.timedelta(days=30):
        # add filters later

        id = message["message_id"]

        # get rest of message data
        msg_data = client.inboxes.messages.get(inbox_id=email, message_id=id)

        email_data = msg_data["text"]

        prompt = random_prompt(email_data)
        printColor(f"Prompt:\n{prompt}\n", "green")
