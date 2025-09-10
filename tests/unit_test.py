import unittest
import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import bot

# Logging
logging.basicConfig(
    filename="../logs/test_logs.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

class TestDetection(unittest.TestCase):
    def test_phase_detection(self):
        self.assertEqual(bot.detect_phase("hello"), "greet")
        self.assertEqual(bot.detect_phase("enumerate s3 buckets"), "enum")
        self.assertEqual(bot.detect_phase("there's misconfiguration in the iam policy"), "exploit")
        self.assertEqual(bot.detect_phase("got persistence via lambda"), "persist")
        self.assertEqual(bot.detect_phase("download ebs snapshot"), "exfil")

    def test_service_detection(self):
        self.assertEqual(bot.detect_service("s3 bucket enumeration"), "s3")
        self.assertEqual(bot.detect_service("ec2 instance metadata"), "ec2")
        self.assertEqual(bot.detect_service("ebs snapshot leak"), "ebs")
        self.assertEqual(bot.detect_service("iam role escalation"), "iam")
        self.assertEqual(bot.detect_service("lambda function exfil"), "lambda")

class TestResponses(unittest.TestCase):
    def test_responses_exist_for_all(self):
        for phase, services in bot.responses.items():
            for service, replies in services.items():
                self.assertIsInstance(replies, list)
                self.assertTrue(len(replies) > 0, f"No replies for {phase}:{service}")

class TestIntegration(unittest.TestCase):
    def test_get_response_smoke(self):
        msg = type("MockMessage", (), {"content": "enumerate s3 buckets"})()
        response = bot.get_response(msg.content)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)