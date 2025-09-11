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

class TestPhases(unittest.TestCase):
    def test_greet(self):
        logging.info("Testing greet phase...")
        phase = bot.detect_phase("hello bot")
        self.assertEqual(phase, "greet")
        response = bot.get_response("hello bot")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_enum(self):
        logging.info("Testing enum phase...")
        phase = bot.detect_phase("enumerate s3 buckets")
        service = bot.detect_service("enumerate s3 buckets")
        self.assertEqual(phase, "enum")
        self.assertEqual(service, "s3")
        response = bot.get_response("enumerate s3 buckets")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_exploit(self):
        logging.info("Testing exploit phase...")
        phase = bot.detect_phase("there is a misconfiguration in the IAM policy")
        self.assertEqual(phase, "exploit")
        response = bot.get_response("there is a misconfiguration in the IAM policy")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_persist(self):
        logging.info("Testing persist phase...")
        phase = bot.detect_phase("setup a backdoor on ec2")
        self.assertEqual(phase, "persist")
        response = bot.get_response("setup a backdoor on ec2")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_exfil(self):
        logging.info("Testing exfil phase...")
        phase = bot.detect_phase("download ebs snapshot")
        service = bot.detect_service("download ebs snapshot")
        self.assertEqual(phase, "exfil")
        self.assertEqual(service, "ebs")
        response = bot.get_response("download ebs snapshot")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_default(self):
        logging.info("Testing default (unknown input)...")
        phase = bot.detect_phase("tell me a joke")
        self.assertEqual(phase, "default")
        response = bot.get_response("tell me a joke")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)