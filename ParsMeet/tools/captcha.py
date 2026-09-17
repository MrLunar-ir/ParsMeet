import random
import string

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class Captcha:
    def __init__(self, cache, ttl=120):
        self.cache = cache
        self.ttl = ttl

    def generate(self, user_id):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.cache.set(f"captcha_{user_id}", code, ttl=self.ttl)
        return code

    def verify(self, user_id, user_input):
        saved = self.cache.get(f"captcha_{user_id}")
        if saved and user_input.strip().upper() == saved:
            self.cache.delete(f"captcha_{user_id}")
            return True
        return False

    def create_image(self, code, path='/tmp/captcha.png'):
        if not PIL_AVAILABLE:
            return ""
        img = Image.new('RGB', (200, 100), color=(230, 230, 230))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
        for _ in range(8):
            draw.line([(random.randint(0, 200), random.randint(0, 100)), (random.randint(0, 200), random.randint(0, 100))], fill=(200, 0, 0), width=1)
        draw.text((20, 30), code, font=font, fill=(0, 0, 0))
        img.save(path)
        return path