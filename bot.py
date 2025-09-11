import os
from dotenv import load_dotenv
import discord
import re
import random
import logging

# Logging
logging.basicConfig(
    filename="logs/pawang_hujan_bot.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

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
    # User finds/was given a potentially vulnerable AWS service
    "enum": [
        r"\b(find|list|discover(ed)?|enum(erate)?|given|found)\b"
    ],
    # User is certain the service is vulnerable and tries to find a way to escalate privilege
    "exploit": [
        r"\b(exploit|misconfig(uration)?|ssrf|leaked creds?|credential(s)?|bypass)\b",
        r"\b(privesc|privilege escalation|escalate|privilege|attach policy|vulnerable|vulnerability|write|permission)\b"
    ],
    # User is privileged, but desires to keep it
    "persist": [
        r"\b(persist(ence)?|backdoor|hidden|access key|keys?|maintain)\b"
    ],
    # User is privleged and desires to exfiltrate for data
    "exfil": [
        r"\b(exfil(tration)?|steal|copy|download|snapshot|sync|data)\b"
    ]
}

# Recognition for common AWS services (S3, EC2, EBS, IAM, DynamoDB, etc)
service_patterns = {
    "s3": r"\b(bucket|s3|object)\b",
    "ec2": r"\b(ec2|instance|compute|shell|machine image)\b",
    "iam": r"\b(iam|role|policy|user|creds?|credential(s)?)\b",
    "ebs": r"\b(ebs|snapshot|volume)\b",
    "cognito": r"\b(cognito|sign up|default)\b",
    "dynamodb": r"\b(dynamodb|database|nosql|table)\b",
    "lambda" :r"\b(lambda|function|serverless|application code|event)\b"
}

