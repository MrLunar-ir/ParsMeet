 نصب

```bash
pip install ParsMeet
```

شروع سریع

```python
import ParsMeet

bot = ParsMeet.Bot(token="توکن شما")

@bot.on_message_all()
def handler(data):
    chat_id = data["chat_id"]
    text = data["text"]
    if text == "/start":
        bot.send_message(chat_id, "سلام! خوش آمدید.")

bot.run()
```

امکانات کلیدی

· ارسال و دریافت پیام (متن، عکس، فایل، ویرایش، حذف، ریپلای)
· دکمه‌های شیشه‌ای (Inline Keyboard) با سازنده‌ی هوشمند KeyboardBuilder
· هوش مصنوعی (رایگان و یا از طریق OpenAI)
· مدیریت گروه (بن، آنبن، وارن با سیستم ۳ اخطاره، سکوت، سنجاق)
· فیلتر تبلیغات و اسپم (تشخیص خودکار لینک و کلمات نامناسب)
· سیستم نرخ محدودیت (Rate Limit) برای جلوگیری از اسپم
· کش (Cache) برای ذخیره‌سازی موقت
· یادآورها (Reminders) با زمان‌بندی خودکار
· کامندهای سفارشی (Custom Commands) که کاربر می‌تواند به راحتی اضافه کند
· کامندهای کنسول برای مدیریت ربات از ترمینال

کامندهای سفارشی

با استفاده از متد bot.add_new_custom_cmds() در کنسول، می‌توانید کامندهای جدیدی به فایل custom_cmds.py اضافه کنید.

```python
# custom_cmds.py
def setup(bot):
    @bot.command("test")
    def test_command(data):
        bot.send_message(data["chat_id"], "پاسخ تست!")
```

کامندهای کنسول

· bot.off() – خاموش کردن ربات
· bot.pause() – مکث
· bot.on() – ادامه
· bot.filter.on() – فعال‌سازی فیلتر تبلیغات
· bot.filter.off() – غیرفعال‌سازی فیلتر
· broadcast <message> – ارسال پیام همگانی
· send <user_id> <message> – ارسال به کاربر خاص
· ask <question> – پرسش از هوش مصنوعی
· bot.add_new_custom_cmds() – افزودن کامند جدید

