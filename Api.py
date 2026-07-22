import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RELIGION_KEYWORD_MAP = {
    "Islam": "mosque OR islamic center",
    "Christianity": "church OR cathedral",
    "Judaism": "synagogue OR Jewish community center",
    "Hinduism": "Hindu temple OR mandir",
    "Buddhism": "Buddhist temple OR monastery",
    "Sikhism": "gurdwara OR Sikh temple"
}

RELIGION_LEARNING_CONTENT = {
    "Islam": {
        "quotes": [
            {
                "text": "Indeed, with hardship comes ease.",
                "citation": "Qur'an 94:6",
                "source": "Sahih International translation",
            },
            {
                "text": (
                    "Allah does not burden a soul beyond that "
                    "it can bear."
                ),
                "citation": "Qur'an 2:286",
                "source": "Sahih International translation",
            },
        ],
        "facts": [
            {
                "title": "Five daily prayers",
                "text": (
                    "The obligatory prayers are Fajr, Dhuhr, "
                    "Asr, Maghrib, and Isha."
                ),
                "source": "Sahih al-Bukhari and Sahih Muslim",
            },
            {
                "title": "Ramadan",
                "text": (
                    "Muslims fast during Ramadan, the month in "
                    "which the Qur'an was revealed."
                ),
                "source": "Qur'an 2:185",
            },
            {
                "title": "Qibla",
                "text": (
                    "During prayer, Muslims face the Kaaba in "
                    "Makkah. This direction is called the Qibla."
                ),
                "source": "Qur'an 2:144",
            },
        ],
    },

    "Christianity": {
        "quotes": [
            {
                "text": "Blessed are the peacemakers.",
                "citation": "Matthew 5:9",
                "source": "King James Version",
            },
            {
                "text": "Thou shalt love thy neighbour as thyself.",
                "citation": "Mark 12:31",
                "source": "King James Version",
            },
        ],
        "facts": [
            {
                "title": "Two main sections",
                "text": (
                    "The Christian Bible is commonly organized "
                    "into the Old Testament and New Testament."
                ),
                "source": "The Holy Bible",
            },
            {
                "title": "Communion",
                "text": (
                    "Communion, also called the Eucharist, "
                    "remembers Jesus' Last Supper with his disciples."
                ),
                "source": "1 Corinthians 11:23–26",
            },
            {
                "title": "Easter",
                "text": (
                    "Easter commemorates the resurrection of Jesus."
                ),
                "source": (
                    "Matthew 28; Mark 16; Luke 24; John 20"
                ),
            },
        ],
    },

    "Judaism": {
        "quotes": [
            {
                "text": "Justice, justice shalt thou pursue.",
                "citation": "Deuteronomy 16:20",
                "source": "JPS 1917 translation",
            },
            {
                "text": "Love thy neighbour as thyself.",
                "citation": "Leviticus 19:18",
                "source": "JPS 1917 translation",
            },
        ],
        "facts": [
            {
                "title": "The Torah",
                "text": (
                    "The Torah contains the first five books "
                    "of the Hebrew Bible."
                ),
                "source": "The Tanakh",
            },
            {
                "title": "Shabbat",
                "text": (
                    "Shabbat is the weekly day of rest, beginning "
                    "on Friday evening and continuing through Saturday."
                ),
                "source": (
                    "Exodus 20:8–11 and Jewish tradition"
                ),
            },
            {
                "title": "The synagogue",
                "text": (
                    "A synagogue can serve as a place for prayer, "
                    "study, and community gathering."
                ),
                "source": "Jewish Encyclopedia",
            },
        ],
    },

    "Hinduism": {
        "quotes": [
            {
                "text": "Yoga is skill in action.",
                "citation": "Bhagavad Gita 2:50",
                "source": "Bhagavad Gita",
            },
            {
                "text": "The Self is the friend of the self.",
                "citation": "Bhagavad Gita 6:5",
                "source": "Bhagavad Gita",
            },
        ],
        "facts": [
            {
                "title": "Many traditions",
                "text": (
                    "Hinduism includes many schools, practices, "
                    "and regional traditions rather than a single "
                    "founder or creed."
                ),
                "source": "Encyclopaedia Britannica",
            },
            {
                "title": "The Bhagavad Gita",
                "text": (
                    "The Bhagavad Gita is a dialogue within "
                    "the Mahabharata."
                ),
                "source": "The Mahabharata",
            },
            {
                "title": "Diwali",
                "text": (
                    "Diwali is a festival of lights observed by "
                    "many Hindu communities and some other South "
                    "Asian traditions."
                ),
                "source": "Encyclopaedia Britannica",
            },
        ],
    },

    "Buddhism": {
        "quotes": [
            {
                "text": "Hatred is never appeased by hatred.",
                "citation": "Dhammapada 5",
                "source": "The Dhammapada",
            },
            {
                "text": "All conditioned things are impermanent.",
                "citation": "Dhammapada 277",
                "source": "The Dhammapada",
            },
        ],
        "facts": [
            {
                "title": "The Buddha",
                "text": (
                    "Siddhartha Gautama became known as the Buddha, "
                    "meaning the Awakened One."
                ),
                "source": "Encyclopaedia Britannica",
            },
            {
                "title": "Four Noble Truths",
                "text": (
                    "The Four Noble Truths explain suffering, "
                    "its origin, its ending, and the path leading "
                    "to its ending."
                ),
                "source": "Dhammacakkappavattana Sutta",
            },
            {
                "title": "Eightfold Path",
                "text": (
                    "The Noble Eightfold Path brings together "
                    "ethical conduct, mental discipline, and wisdom."
                ),
                "source": "Dhammacakkappavattana Sutta",
            },
        ],
    },

    "Sikhism": {
        "quotes": [
            {
                "text": "No one is my enemy, no one a stranger.",
                "citation": "Guru Granth Sahib, Ang 1299",
                "source": "Sri Guru Granth Sahib",
            },
            {
                "text": "Recognize the whole human race as one.",
                "citation": "Akal Ustat",
                "source": "Guru Gobind Singh",
            },
        ],
        "facts": [
            {
                "title": "Origins in Punjab",
                "text": (
                    "Sikhism began in the Punjab region with "
                    "Guru Nanak in the fifteenth century."
                ),
                "source": "Encyclopaedia Britannica",
            },
            {
                "title": "Living Guru",
                "text": (
                    "Sikhs regard the Guru Granth Sahib as "
                    "the eternal Guru."
                ),
                "source": "Sri Guru Granth Sahib",
            },
            {
                "title": "Langar",
                "text": (
                    "Langar is a free community meal traditionally "
                    "open to everyone, regardless of background."
                ),
                "source": "Sikh Rehat Maryada",
            },
        ],
    },

    "Other": {
        "quotes": [
            {
                "text": (
                    "Learning begins with respectful curiosity."
                ),
                "citation": "Faithful community principle",
                "source": "Faithful",
            },
        ],
        "facts": [
            {
                "title": "Start with primary sources",
                "text": (
                    "When exploring a tradition, begin with its own "
                    "texts, institutions, and community voices."
                ),
                "source": "Faithful learning guideline",
            },
            {
                "title": "Ask respectful questions",
                "text": (
                    "Practices can differ across denominations, "
                    "schools, cultures, and local communities."
                ),
                "source": "Faithful learning guideline",
            },
            {
                "title": "Keep learning local",
                "text": (
                    "A nearby community can provide context that "
                    "a short online summary cannot."
                ),
                "source": "Faithful learning guideline",
            },
        ],
    },
}
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

    # @classmethod
    # def get_live_community_places(cls, religion_choice, latitude, longitude):
    #     if not cls.MAPS_KEY or cls.MAPS_KEY.startswith("mock_"):
    #         logger.info("Using mock community data (No valid Google Maps key configured).")
    #         return cls.get_mock_community_data(religion_choice)

    #     search_query = RELIGION_KEYWORD_MAP.get(religion_choice, "place of worship")
    #     url = "https://places.googleapis.com/v1/places:searchText"
        
    #     headers = {
    #         "Content-Type": "application/json",
    #         "X-Goog-Api-Key": cls.MAPS_KEY,
    #         "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.googleMapsUri"
    #     }

    #     payload = {
    #         "textQuery": search_query,
    #         "locationBias": {
    #             "circle": {
    #                 "center": {
    #                     "latitude": latitude,
    #                     "longitude": longitude
    #                 },
    #                 "radius": 15000.0
    #             }
    #         }
    #     }

    #     try:
    #         response = requests.post(url, json=payload, headers=headers, timeout=cls.TIMEOUT_LIMIT)
    #         if response.status_code == 200:
    #             results = response.json().get("places", [])
    #             places_list = []
                
    #             for place in results:
    #                 places_list.append({
    #                     "name": place.get("displayName", {}).get("text", "N/A"),
    #                     "address": place.get("formattedAddress", "Address Unavailable"),
    #                     "phone": place.get("nationalPhoneNumber", "N/A"),
    #                     "maps_link": place.get("googleMapsUri", "#")
    #                 })
    #             return places_list
                
    #         logger.error(f"Google Places API Error: {response.status_code}")
    #     except requests.exceptions.RequestException as error:
    #         logger.error(f"Google Places Request Failed: {str(error)}")

    #     return cls.get_mock_community_data(religion_choice)

    @classmethod
    def get_live_community_places(
        cls,
        religion_choice,
        latitude,
        longitude,
        city=None,
    ):
        if not cls.MAPS_KEY or cls.MAPS_KEY.startswith("mock_"):
            logger.info(
                "Using mock community data "
                "(No valid Google Maps key configured)."
            )
            return cls.get_mock_community_data(
                religion_choice,
                city,
            )

        search_query = RELIGION_KEYWORD_MAP.get(
            religion_choice,
            "place of worship",
        )

        url = "https://places.googleapis.com/v1/places:searchText"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": cls.MAPS_KEY,
            "X-Goog-FieldMask": (
                "places.displayName,"
                "places.formattedAddress,"
                "places.nationalPhoneNumber,"
                "places.googleMapsUri"
            ),
        }

        payload = {
            "textQuery": search_query,
            "maxResultCount": 5,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": 15000.0,
                }
            },
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=cls.TIMEOUT_LIMIT,
            )

            if response.status_code == 200:
                results = response.json().get("places", [])[:5]
                places_list = []

                for place in results:
                    places_list.append(
                        {
                            "name": place.get(
                                "displayName",
                                {},
                            ).get("text", "N/A"),
                            "address": place.get(
                                "formattedAddress",
                                "Address unavailable",
                            ),
                            "phone": place.get(
                                "nationalPhoneNumber",
                                "N/A",
                            ),
                            "maps_link": place.get(
                                "googleMapsUri",
                                "#",
                            ),
                        }
                    )

                return places_list

            logger.error(
                "Google Places API Error: %s - %s",
                response.status_code,
                response.text,
            )

        except requests.exceptions.RequestException as error:
            logger.error(
                "Google Places Request Failed: %s",
                str(error),
            )

        return cls.get_mock_community_data(
            religion_choice,
            city,
        )
    
    @classmethod
    def get_religion_learning_content(cls, religion_choice):
        """Return a rotating reflection and sourced learning facts."""

        content_key = (
            religion_choice
            if religion_choice in RELIGION_LEARNING_CONTENT
            else "Other"
        )

        content = RELIGION_LEARNING_CONTENT[content_key]
        quotes = content["quotes"]

        day_number = datetime.now().timetuple().tm_yday
        quote_index = (day_number - 1) % len(quotes)

        return {
            "religion": religion_choice or "Other",
            "is_supported": content_key != "Other",
            "quote": quotes[quote_index],
            "facts": content["facts"],
            "disclaimer": (
                "This learning preview is educational. Practices and "
                "interpretations can vary across communities."
            ),
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
                "source": "Surah At-Tawbah [9:60]"
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
    def get_mock_community_data(religion_choice, city=None):
        city_name = city or "your area"

        mock_database = {
            "Islam": [
                {
                    "name": f"Central Community Masjid of {city_name}",
                    "address": f"123 Faith Way, {city_name}",
                    "distance": "1.2 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                },
                {
                    "name": f"{city_name} Islamic Center",
                    "address": f"789 Peace Street, {city_name}",
                    "distance": "3.5 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                },
            ],
            "Christianity": [
                {
                    "name": f"Grace Fellowship of {city_name}",
                    "address": f"456 Hope Boulevard, {city_name}",
                    "distance": "2.1 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                }
            ],
            "Judaism": [
                {
                    "name": f"{city_name} Community Synagogue",
                    "address": f"555 Shalom Drive, {city_name}",
                    "distance": "4.0 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                }
            ],
            "Hinduism": [
                {
                    "name": f"{city_name} Hindu Temple",
                    "address": f"210 Dharma Road, {city_name}",
                    "distance": "2.8 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                }
            ],
            "Buddhism": [
                {
                    "name": f"{city_name} Buddhist Center",
                    "address": f"88 Mindful Lane, {city_name}",
                    "distance": "3.1 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                }
            ],
            "Sikhism": [
                {
                    "name": f"{city_name} Gurdwara",
                    "address": f"34 Seva Street, {city_name}",
                    "distance": "4.2 miles",
                    "phone": "Not available",
                    "maps_link": "#",
                }
            ],
        }

        return mock_database.get(religion_choice, [])
    # @staticmethod
    # def get_mock_community_data(religion_choice):
    #     mock_database = {
    #         "Islam": [
    #             {"name": "Central Community Masjid", "address": "123 Faith Way, Atlanta, GA", "distance": "1.2 miles", "phone": "404-555-0199", "maps_link": "#"},
    #             {"name": "Downtown Islamic Center", "address": "789 Peace St, Atlanta, GA", "distance": "3.5 miles", "phone": "404-555-0142", "maps_link": "#"}
    #         ],
    #         "Christianity": [
    #             {"name": "Grace Fellowship Church", "address": "456 Hope Blvd, Atlanta, GA", "distance": "2.1 miles", "phone": "404-555-0122", "maps_link": "#"}
    #         ],
    #         "Judaism": [
    #             {"name": "B'nai Israel Synagogue", "address": "555 Shalom Dr, Atlanta, GA", "distance": "4.0 miles", "phone": "404-555-0177", "maps_link": "#"}
    #         ]
    #     }
    #     return mock_database.get(religion_choice, [])


if __name__ == "__main__":
    print("--- STARTING API LIVE TESTS ---")

    print("--- TESTING GOOGLE PLACES COMMUNITY FINDER ---")
    test_lat, test_lon = 33.7490, -84.3880
    test_religion = "Islam"
    
    print(f"\nSearching places of worship for '{test_religion}' near Lat: {test_lat}, Lon: {test_lon}...")
    results = IslamicAPIService.get_live_community_places(test_religion, test_lat, test_lon)
    
    print(f"\nTotal Places Found: {len(results)}")
    for idx, place in enumerate(results, start=1):
        print(f"\n[{idx}] {place['name']}")
        print(f"    Address: {place['address']}")
        print(f"    Phone:   {place['phone']}")
        print(f"    Link:    {place.get('maps_link', '#')}")
        
    print("\n--- GOOGLE PLACES TEST COMPLETE ---")
    
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