# Phase → responses
responses = {
    "greet": {
        "default": [
            "Hello hacker ;)",
            "Hi! Ready to pwn AWS?"
        ]
    },
    "default": {
        "default": [
            "I'm not quite sure what you're asking of. Try asking a cloud hacking question."
        ]
    },
    "enum": {
        "s3": [
            "You can enumerate S3 buckets with `aws s3 ls` or tools like cloud_enum / ScoutSuite.",
            "Try accessing the bucket you found: `http://bucket-name.s3.amazonaws.com/`."
        ],
        "ec2": [
            "Try running `aws ec2 describe-instances` and don't forget your region.",
            "Since EC2 machines are just virtual machines, try enumerating for open ports or other supported applications.",
            "If you have an AMI instead, try launching it and fish for credentials such as SSH keys or other credentials using `find / -name \"\credentials\"\ -type f`",
            "Check the instance's user data for hard-coded secrets."
        ],
        "iam": [
            "You can try: `aws iam list-users` or `aws iam list-roles`, and check attached policies.",
            "Try automating the enumereation process using tools like `enumerate-iam`.",
            "Interesting! Overly permissive IAM roles are common entry points. What else?"
        ],
        "ebs": [
            "EBS Enumeration: list snapshots with `aws ec2 describe-snapshots`.",
            "Public snapshots may contain sensitive data, including credentials. For faster credentials searching, use `trufflehog`."
        ],
        "cognito": [
            "Your first step should be collecting the user and identity pools.",
            "Enumerating for existing account might be possible if the `Prevent user existence errors` configuration is turned off. Even then, using `cognito:signUp` will still show the errors that differentiate between accounts that exist ot not."
        ],
        "default": [
            "You should consider general enumeration: start with IAM, S3, EC2, and networking.",
            "Did you know that tools like ScoutSuite and Pacu can automate cloud recon?"
        ]
    },
    "exploit": {
        "s3": [
            "Try the possibility of an older version existing.",
            "Another object of interest includes a database backup accidentally pushed to the bucket!",
            "If you have write access, try writing malicious code to get RCE."
        ],
        "ec2": [
            "If you have shell access, check the metadata service: `curl http://169.254.169.254/latest/meta-data/`.",
            "Common web vulnerabilities might be present in your EC2 instance, such as SSRF, SSTI, SQLI. Check OWASP Top 10.",
            "Check if your instance is vulnerable to arbitrary code execution."
        ],
        "iam": [
            "You should consider assuming some of the more promising roles.",
            "See if the leaked credential has access to other AWS services",
            "If you have write permission for the leaked policy, try changing it to give yourself a more escalated position.",
            "Try creating access keys for other users if your leaked role permits it.",
            "`iam:CreateServiceSpecificCredentials` or `iam:ResetServiceSpecificCredentials` can be used to create/reset default credentials for other AWS services.",
            "If you have the permission to do `iam:UploadSSHPublicKey` and `iam:DeactivateMFADevice`, you can bypass multi-factor authentication."
        ],
        "ebs": [
            "Did you know that you can copy the EBS snapshot block per block for offline analysis?",
            "Try seeing if you have the `ec2:CreateSnapshot` privilege to create a snapshot of an EC2 instance that you can download later."
        ],
        "cognito": [
            "Does it support default sign up? Try the `cognito-scanner` tool.",
            "You should try updating the cognito policy to allow basic authentication.",
            "Try creating a user, or updating the user's password to impersonate them."
        ],
        "default": [
            "You should follow the general exploitation path: test for SSRF → metadata service, privilege escalation, or leaked creds."
        ]
    },
    "persist": {
        "ec2": [
            "Use common backdoors such as a traditional rootkit.",
            "Try adding backdoor scripts from the user data if you have the write permission.",
            "To mitigate loss of network/VPC access, try setting up a VPN or VPC peering to directly connect to the vulnerable EC2's VPC"
        ],
        "iam": [
            "Try creating a new user that you can directly control",
            "Add a user you controlled to a privileged group", 
            "Grant extra permissions to users/groups you controlled through attached policies or inline policies", 
            "Disable MFA or add your own MFA device",
            "Try role chain juggling where you chain multiple `assume-role` commands extend the role's expiration"
        ],
        "dynamodb": [
            "You can add a Lambda function that will be triggered if any CRUD operation is applied to a DynamoDB database. This function can serve as your backdoor."
        ],
        "lambda": [
            "You can try creating a listener code that logs for any change in the `var/logs/nginx` folder",
            "Every time a new user is created, you can set up a lambda function that will be invoked to send the access keys to you"
        ],
        "default": [
            "Try the general persistance method such as adding yourself to a more privileged group permanently.",
            "Lambda functions are nice for persistance because you can run codes if an event is triggered"
        ]
    },
    "exfil": {
        "ec2": [
            "Copy the running instance since some of them might contain sensitive information such as environment secrets.",
            "Try DNS exfiltration, if you have no other access.",
            "Try applying port forwarding using the AWS-StartPortForwardingSession SSM document (no remote host parameter required)"
        ],
        "dynamodb": [
            "Use the `batch-get-item` if you want to download items from a table using its primary key",
            "Scan the whole table for interesting fields such as usernames and passwords.",
            "Backup the table to an S3 bucket you control using the `dynamodb:ExportTableToPointInTime` functionality"
        ],
        "ebs": [
            "Did you know that you can copy the EBS snapshot block per block for offline analysis?",
            "Public snapshots may contain sensitive data."
        ],
        "lambda":[
            "You can try accessing the default Lambda environment values in `/proc/self/environ`. This usually contains `AWS_SESSION_TOKEN`, `AWS_SECRET_ACCESS_KEY`, and `AWS_ACCESS_KEY_ID` for the Lambda function."
        ],
        "default": [
            "Some services you can try to exfiltrate data are EC2, DynamoDB, Lambda, and EBS."
        ]
    }
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
    return "default"

def detect_service(message: str):
    for service, pat in service_patterns.items():
        if re.search(pat, message, re.IGNORECASE):
            return service
    return "default"

def get_response(message: str):
    phase = detect_phase(message)
    if not phase:
        return None
    service = detect_service(message)
    possible_responses = responses.get(phase, {}).get(service, responses.get(phase, {}).get("default", []))
    if possible_responses:
        return random.choice(possible_responses)
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

if __name__ == "__main__":
    client.run(TOKEN)