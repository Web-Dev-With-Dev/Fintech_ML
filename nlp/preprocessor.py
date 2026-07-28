import re
import random
import unicodedata

STOPWORDS = {
    'hi': ['है', 'के', 'में', 'की', 'और', 'से', 'को', 'का', 'एक'],
    'en': ['the', 'is', 'in', 'at', 'of', 'and', 'a', 'to', 'for'],
    'hinglish': ['hai', 'ke', 'me', 'ki', 'aur', 'se', 'ko', 'ka', 'ek'],
    'ta': ['மற்றும்', 'ஒரு', 'என்று', 'இந்த'],
    'te': ['మరియు', 'ఒక', 'అని', 'ఈ'],
    'bn': ['এবং', 'একটি', 'যে', 'এই'],
    'mr': ['आणि', 'एक', 'की', 'हे'],
    'gu': ['અને', 'એક', 'કે', 'આ']
}

class TextPreprocessor:

    def clean(self, text: str, lang: str) -> str:
        text = unicodedata.normalize('NFKC', text)

        if lang in ['en', 'hinglish']:
            text = text.lower()

        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def remove_urls(self, text: str) -> tuple[str, list[str]]:
        url_pattern = r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        urls_found = re.findall(url_pattern, text)
        cleaned_text = re.sub(url_pattern, '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        return cleaned_text, urls_found

    def extract_phone_numbers(self, text: str) -> list[str]:
        phone_pattern = r'(?:(?:\+|0{0,2})91[\s-]*)?[6789]\d{2}[\s-]*\d{3}[\s-]*\d{4}'
        phones = re.findall(phone_pattern, text)
        normalized_phones = [re.sub(r'[^\d+]', '', p) for p in phones]
        return normalized_phones

    def extract_amounts(self, text: str) -> list[float]:
        amount_pattern = r'(?:(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d{1,2})?))|([\d,]+(?:\.\d{1,2})?)\s*(?:rupees|rs)'
        matches = re.findall(amount_pattern, text, flags=re.IGNORECASE)
        amounts = []
        for match in matches:
            amt_str = match[0] if match[0] else match[1]
            try:
                amt_float = float(amt_str.replace(',', ''))
                amounts.append(amt_float)
            except ValueError:
                continue
        return amounts

    def inject_noise(self, text: str, noise_level: float = 0.1) -> str:
        if not text:
            return text

        chars = list(text)
        num_noisy_chars = int(len(chars) * noise_level)

        for _ in range(num_noisy_chars):
            idx = random.randint(0, max(0, len(chars) - 1))
            if not chars:
                break
            action = random.choice(['delete', 'swap', 'typo'])

            if action == 'delete' and len(chars) > 1:
                chars.pop(idx)
            elif action == 'swap' and idx < len(chars) - 1:
                chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
            elif action == 'typo':
                if chars[idx].isalpha() and chars[idx].isascii():
                    chars[idx] = 'x'

        return ''.join(chars)

    def get_features(self, text: str, lang: str) -> dict:
        cleaned_text, urls = self.remove_urls(text)
        cleaned_text = self.clean(cleaned_text, lang)
        phones = self.extract_phone_numbers(text)
        amounts = self.extract_amounts(text)

        return {
            'cleaned_text': cleaned_text,
            'urls': urls,
            'has_urls': len(urls) > 0,
            'phone_numbers': phones,
            'has_phone_numbers': len(phones) > 0,
            'amounts': amounts,
            'max_amount': max(amounts) if amounts else 0.0,
            'text_length': len(text)
        }
