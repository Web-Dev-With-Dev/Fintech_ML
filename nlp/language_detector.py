import re
try:
    import langdetect
except ImportError:
    langdetect = None

class LanguageDetector:

    def __init__(self):
        self.language_map = {
            'hi': {'code': 'hi', 'name_en': 'Hindi', 'name_native': 'हिन्दी'},
            'en': {'code': 'en', 'name_en': 'English', 'name_native': 'English'},
            'hinglish': {'code': 'hinglish', 'name_en': 'Hinglish', 'name_native': 'Hinglish'},
            'ta': {'code': 'ta', 'name_en': 'Tamil', 'name_native': 'தமிழ்'},
            'te': {'code': 'te', 'name_en': 'Telugu', 'name_native': 'తెలుగు'},
            'bn': {'code': 'bn', 'name_en': 'Bengali', 'name_native': 'বাংলা'},
            'mr': {'code': 'mr', 'name_en': 'Marathi', 'name_native': 'मराठी'},
            'gu': {'code': 'gu', 'name_en': 'Gujarati', 'name_native': 'ગુજરાતી'},
            'unknown': {'code': 'unknown', 'name_en': 'Unknown', 'name_native': 'Unknown'}
        }

    def detect_script(self, text: str) -> str:
        if not text:
            return "Unknown"

        ranges = {
            'Devanagari': (0x0900, 0x097F),
            'Bengali': (0x0980, 0x09FF),
            'Gujarati': (0x0A80, 0x0AFF),
            'Tamil': (0x0B80, 0x0BFF),
            'Telugu': (0x0C00, 0x0C7F),
            'Latin': (0x0000, 0x007F)
        }

        script_counts = {script: 0 for script in ranges}

        for char in text:
            code = ord(char)
            for script, (start, end) in ranges.items():
                if start <= code <= end:
                    script_counts[script] += 1
                    break

        max_script = max(script_counts, key=script_counts.get)
        if script_counts[max_script] > 0:
            return max_script
        return "Unknown"

    def detect_language(self, text: str) -> str:
        script = self.detect_script(text)

        if script == 'Devanagari':
            if re.search(r'(आहे|नाही|झाले|करतो)\b', text):
                return 'mr'
            return 'hi'
        elif script == 'Tamil':
            return 'ta'
        elif script == 'Telugu':
            return 'te'
        elif script == 'Bengali':
            return 'bn'
        elif script == 'Gujarati':
            return 'gu'
        elif script == 'Latin':
            if langdetect:
                try:
                    lang = langdetect.detect(text)
                    if lang == 'en':
                        hinglish_keywords = {'hai', 'kya', 'karo', 'kar', 'bhi', 'se', 'ko', 'aur', 'nhi', 'nahi'}
                        words = set(text.lower().split())
                        if words.intersection(hinglish_keywords):
                            return 'hinglish'
                        return 'en'
                    elif lang in ['hi', 'mr', 'ne']:
                        return 'hinglish'
                except Exception:
                    pass

            hinglish_keywords = {'hai', 'kya', 'karo', 'kar', 'bhi', 'se', 'ko', 'aur', 'nhi', 'nahi'}
            words = set(text.lower().split())
            if words.intersection(hinglish_keywords):
                return 'hinglish'
            return 'en'

        return 'unknown'

    def get_language_name(self, lang_code: str) -> dict:
        return self.language_map.get(lang_code, self.language_map['unknown'])
