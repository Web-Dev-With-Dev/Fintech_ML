import pandas as pd
import random
import os
import re

class ScamDataGenerator:
    def __init__(self):
        self.languages = ['English', 'Hindi', 'Hinglish', 'Tamil', 'Telugu', 'Bengali', 'Marathi', 'Gujarati']
        self.categories = ['OTP fraud', 'account block threat', 'prize/lottery', 'KYC update', 'fake loan offer', 'government scheme fraud', 'bank impersonation']
        
        self.safe_templates = {
            'English': [
                "Dear Customer, your A/C {ac_num} is credited with INR {amount} on {date}. Info: {info}. Available Bal INR {bal} - SBI",
                "Your A/C {ac_num} has a debit by transfer of Rs {amount} on {date}. Avl Bal Rs {bal}. - HDFC Bank",
                "Rs {amount} debited from a/c {ac_num} on {date} to VPA {vpa}. Not you? Call 1800XXXX - PNB",
                "Update: A/c {ac_num} credited by Rs {amount} on {date} via IMPS. Bal: Rs {bal}. - ICICI Bank",
                "Your salary of Rs {amount} has been credited to your account {ac_num} on {date}. - Axis Bank"
            ],
            'Hindi': [
                "प्रिय ग्राहक, आपके बैंक खाते {ac_num} में {date} को {amount} रुपये जमा किए गए हैं। कुल राशि {bal} - SBI",
                "आपके खाते {ac_num} से {date} को {amount} रुपये निकाले गए हैं। शेष राशि {bal} रुपये - HDFC",
                "खाता {ac_num} में {date} को {amount} रुपये का डेबिट हुआ। शेष {bal} - PNB",
                "आपके A/c {ac_num} में {date} को वेतन के रूप में {amount} रुपये जमा हुए। - BOI",
                "नमस्कार, आपके खाते {ac_num} से UPI द्वारा {amount} रुपये का भुगतान सफल रहा। - ICICI"
            ],
            'Hinglish': [
                "Dear customer, aapke account {ac_num} me Rs {amount} credit hue hai {date} ko. Avl Bal Rs {bal} - SBI",
                "Aapke a/c {ac_num} se Rs {amount} deduct hue hai {date} ko. Bal Rs {bal} - HDFC",
                "Rs {amount} transfer hue a/c {ac_num} se {vpa} ko {date} par. - PNB",
                "Aapka salary Rs {amount} a/c {ac_num} me credit ho gaya hai {date} ko. - Axis",
                "Aapke khate {ac_num} se Rs {amount} ka UPI payment successful raha. - ICICI"
            ]
        }
        
        for lang in ['Tamil', 'Telugu', 'Bengali', 'Marathi', 'Gujarati']:
            self.safe_templates[lang] = [
                f"Safe bank msg in {lang} for A/c {{ac_num}} debited INR {{amount}}",
                f"Safe bank msg in {lang} for A/c {{ac_num}} credited INR {{amount}}"
            ]
            
        self.scam_templates = {
            'English': {
                'OTP fraud': [
                    "Dear user, your HDFC bank account points are expiring today. Click {url} to redeem and share OTP {otp}",
                    "SBI ALERT: Your account will be blocked. Share OTP {otp} with our executive to verify your identity.",
                    "Complete your KYC verification now. Open link {url} and enter OTP {otp} sent to your phone.",
                    "Your credit card limit has been increased. Reply with OTP {otp} to activate the new limit immediately."
                ],
                'account block threat': [
                    "URGENT: Your SBI account {ac_num} has been SUSPENDED due to incomplete KYC. Update immediately at {url} to avoid freeze.",
                    "Dear Customer, your PNB PAN is not updated. Your A/C will be blocked in 24hrs. Update via {url}",
                    "Your HDFC NetBanking is locked due to multiple failed attempts. Click {url} to unlock.",
                    "ALERT: Income tax department has blocked your bank accounts. Pay penalty fee at {url} immediately."
                ],
                'prize/lottery': [
                    "Congratulations! You have won KBC lottery of Rs {amount}. Send WhatsApp message to {phone} to claim.",
                    "Jio Lucky Draw: Your mobile number has won a TATA Safari. Pay registration fee of Rs 5000 at {url}",
                    "You are the lucky winner of iPhone 14 Pro Max! Click {url} to provide delivery address and pay shipping fee.",
                    "Amazon 10th Anniversary prize: Rs {amount} cash! Claim your reward now at {url}"
                ],
                'KYC update': [
                    "Dear Customer, your Bank KYC is pending. Update PAN card now at {url} otherwise A/c will be closed.",
                    "RBI Alert: Mandatory KYC update required for your PayTM wallet. Complete within 24h at {url}",
                    "Update your Aadhaar with your bank account immediately to prevent blocking. Visit {url}",
                    "HDFC Bank KYC Update: Dear user, update your documents at {url} to continue using services."
                ],
                'fake loan offer': [
                    "Pre-approved loan of Rs {amount} from Bajaj Finance is ready for disbursal. Zero interest! Click {url}",
                    "Need instant cash? Get upto Rs 5,00,000 in 5 mins without CIBIL score. Download app {url}",
                    "Congratulations! Your Mudra loan of Rs {amount} is approved. Pay processing fee of Rs 2000 at {url}",
                    "Instant personal loan approved! No documentation. Claim now {url}"
                ],
                'government scheme fraud': [
                    "PM Kisan Samman Nidhi: Rs {amount} has been approved for you. Click {url} to receive in bank.",
                    "Govt Free Laptop Scheme 2024: Register your details and pay Rs 500 courier fee at {url}",
                    "Your Covid relief fund of Rs 10000 is pending. Fill the form at {url} to get it today.",
                    "Claim your LPG subsidy directly in bank account. Verify details at {url}"
                ],
                'bank impersonation': [
                    "Dear SBI User, your account has unusual login attempt. Verify your credentials at {url}",
                    "HDFC Bank Support: We noticed suspicious activity on your credit card. Call {phone} to secure it.",
                    "ICICI Alert: Your reward points worth Rs {amount} are expiring today. Redeem at {url}",
                    "Dear customer, you have requested a money transfer of Rs {amount}. If not you, click {url} to cancel."
                ]
            }
        }
        
        for lang in ['Hindi', 'Hinglish', 'Tamil', 'Telugu', 'Bengali', 'Marathi', 'Gujarati']:
            self.scam_templates[lang] = {}
            for cat in self.categories:
                self.scam_templates[lang][cat] = [
                    f"Scam {cat} msg in {lang} variant 1: Click {url} or call {phone}",
                    f"Scam {cat} msg in {lang} variant 2: Pay Rs {amount} at {url}",
                    f"Scam {cat} msg in {lang} variant 3: Your account {ac_num} is blocked. Link: {url}",
                    f"Scam {cat} msg in {lang} variant 4: Share OTP {otp} for {cat}"
                ]
                
    def _inject_noise(self, text: str) -> str:
        noise_level = random.random()
        if noise_level < 0.2:
            emojis = ["🚨", "⚠️", "💸", "🎁", "📱", "🏧"]
            text = f"{random.choice(emojis)} {text} {random.choice(emojis)}"
        elif noise_level < 0.4:
            subs = {'a': '@', 'o': '0', 'i': '1', 's': '$', 'e': '3'}
            for k, v in subs.items():
                if random.random() < 0.3:
                    text = text.replace(k, v)
        elif noise_level < 0.6:
            if len(text) > 5:
                idx = random.randint(1, len(text)-2)
                text = text[:idx] + text[idx+1] + text[idx] + text[idx+2:]
        return text
        
    def _fill_template(self, template: str) -> str:
        ac_num = f"XX{random.randint(1000, 9999)}"
        amount = random.randint(1000, 500000)
        bal = amount + random.randint(1000, 100000)
        date = f"{random.randint(1, 28)}/{random.randint(1, 12)}/2024"
        info = f"Ref No {random.randint(1000000, 9999999)}"
        vpa = f"{random.randint(9000000000, 9999999999)}@ybl"
        url = f"http://{random.choice(['update', 'kyc', 'reward', 'secure'])}-{random.choice(['sbi', 'hdfc', 'pnb'])}.com"
        otp = f"{random.randint(100000, 999999)}"
        phone = f"+91{random.randint(7000000000, 9999999999)}"
        
        try:
            return template.format(
                ac_num=ac_num, amount=amount, bal=bal, date=date, 
                info=info, vpa=vpa, url=url, otp=otp, phone=phone
            )
        except KeyError:
            return template

    def generate_scam_samples(self, n: int, category: str, language: str) -> list[dict]:
        samples = []
        templates = self.scam_templates.get(language, {}).get(category, [])
        if not templates:
            templates = self.scam_templates['English'][category]
            
        for _ in range(n):
            template = random.choice(templates)
            text = self._fill_template(template)
            text = self._inject_noise(text)
            
            samples.append({
                'text': text,
                'language': language,
                'category': category,
                'label': 'SCAM',
                'urgency_level': random.randint(3, 5),
                'scam_type': category
            })
        return samples

    def generate_safe_samples(self, n: int, language: str) -> list[dict]:
        samples = []
        templates = self.safe_templates.get(language, self.safe_templates['English'])
        
        for _ in range(n):
            template = random.choice(templates)
            text = self._fill_template(template)
            
            samples.append({
                'text': text,
                'language': language,
                'category': 'legitimate bank alert',
                'label': 'SAFE',
                'urgency_level': random.randint(1, 2),
                'scam_type': 'None'
            })
        return samples

    def generate_full_dataset(self, total_samples: int = 50000) -> pd.DataFrame:
        print(f"Generating {total_samples} samples...")
        samples = []
        
        safe_count = total_samples // 2
        scam_count = total_samples - safe_count
        
        safe_per_lang = safe_count // len(self.languages)
        for lang in self.languages:
            samples.extend(self.generate_safe_samples(safe_per_lang, lang))
            
        scam_per_lang_cat = scam_count // (len(self.languages) * len(self.categories))
        for lang in self.languages:
            for cat in self.categories:
                samples.extend(self.generate_scam_samples(scam_per_lang_cat, cat, lang))
                
        remainder = total_samples - len(samples)
        if remainder > 0:
            samples.extend(self.generate_safe_samples(remainder, 'English'))
            
        random.shuffle(samples)
        return pd.DataFrame(samples)

    def save_dataset(self, df: pd.DataFrame, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Dataset saved to {path}")

if __name__ == "__main__":
    generator = ScamDataGenerator()
    dataset = generator.generate_full_dataset(total_samples=50000)
    
    output_path = r"G:\Hackathon\Fintech_ML\FinShield\data_engine\datasets\scam_sms_dataset.csv"
    generator.save_dataset(dataset, output_path)
    
    print("\n--- Dataset Statistics ---")
    print(f"Total samples: {len(dataset)}")
    print("\nLabel Distribution:")
    print(dataset['label'].value_counts())
    print("\nLanguage Distribution:")
    print(dataset['language'].value_counts())
    print("\nCategory Distribution:")
    print(dataset['category'].value_counts())
