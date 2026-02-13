import random
import os
import sys
import json
import subprocess
import asyncio
from datetime import datetime, timezone, timedelta
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
TELEGRAPH_URL = "https://api.telegra.ph"

HASHTAGS = "#факты #интересно #наука #удивительное"
CHANNEL_LINK = "AI_facts_vip"

CATEGORIES = [
    "космос и вселенная",
    "человеческое тело и мозг",
    "животные и природа",
    "история и древние цивилизации",
    "океан и подводный мир",
    "психология и поведение людей",
    "еда и кулинария",
    "технологии и изобретения",
    "языки и культуры мира",
    "математика и числа",
    "география и страны",
    "музыка и звуки",
    "спорт и рекорды",
    "деньги и экономика",
    "сон и сновидения",
    "цвета и зрение",
    "время и календари",
    "погода и климат",
    "микробы и бактерии",
    "мифы которые все считают правдой",
    "древний египет и пирамиды",
    "динозавры и вымершие животные",
    "черные дыры и звезды",
    "человеческая память",
    "самые странные законы в мире",
    "рекорды гиннесса",
    "тайны глубокого океана",
    "как работает мозг во сне",
    "удивительные способности животных",
    "изобретения которые изменили мир",
    "факты о днк и генетике",
    "самые опасные места на земле",
    "как работает гравитация",
    "тайны ancient рима",
    "факты о луне и солнце",
    "как устроен человеческий глаз",
    "самые маленькие страны мира",
    "удивительные растения",
    "факты о молниях и электричестве",
    "как работает интернет",
    "самые большие животные в истории",
    "факты о вулканах и землетрясениях",
    "тайны антарктиды",
    "как устроена вселенная",
    "факты о воде которые удивляют",
    "самые древние города мира",
    "как животные общаются друг с другом",
    "факты о скорости света",
    "удивительные совпадения в истории",
    "как работает искусственный интеллект",
]

POST_STYLES = [
    {
        "system": "Ты автор научно-популярного контента. Пишешь увлекательно и просто на русском. Говоришь на ты.",
        "prompt": "Напиши пост с удивительным фактом на тему: {topic}. Максимум 60 слов. Начни с 'А ты знал, что...' Объясни подробнее в 2-3 предложениях. В конце задай вопрос читателям.",
    },
    {
        "system": "Ты разрушитель мифов. Пишешь дерзко и увлекательно на русском.",
        "prompt": "Напиши пост-разоблачение мифа на тему: {topic}. Максимум 60 слов. Начни с '❌ Все думают что...' Потом '✅ На самом деле...' Коротко и мощно.",
    },
    {
        "system": "Ты автор контента о сравнениях и масштабах на русском.",
        "prompt": "Напиши пост со сравнением на тему: {topic}. Максимум 60 слов. Покажи что-то привычное в необычном масштабе. Удиви читателя цифрами или сравнением.",
    },
    {
        "system": "Ты рассказчик удивительных историй об открытиях на русском.",
        "prompt": "Расскажи короткую удивительную историю открытия на тему: {topic}. Максимум 60 слов. Начни сразу с действия. Кто открыл, как это было.",
    },
    {
        "system": "Ты автор топ-списков с фактами на русском.",
        "prompt": "Напиши 3 невероятных факта на тему: {topic}. Максимум 60 слов. Пронумеруй 1️⃣ 2️⃣ 3️⃣. Каждый факт одно предложение. В конце спроси какой удивил больше.",
    },
]


def call_groq(system, prompt):
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 300,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print("Groq error:", resp.text)
        return None
    return resp.json()["choices"][0]["message"]["content"]


def generate_post(topic):
    style = random.choice(POST_STYLES)
    return call_groq(style["system"], style["prompt"].format(topic=topic))


def generate_quote(topic):
    return call_groq(
        "Ты создаешь короткие удивительные факты на русском.",
        "Напиши один удивительный факт на тему: " + topic + ". Одно предложение. Максимум 15 слов. Без кавычек. Начни с существительного."
    )


def generate_voice_text(topic):
    return call_groq(
        "Ты ведущий научно-популярного подкаста. Говоришь увлекательно на русском.",
        "Напиши текст для голосового сообщения с удивительным фактом на тему: " + topic + ". 2-3 предложения. Максимум 40 слов. Без кавычек. Начни с обращения к слушателю."
    )


