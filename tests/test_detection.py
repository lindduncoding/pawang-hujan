import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot import detect_phase, detect_service, get_response

@pytest.mark.parametrize("msg,expected_phase", [
    ("hello bot", "greet"),
    ("list all buckets", "enum"),
    ("leaked creds detected", "exploit"),
    ("set up persistence with a backdoor", "persist"),
    ("time to exfiltrate some data", "exfil"),
])
def test_phase_detection(msg, expected_phase):
    assert detect_phase(msg) == expected_phase

@pytest.mark.parametrize("msg,expected_service", [
    ("s3 bucket exposed", "s3"),
    ("got into an ec2 instance", "ec2"),
    ("iam role compromised", "iam"),
    ("snapshot of an ebs volume", "ebs"),
    ("default cognito sign up", "cognito"),
    ("nosql dynamodb table", "dynamodb"),
    ("lambda function abused", "lambda"),
])
def test_service_detection(msg, expected_service):
    assert detect_service(msg) == expected_service
