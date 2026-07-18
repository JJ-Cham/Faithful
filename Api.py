import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IslamicAPIService:
    ALADHAN_BASE_URL = os.getenv("ALADHAN_API_BASE_URL", "https://api.aladhan.com/v1")
    UMMAH_API_KEY = os.getenv("UMMAH_API_KEY")
    MAPS_KEY = os.getenv("MAPS_PLACES_API_KEY")
    TIMEOUT_LIMIT = 5.0

    @classmethod
    def get_prayer_times_and_date(cls, latitude, longitude, method=3):
        current_date = datetime.now().strftime("%d-%m-%Y")
        url = f"{cls.ALADHAN_BASE_URL}/timings/{current_date}"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "method": method
        }
        try:
            response = requests.get(url, params=params, timeout=cls.TIMEOUT_LIMIT)
            if response.status_code == 200:
                payload = response.json()
                data = payload.get("data", {})
                timings = data.get("timings", {})
                hijri_data = data.get("date", {}).get("hijri", {})
                formatted_hijri = f"{hijri_data.get('day')} {hijri_data.get('month', {}).get('en')} {hijri_data.get('year')} AH"
                return {
                    "status": "success",
                    "prayer_times": {
                        "Fajr": timings.get("Fajr"),
                        "Dhuhr": timings.get("Dhuhr"),
                        "Asr": timings.get("Asr"),
                        "Maghrib": timings.get("Maghrib"),
                        "Isha": timings.get("Isha")
                    },
                    "hijri_date": formatted_hijri
                }
            logger.error(f"API Error Code: {response.status_code}")
        except requests.exceptions.RequestException as error:
            logger.error(f"Network Failure: {str(error)}")
        return cls._get_prayer_fallback_data()

    @classmethod
    def _get_prayer_fallback_data(cls):
        return {
            "status": "fallback",
            "prayer_times": {
                "Fajr": "05:00",
                "Dhuhr": "13:30",
                "Asr": "17:00",
                "Maghrib": "20:15",
                "Isha": "21:45"
            },
            "hijri_date": "Date Unavailable"
        }

    @staticmethod
    def get_verified_daily_reminder():
        return {
            "content": "Verily, with hardship, there is relief.",
            "surah_verse": "Surah Al-Inshirah [94:5]",
            "source": "The Holy Qur'an (Sahih International Translation)",
            "disclaimer": "This content is purely educational and does not constitute or replace formal religious rulings (fatwas)."
        }

    @staticmethod
    def get_verified_quiz_questions():
        return [
            {
                "id": 1,
                "question": "How many obligatory (Fard) prayers are performed by Muslims daily?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "5",
                "explanation": "Muslims perform 5 daily mandatory prayers: Fajr, Dhuhr, Asr, Maghrib, and Isha.",
                "source": "Sahih al-Bukhari & Sahih Muslim"
            },
            {
                "id": 2,
                "question": "In which Islamic month is fasting during the daytime mandatory?",
                "options": ["Muharram", "Ramadan", "Shawwal", "Dhul-Hijjah"],
                "correct_answer": "Ramadan",
                "explanation": "Fasting during the holy month of Ramadan is the fourth pillar of Islam.",
                "source": "Surah Al-Baqarah [2:185]"
            },
            {
                "id": 3,
                "question": "What is the direction towards the Kaaba in Mecca called?",
                "options": ["Qibla", "Mihrab", "Minbar", "Hijra"],
                "correct_answer": "Qibla",
                "explanation": "The Qibla is the fixed direction facing the Kaaba in Mecca that Muslims turn to during prayer.",
                "source": "Surah Al-Baqarah [2:144]"
            },
            {
                "id": 4,
                "question": "Which pillar of Islam refers to the mandatory giving of charity to the poor?",
                "options": ["Shahada", "Salah", "Zakat", "Hajj"],
                "correct_answer": "Zakat",
                "explanation": "Zakat represents a fixed percentage portion of wealth given away to designated charitable categories.",
                "source": "Surah At-Tawbah [3:60]"
            },
            {
                "id": 5,
                "question": "What is the historical migration of Prophet Muhammad (PBUH) from Mecca to Medina known as?",
                "options": ["Isra", "Mi'raj", "Hijrah", "Fath"],
                "correct_answer": "Hijrah",
                "explanation": "The Hijrah marks the foundational migration of early Muslims and the start of the Islamic lunar calendar tracking.",
                "source": "Ar-Raheeq Al-Makhtoom (The Sealed Nectar)"
            }
        ]

    @staticmethod
    def get_mock_community_data(religion_choice):
        mock_database = {
            "Islam": [
                {"name": "Central Community Masjid", "address": "123 Faith Way, Atlanta, GA", "distance": "1.2 miles", "phone": "404-555-0199"},
                {"name": "Downtown Islamic Center", "address": "789 Peace St, Atlanta, GA", "distance": "3.5 miles", "phone": "404-555-0142"}
            ],
            "Christianity": [
                {"name": "Grace Fellowship Church", "address": "456 Hope Blvd, Atlanta, GA", "distance": "2.1 miles", "phone": "404-555-0122"}
            ],
            "Judaism": [
                {"name": "B'nai Israel Synagogue", "address": "555 Shalom Dr, Atlanta, GA", "distance": "4.0 miles", "phone": "404-555-0177"}
            ]
        }
        return mock_database.get(religion_choice, [])
if __name__ == "__main__":
    print("--- STARTING API LIVE TESTS ---")
    
    # Test Atlanta coordinates
    test_lat, test_lon = 33.7490, -84.3880
    
    print(f"\n[TEST 1] Fetching live prayer times for Lat: {test_lat}, Lon: {test_lon}...")
    prayer_result = IslamicAPIService.get_prayer_times_and_date(test_lat, test_lon)
    print(f"Status: {prayer_result['status']}")
    print(f"Hijri Date: {prayer_result['hijri_date']}")
    print(f"Timings: {prayer_result['prayer_times']}")
    
    print("\n[TEST 2] Verifying static secure reminder structural data...")
    reminder = IslamicAPIService.get_verified_daily_reminder()
    print(f"Content: {reminder['content']}")
    print(f"Source Verification: {reminder['source']}")
    
    print("\n[TEST 3] Loading five verified quiz modules...")
    questions = IslamicAPIService.get_verified_quiz_questions()
    print(f"Total Questions Loaded: {len(questions)}")
    print(f"Sample Question 1: {questions[0]['question']}")
    print(f"Sample 1 Source: {questions[0]['source']}")
    
    print("\n[TEST 4] Loading community finder structural layout data...")
    places = IslamicAPIService.get_mock_community_data("Islam")
    print(f"Found {len(places)} local places for Islam layout tracking.")
    
    print("\n--- ALL TESTS COMPLETED ---")