import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import detect_phase, detect_service, get_response

SEMANTIC_KEYWORDS = {
    "greet": [
        r"\b(hi|hello|hey|greetings|morning|afternoon|evening)\b",
        r"\b(pwn|hacker|ready|aws)\b",
    ],
    "enum": [
        r"\b(enum|list|discover|find|found|scan|recon|enumerate)\b",
        r"\b(bucket|s3|object|public|http|access|sync)\b",
        r"\b(ec2|instance|compute|vm|ami|ports?|ssh|shell|metadata|userdata)\b",
        r"\b(iam|role|user|policy|group|identity|assume-?role)\b",
        r"\b(ebs|snapshot|volume|disk|storage)\b",
        r"\b(cognito|signup|userpool|identitypool)\b",
        r"\b(dynamodb|nosql|table|database|scan|export)\b",
    ],
    "exploit": [
        r"\b(exploit|misconfig(uration)?|vuln(erability)?|attack)\b",
        r"\b(privesc|privilege\s*escalation|escalate)\b",
        r"\b(ssrf|ssti|sqli|injection|rce|code\s*execution)\b",
        r"\b(leaked|creds?|credentials?|keys?)\b",
        r"\b(assume-?role|attach\s*policy|write\s*policy|access\s*key)\b",
        r"\b(snapshot\s*copy|offline\s*analysis)\b",
        r"\b(cognito|impersonate|change\s*password|scanner)\b",
    ],
    "persist": [
        r"\b(persist|persistence|backdoor|maintain|hidden)\b",
        r"\b(access\s*key|keys?|creds?|credentials?)\b",
        r"\b(rootkit|script|listener|event|trigger|vpn|peering)\b",
        r"\b(new\s*user|privileged\s*group|grant\s*permission|disable\s*mfa)\b",
        r"\b(lambda|logs?|invoked|scheduled|monitor)\b",
    ],
    "exfil": [
        r"\b(exfil|exfiltration|steal|dump|leak|copy|download|sync)\b",
        r"\b(data|datadump|sensitive|public\s*snapshots?)\b",
        r"\b(ec2|ami|dns\s*exfil|port\s*forward)\b",
        r"\b(dynamodb|batch-?get-?item|scan\s*table|export\s*table)\b",
        r"\b(ebs|snapshot|block\s*device|volume)\b",
        r"\b(lambda|proc/self/environ|session\s*token|secret\s*access)\b",
    ],
}


# Test cases: (user_input, expected_category)
test_cases = [
    ("hello bot", "greet"),
    ("enumerate s3 buckets", "enum"),
    ("we want to escalate privilage using iam", "exploit"),
    ("got persistence by invoking lambda function", "persist"),
    ("download ebs snapshot", "exfil"),
]

@pytest.mark.parametrize("user_input,expected_category", test_cases)
def test_response(user_input, expected_category):
    response = get_response(user_input)
    assert response is not None, f"No response for: {user_input}"

    # Check if response matches at least one synonym regex
    matched = any(
        __import__("re").search(pattern, response.lower())
        for pattern in SEMANTIC_KEYWORDS[expected_category]
    )
    assert matched, f"Expected '{expected_category}' semantics in: {response}"
