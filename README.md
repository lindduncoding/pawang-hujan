# Pawang Hujan

A pattern-matching based Discord chatbot as your companion in doing cloud (AWS) pentesting. Integrated using the [discord.py](https://discordpy.readthedocs.io/en/stable/) library. Ready to alter the weather today? 

**WARNING!**
Only hack clouds you are permitted to. I am NOT responsible for any shenanigans towards your corpo's infrastructure.

Made for an NLP course we took as undergraduates.

## Setup

1. Clone the repo and move to the working directory
```
git clone https://github.com/lindduncoding/pawang-hujan.git
cd pawang-hujan
```

2. Make a virtual environment and activate it 
```
python -m venv .venv
source .venv/bin/activate
```

3. Install requirements
```
pip install -r requirements.txt
```

4. Create your first Discord Bot/Application by followin this [documentation](https://discordpy.readthedocs.io/en/stable/discord.html).

5. Using the `.env.example` file, make your .env file where you store your Discord Bot token.

6. Run the application by doing 
```
python3 bot.py
```

## Intuition

The intuition behind the rules lies on the fact that the penetration testing (pentesting) process is, most of the time, *predictable*. Therefore, it's **possible to map** the pentesting process into a **simple rule chain.** To make the rules more robust, we matched user inputs using regular expression to classify the pentesting process (enumerating, exploiting, persisting, exfiltrating) and to classify the specific AWS service the user is interested in (EC2, S3, IAM, Cognito, DynamoDB, Lambda, EBS).

However, real life pentesting process **might not always be this predictable** since business logic might vary from one company to another. Apart from that, different jurisdiction and therefore data protection laws will also add to the variability. In conclusion, *this tool shouldn't be used in production* as it is just a fun class project to learn about the basics of chatbots. 

## Demonstration

## Team

- Bot developer: Fidelya Fredelina (22/496507/TK/54405)
- Bot knowledge organizer: Fidelya Fredelina (22/496507/TK/54405)