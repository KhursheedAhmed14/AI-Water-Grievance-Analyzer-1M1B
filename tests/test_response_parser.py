"""
tests/test_response_parser.py
Unit tests for core.response_parser
"""

import unittest
from core.response_parser import parse_response, REQUIRED_KEYS


class TestResponseParser(unittest.TestCase):
    def test_a_valid_json(self):
        """Test parsing plain valid JSON."""
        raw = """{
            "summary": "Water pipeline leakage on Main Street.",
            "category": "Pipeline Leakage",
            "severity": "High",
            "priority": "Urgent",
            "location": "Main Street",
            "duration": "2 days",
            "affected_people": "50 households",
            "key_facts": ["Leakage on Main Street", "Ongoing for 2 days"],
            "missing_info": "Contact details"
        }"""
        res = parse_response(raw)
        for key in REQUIRED_KEYS:
            self.assertIn(key, res)
        self.assertEqual(res["category"], "Pipeline Leakage")
        self.assertEqual(res["severity"], "High")
        self.assertEqual(res["priority"], "Urgent")
        self.assertEqual(res["key_facts"], ["Leakage on Main Street", "Ongoing for 2 days"])

    def test_b_fenced_json(self):
        """Test parsing ```json fenced JSON."""
        raw = r"""```json
        {
            "summary": "No water supply in sector 4.",
            "category": "Water Supply Disruption",
            "severity": "Medium",
            "priority": "High",
            "location": "Sector 4",
            "duration": "Unclear",
            "affected_people": "Unclear",
            "key_facts": "[\"No water in sector 4\"]",
            "missing_info": "Duration"
        }
        ```"""
        res = parse_response(raw)
        self.assertEqual(res["category"], "Water Supply Disruption")
        self.assertEqual(res["severity"], "Medium")
        self.assertEqual(res["priority"], "High")
        self.assertEqual(res["key_facts"], ["No water in sector 4"])

    def test_c_json_preceded_by_text(self):
        """Test parsing JSON preceded and followed by explanatory text."""
        raw = """Here is the structured analysis of the grievance:

        {
            "summary": "Low water pressure in residential area.",
            "category": "Low Water Pressure",
            "severity": "Low",
            "priority": "Low",
            "location": "Park View",
            "duration": "1 week",
            "affected_people": "Entire building",
            "key_facts": "Low pressure reported",
            "missing_info": "None identified"
        }

        Hope this analysis is helpful!"""
        res = parse_response(raw)
        self.assertEqual(res["category"], "Low Water Pressure")
        self.assertEqual(res["severity"], "Low")
        self.assertEqual(res["priority"], "Low")
        self.assertEqual(res["key_facts"], ["Low pressure reported"])

    def test_d_malformed_non_json(self):
        """Test handling malformed / non-JSON response."""
        raw = "I cannot analyze this complaint because it is invalid text."
        res = parse_response(raw)
        self.assertEqual(res["summary"], "Could not parse AI response.")
        self.assertEqual(res["category"], "Other / Unclear")
        self.assertEqual(res["severity"], "Unclear")
        self.assertEqual(res["priority"], "Unclear")
        self.assertIn("raw_response", res)
        self.assertEqual(res["raw_response"], raw)

    def test_enum_validation_and_defaults(self):
        """Test invalid enums fall back safely to defaults."""
        raw = """{
            "summary": "Pipeline problem",
            "category": "Invalid Category",
            "severity": "Invalid Severity",
            "priority": "Invalid Priority",
            "location": "Area 51",
            "duration": "1 day",
            "affected_people": "10",
            "key_facts": ["Fact 1"],
            "missing_info": "None"
        }"""
        res = parse_response(raw)
        self.assertEqual(res["category"], "Other / Unclear")
        self.assertEqual(res["severity"], "Unclear")
        self.assertEqual(res["priority"], "Unclear")
        self.assertEqual(res["key_facts"], ["Fact 1"])


if __name__ == "__main__":
    unittest.main()
