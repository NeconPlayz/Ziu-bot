import discord
from discord.ext import commands
from discord import app_commands
import asyncio, os, random, tempfile, httpx
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

API_KEY  = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "TC0Zp7WVFzhA8zpTlRqV"

ROASTS = [
    "Haan haan, tune kaha {msg}. Wah kya baat! Mujhe laga kuch akal wali baat bolega par nahi. Bilkul typical.",
    "Tune kaha {msg}. Yeh sun ke mera IQ dus point gir gaya. Tu khush hai apne aap se?",
    "Oye tune kaha {msg}. Main soch rahi thi tu boring nahi hoga. Galat thi main, bilkul galat.",
    "Tune kaha {msg}. Seriously? Teri soch itni choti hai ki ant bhi na ghuse usme.",
    "Arre tune kaha {msg}. Yeh sun ke mujhe neend aa gayi. Tu sleeping pill se bhi effective hai.",
    "Tune kaha {msg}. Aur socha main impress ho jaungi? Cute try tha, par nahi hogi main.",
]

GENERIC = [
    "Teri personality pirated site se download ki lagti hai. Full of bugs, zero quality.",
    "Tu itna useless hai ki WiFi bhi tujhse better connection deta hai.",
    "Tera confidence aur teri aukat mein Mariana Trench jitna farak hai samjha?",
    "Tu itna slow hai ki kachhua bhi tujhe overtake kar ke chala gaya.",
    "Tera dimag saintalis tabs wale Chrome browser ki tarah hai, sab crash.",
    "Main tujhe roast karna chahti thi par realize kiya tu khud ek joke hai.",
]

def make_roast(msg: str) -> str:
    if msg and len(msg.strip()) > 3:
        clean = msg[:50].strip()
        return random.choice(ROASTS).format(msg=clean)
    return random.choice(GENERIC)

async def speak(text: str) -> str:
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    out.close()
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.35, "similarity_boost": 0.85, "style": 0.6}
            }
        )
        r.raise_for_status()
        open(out.name, "wb").write(r.content)
    return out.name

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

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot: return
    await bot.process_commands(message)
    if message.channel.id not in bot.active_channels: return
    if message.content.startswith(("/", "!")): return

    await asyncio.sleep(random.uniform(1, 2))
    async with message.channel.typing():
        try:
            text = make_roast(message.content)
            path = await speak(text)
            await message.channel.send(file=discord.File(path, filename="ziu.mp3"))
            os.unlink(path)
        except Exception as e:
            print(f"[ERROR] {e}")

@bot.event
async def on_ready():
    print(f"✅ Ziu online! API={'OK' if API_KEY else 'MISSING'}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="roast karne ka mauka 👀"))

bot.run(os.getenv("DISCORD_TOKEN"))
