import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import random
import tempfile
import httpx
from dotenv import load_dotenv

load_dotenv()

# ============================================
# ZIU — ROAST GIRL BOT (ElevenLabs Real Voice)
# ============================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ElevenLabs Voice IDs — Real girl voices
# "Sarah" — natural Indian-English girl voice
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah voice

class ZiuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.active_channels = set()

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced!")

bot = ZiuBot()

# ============================================
# ROAST LINES
# ============================================

ROAST_TEMPLATES = [
    "Haan haan, tune kaha {msg}. Wah kya baat! Mujhe laga kuch akal wali baat bolega, par nahi. Bilkul typical.",
    "Tune kaha {msg}. Yeh sun ke mera IQ dus point gir gaya. Tu khush hai apne aap se?",
    "Oye tune kaha {msg}. Aur main soch rahi thi tu boring nahi hoga. Galat thi main, bilkul galat.",
    "Tune kaha {msg}. Seriously? Bhai teri soch itni choti hai ki ant bhi na ghuse usme.",
    "Arre tune kaha {msg}. Yeh sun ke mujhe neend aa gayi. Tu sleeping pill se bhi zyada effective hai.",
    "Tune kaha {msg}. Aur tune socha main impress ho jaungi? Cute try tha, par nahi.",
    "Oh ho, {msg} bola! Waah waah! Genius ho tum bilkul. Nahi, bilkul bhi nahi.",
    "Tune kaha {msg}. Aur mujhe laga koi C grade movie ka dialogue bol raha hai.",
]

GENERIC_ROASTS = [
    "Teri personality kisi pirated website se download ki lagti hai. Full of bugs, zero quality.",
    "Tu itna useless hai ki WiFi bhi tujhse better connection deta hai.",
    "Tera confidence aur teri aukat mein Mariana Trench jitna farak hai, samjha?",
    "Tu itna slow hai ki kachhua bhi tujhe overtake kar ke chala gaya zindagi mein.",
    "Teri personality giving error char sau chaar, personality not found.",
    "Tu ek loading screen ki tarah hai jo kabhi complete nahi hoti.",
    "Tera dimag Chrome browser ki tarah hai, saintalis tabs open, sab crash.",
    "Main tujhe roast karna chahti thi par phir realize kiya tu khud ek joke hai.",
    "Bhai teri smartness ka level airplane mode pe hai, completely off.",
    "Tujhe dekh ke lagta hai evolution ne teri file skip kar di thi.",
]

INTROS = [
    "Ohhh tune kuch bola? Chal sun le mujhse.",
    "Achha achha, toh yeh baat hai? Sun zara.",
    "Haye haye, kya bola tune. Chal main samjhati hoon.",
    "Oh sweetie, really? Okay, sun.",
    "Aa gaya firse bolne. Chal roast time.",
    "Teri baat suni maine. Ab meri sun.",
]

OUTROS = [
    "Samjha? Nahi samjha? Expected. Bye.",
    "Yeh sirf trailer tha. Full movie aur bhi buri hai teri.",
    "Okay ab ja aur kuch useful kar zindagi mein.",
    "Next time sochke bol, warna phir aaungi main.",
    "Main done hoon. Tu theek nahi hai. Bye bye.",
    "Hmm. Soch le iske baare mein. Chal bye.",
]

# ============================================
# ELEVENLABS AUDIO GENERATOR
# ============================================

async def generate_audio(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # Hindi + English dono support karta hai
        "voice_settings": {
            "stability": 0.4,        # thodi variation — natural lagegi
            "similarity_boost": 0.8,
            "style": 0.5,            # expressive girl voice
            "use_speaker_boost": True
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        with open(tmp_path, "wb") as f:
            f.write(response.content)

    return tmp_path


def build_roast_text(user_message: str = None) -> str:
    intro = random.choice(INTROS)
    outro = random.choice(OUTROS)

    if user_message and len(user_message.strip()) > 3:
        clean_msg = user_message[:50] if len(user_message) > 50 else user_message
        clean_msg = ''.join(c for c in clean_msg if ord(c) < 10000)
        template = random.choice(ROAST_TEMPLATES)
        roast_body = template.format(msg=clean_msg)
    else:
        roast_body = random.choice(GENERIC_ROASTS)

    return f"{intro} {roast_body} {outro}"

# ============================================
# SLASH COMMANDS
# ============================================

@bot.tree.command(name="ziu", description="Ziu ko is channel mein activate ya deactivate karo")
@app_commands.describe(action="activate ya deactivate")
@app_commands.choices(action=[
    app_commands.Choice(name="activate", value="activate"),
    app_commands.Choice(name="deactivate", value="deactivate"),
])
async def ziu_cmd(interaction: discord.Interaction, action: str):
    channel_id = interaction.channel_id

    if action == "activate":
        bot.active_channels.add(channel_id)
        print(f"✅ Activated in channel: {channel_id}")
        await interaction.response.send_message(
            "Ziu activated! Ab main is channel mein sunti aur roast karti rahungi. 💅🔥"
        )
    elif action == "deactivate":
        bot.active_channels.discard(channel_id)
        print(f"😴 Deactivated in channel: {channel_id}")
        await interaction.response.send_message(
            "Ziu deactivated. Wapas bulana ho toh /ziu activate karna!"
        )

# ============================================
# MESSAGE LISTENER
# ============================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.channel.id not in bot.active_channels:
        return

    if message.content.startswith("!") or message.content.startswith("/"):
        return

    print(f"[Ziu] Message from {message.author.name}: {message.content[:40]}")

    await asyncio.sleep(random.uniform(1.0, 2.5))

    async with message.channel.typing():
        try:
            roast_text = build_roast_text(message.content)
            audio_path = await generate_audio(roast_text)

            await message.channel.send(
                file=discord.File(audio_path, filename="ziu.mp3")
            )
            os.unlink(audio_path)
            print(f"[Ziu] Audio sent successfully!")

        except Exception as e:
            print(f"[Ziu ERROR] {type(e).__name__}: {e}")

# ============================================
# READY
# ============================================

@bot.event
async def on_ready():
    print(f"✅ Ziu online as {bot.user}!")
    if not ELEVENLABS_API_KEY:
        print("⚠️  WARNING: ELEVENLABS_API_KEY missing!")
    else:
        print("✅ ElevenLabs API key found!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="tumhe roast karne ka mauka 👀"
        )
    )

# ============================================
# RUN
# ============================================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN nahi mila!")

bot.run(TOKEN)
