import discord
from discord.ext import commands
from discord import app_commands
import asyncio, os, random, tempfile
from gtts import gTTS
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class ZiuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.active_channels = set()
    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Commands synced!")

bot = ZiuBot()

# ============================================
# ROAST LINES
# ============================================

ROASTS = [
    "Haan haan, tune kaha {msg}. Wah kya baat! Mujhe laga kuch akal wali baat bolega par nahi. Bilkul typical.",
    "Tune kaha {msg}. Yeh sun ke mera IQ dus point gir gaya. Tu khush hai apne aap se?",
    "Oye tune kaha {msg}. Main soch rahi thi tu boring nahi hoga. Galat thi main, bilkul galat.",
    "Tune kaha {msg}. Seriously? Teri soch itni choti hai ki ant bhi na ghuse usme.",
    "Arre tune kaha {msg}. Yeh sun ke mujhe neend aa gayi. Tu sleeping pill se bhi zyada effective hai.",
    "Tune kaha {msg}. Aur socha main impress ho jaungi? Cute try tha par nahi hogi main.",
    "Oh ho {msg} bola! Waah waah genius ho tum. Nahi, bilkul bhi nahi.",
    "Tune kaha {msg}. Lagta hai koi C grade movie ka dialogue yaad tha tujhe.",
]

GENERIC = [
    "Teri personality pirated site se download ki lagti hai. Full of bugs, zero quality.",
    "Tu itna useless hai ki WiFi bhi tujhse better connection deta hai.",
    "Tera confidence aur teri aukat mein Mariana Trench jitna farak hai samjha?",
    "Tu itna slow hai ki kachhua bhi tujhe overtake kar ke chala gaya zindagi mein.",
    "Tera dimag saintalis tabs wale Chrome browser ki tarah hai, sab crash.",
    "Main tujhe roast karna chahti thi par realize kiya tu khud ek joke hai.",
    "Bhai teri smartness ka level airplane mode pe hai, completely off.",
    "Tujhe dekh ke lagta hai evolution ne teri file skip kar di thi.",
]

def make_roast(msg: str) -> str:
    if msg and len(msg.strip()) > 3:
        clean = ''.join(c for c in msg[:50] if ord(c) < 10000).strip()
        return random.choice(ROASTS).format(msg=clean)
    return random.choice(GENERIC)

# ============================================
# AUDIO — gTTS + pydub pitch tuning (girl voice)
# ============================================

def generate_audio_sync(text: str) -> str:
    # Step 1: gTTS se raw audio
    raw = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    raw.close()
    gTTS(text=text, lang="hi", slow=False).save(raw.name)

    # Step 2: pydub se pitch + speed adjust
    audio = AudioSegment.from_mp3(raw.name)

    # Speed 1.1x — girl jaisi fast natural speech
    audio = audio.speedup(playback_speed=1.1)

    # Pitch +4 semitones upar — female voice range
    octaves = 4 / 12.0
    new_rate = int(audio.frame_rate * (2.0 ** octaves))
    audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
    audio = audio.set_frame_rate(44100)

    # Step 3: output save
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    out.close()
    audio.export(out.name, format="mp3", bitrate="128k")
    os.unlink(raw.name)
    return out.name

async def generate_audio(text: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_audio_sync, text)

# ============================================
# SLASH COMMANDS
# ============================================

@bot.tree.command(name="ziu", description="Ziu activate/deactivate")
@app_commands.choices(action=[
    app_commands.Choice(name="activate",   value="activate"),
    app_commands.Choice(name="deactivate", value="deactivate"),
])
async def ziu_cmd(interaction: discord.Interaction, action: str):
    if action == "activate":
        bot.active_channels.add(interaction.channel_id)
        await interaction.response.send_message("Ziu activated! Ab roast hoga har message ka. 💅🔥")
    else:
        bot.active_channels.discard(interaction.channel_id)
        await interaction.response.send_message("Ziu deactivated. Bye! 👋")

# ============================================
# MESSAGE LISTENER
# ============================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in bot.active_channels: return
    if message.content.startswith(("/", "!")): return

    await asyncio.sleep(random.uniform(1.0, 2.0))
    async with message.channel.typing():
        try:
            text = make_roast(message.content)
            path = await generate_audio(text)
            await message.channel.send(file=discord.File(path, filename="ziu.mp3"))
            os.unlink(path)
            print(f"[Ziu] ✅ Roasted: {message.author.name}")
        except Exception as e:
            print(f"[Ziu ERROR] {e}")

@bot.event
async def on_ready():
    print(f"✅ Ziu online as {bot.user}!")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="roast karne ka mauka 👀"))

bot.run(os.getenv("DISCORD_TOKEN")) 
