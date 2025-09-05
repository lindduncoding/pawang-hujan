import os
from dotenv import load_dotenv
import discord
import re
import random

# Load Bot's Token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Phase regex patterns
phase_patterns = {
    "greet": [
        r"\b(hi|hello|hey|hi|greetings|morning|evening|afternoon)\b"
    ],
    "enum": [
        r"\b(find|list|discover|enum(erate)?)\b",
        r"\b(bucket|account|recon|scan)\b"
    ],
    "exploit": [
        r"\b(exploit|misconfig(uration)?|ssrf|leaked creds?|credential(s)?)\b",
        r"\b(privesc|privilege escalation|attach policy|iam)\b"
    ],
    "post": [
        r"\b(post(-)?exploitation?|dump|secrets?|parameter store|lambda|pivot|sts)\b"
    ],
    "persist": [
        r"\b(persist(ence)?|backdoor|hidden|access key|keys?)\b"
    ],
    "exfil": [
        r"\b(exfil(tration)?|steal|copy|download|snapshot|sync|data)\b"
    ]
}

# Phase → responses
phase_responses = {
    "greet": [
        "Hello hacker ;)",
        "Hi! Ready to pwn AWS?"
    ],
    "enum": [
        "You should start enumeration: try `aws iam list-users` and `aws iam list-roles`.",
        "Enumerate S3 buckets with `aws s3 ls` or tools like cloud_enum / ScoutSuite."
    ],
    "exploit": [
        "Since you found creds, you should check their validity with `aws sts get-caller-identity`.",
        "If permissions allow `iam:AttachUserPolicy`, you can escalate to admin!"
    ],
    "post": [
        "Time for post-exploitation: dump secrets with `aws secretsmanager list-secrets`.",
        "You could also pivot using STS assume-role into other accounts."
    ],
    "persist": [
        "For persistence, create new IAM access keys or attach an admin policy to a low-privileged user.",
        "Another trick: deploy a hidden Lambda backdoor."
    ],
    "exfil": [
        "To exfiltrate, sync S3 buckets with `aws s3 sync`.",
        "Snapshot EBS volumes to pull data offline."
    ]
}

# Simple pronoun/persona detection
def detect_pronoun(message: str):
    msg = message.lower()
    if re.search(r"\bi\b|\bme\b|\bmy\b", msg):
        return "user"
    elif re.search(r"\bwe\b|\bours?\b", msg):
        return "group"
    elif re.search(r"\byou\b", msg):
        return "direct"
    return "neutral"

def adapt_response(response: str, pronoun: str):
    if pronoun == "user":
        return response.replace("you", "you").replace("Your", "Your")
    elif pronoun == "group":
        return response.replace("you", "your team").replace("You", "Your team")
    elif pronoun == "direct":
        return response.replace("you", "I").replace("You", "I")
    else:
        return response

def detect_phase(message: str):
    for phase, patterns in phase_patterns.items():
        for pat in patterns:
            if re.search(pat, message, re.IGNORECASE):
                return phase
    return None

def get_response(message: str):
    phase = detect_phase(message)
    if phase and phase in phase_responses:
        response = random.choice(phase_responses[phase])
        pronoun = detect_pronoun(message)
        return adapt_response(response, pronoun)
    return None

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    response = get_response(message.content)
    if response:
        await message.channel.send(response)

client.run(TOKEN)