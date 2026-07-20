import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Api import IslamicAPIService

class TestIslamicAPIService(unittest.TestCase):

    def test_google_places_live(self):
        test_lat, test_lon = 33.7490, -84.3880
        religion = "Islam"
        
        results = IslamicAPIService.get_live_community_places(religion, test_lat, test_lon)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn("name", results[0])
        self.assertIn("address", results[0])

    def test_prayer_times(self):
        test_lat, test_lon = 33.7490, -84.3880
        response = IslamicAPIService.get_prayer_times_and_date(test_lat, test_lon)
        
        self.assertIn("status", response)
        self.assertIn("prayer_times", response)
        self.assertIn("hijri_date", response)

    def test_verified_reminder(self):
        reminder = IslamicAPIService.get_verified_daily_reminder()
        self.assertIn("content", reminder)
        self.assertIn("source", reminder)

    def test_verified_quiz_questions(self):
        questions = IslamicAPIService.get_verified_quiz_questions()
        self.assertEqual(len(questions), 5)
        self.assertIn("question", questions[0])
        self.assertIn("correct_answer", questions[0])

    def test_mock_community_fallback(self):
        places = IslamicAPIService.get_mock_community_data("Islam")
        self.assertGreater(len(places), 0)
        self.assertIn("name", places[0])

if __name__ == "__main__":
    unittest.main()