def create_voice(text):
    try:
        import edge_tts

        async def do_tts():
            communicate = edge_tts.Communicate(text, "ru-RU-DmitryNeural")
            await communicate.save("voice.mp3")

        asyncio.run(do_tts())
        print("MP3 created!")

        if not os.path.exists("voice.mp3"):
            print("MP3 file not found")
            return False

        result = subprocess.run(
            ["ffmpeg", "-y", "-i", "voice.mp3", "-c:a", "libopus", "-b:a", "64k", "voice.ogg"],
            timeout=30,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("FFmpeg error:", result.stderr)
            return False

        print("OGG created!")
        return os.path.exists("voice.ogg")

    except Exception as e:
        print("Voice error:", e)
        return False


def send_voice_to_telegram(file_path):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendVoice"
    with open(file_path, "rb") as f:
        files = {"voice": f}
        data = {"chat_id": CHANNEL_ID}
        resp = requests.post(url, data=data, files=files, timeout=30)
    return resp.json()


def send_photo_to_telegram(photo_url, caption):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendPhoto"
    payload = {"chat_id": CHANNEL_ID, "photo": photo_url, "caption": caption}
    return requests.post(url, json=payload, timeout=30).json()


def send_to_telegram(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text, "disable_web_page_preview": False}
    return requests.post(url, json=payload, timeout=30).json()


def generate_article(topic):
    return call_groq(
        "Ты автор научно-популярного блога. Пишешь увлекательно и просто. Без канцелярита. Говоришь на ты.",
        "Напиши статью 200-300 слов с удивительными фактами на тему: " + topic + ". Начни с интригующего вопроса. 3-4 абзаца. В конце: Подписывайся на Telegram канал https://t.me/" + CHANNEL_LINK + " — удивительные факты каждый день!"
    )


def publish_to_telegraph(title, content):
    acc = requests.get(TELEGRAPH_URL + "/createAccount", params={
        "short_name": "FactsBot",
        "author_name": "Факты и интересности",
        "author_url": "https://t.me/" + CHANNEL_LINK,
    }, timeout=30).json()

    if not acc.get("ok"):
        return None

    token = acc["result"]["access_token"]
    paragraphs = content.split("\n")
    nodes = []
    for p in paragraphs:
        p = p.strip()
        if p:
            nodes.append({"tag": "p", "children": [p]})

    page = requests.post(TELEGRAPH_URL + "/createPage", data={
        "access_token": token,
        "title": title,
        "author_name": "Факты и интересности",
        "author_url": "https://t.me/" + CHANNEL_LINK,
        "content": json.dumps(nodes),
        "return_content": "false",
    }, timeout=30).json()

    if page.get("ok"):
        return page["result"]["url"]
    return None


def main():
    print("=== FACTS BOT START ===")

    if not TELEGRAM_BOT_TOKEN or not CHANNEL_ID or not GROQ_API_KEY:
        print("ERROR: env vars not set")
        sys.exit(1)

    topic = random.choice(CATEGORIES)
    print("Topic:", topic)

    msk = timezone(timedelta(hours=3))
    hour = datetime.now(msk).hour
    if 5 <= hour < 12:
        greeting = "🌅 Утренний факт!"
    elif 12 <= hour < 17:
        greeting = "🧠 Факт дня!"
    elif 17 <= hour < 22:
        greeting = "🌆 Вечерний факт!"
    else:
        greeting = "🌙 Факт на ночь!"

    # 1. Голосовое
    print("Generating voice text...")
    voice_text = generate_voice_text(topic)
    if voice_text:
        print("Voice text:", voice_text)
        print("Creating audio...")
        if create_voice(voice_text):
            print("Sending voice...")
            vr = send_voice_to_telegram("voice.ogg")
            if vr.get("ok"):
                print("Voice sent!")
            else:
                print("Voice send error:", vr)

    # 2. Картинка
    print("Generating quote...")
    quote = generate_quote(topic)
    if quote:
        print("Quote:", quote)
        photo_url = "https://picsum.photos/800/500?random=" + str(random.randint(1, 99999))
        pr = send_photo_to_telegram(photo_url, "🧠 " + quote)
        if pr.get("ok"):
            print("Photo sent!")

    # 3. Текст
    print("Generating post...")
    content = generate_post(topic)
    if not content:
        print("Post generation failed")
        sys.exit(1)

    full_post = greeting + "\n\n" + content + "\n\n" + HASHTAGS

    # 4. Telegraph
    print("Generating article...")
    article = generate_article(topic)
    if article:
        tg_url = publish_to_telegraph(topic.capitalize(), article)
        if tg_url:
            full_post += "\n\n📖 Подробнее: " + tg_url
            print("Telegraph:", tg_url)

    print("Sending post...")
    result = send_to_telegram(full_post)

    if result.get("ok"):
        print("SUCCESS!")
    else:
        print("ERROR:", result)
        sys.exit(1)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
