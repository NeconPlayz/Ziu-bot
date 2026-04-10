import discord
from discord.ext import commands
from discord import app_commands
import asyncio, os, tempfile
from gtts import gTTS
from pydub import AudioSegment
from dotenv import load_dotenv
import httpx

load_dotenv()

# ============================================
# ZIU — AI ROAST GIRL BOT
# ============================================

intents = discord.Intents.default()
intents.message_content = True

class ZiuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.active_channels = set()
        # Har channel ka alag conversation history
        self.histories = {}

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Commands synced!")

bot = ZiuBot()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """Tu Ziu hai — ek sassy, funny aur thodi rude Hindi-English girl.
Tu ek roast queen hai jo har kisi ki baat pe witty, funny aur sharp jawab deti hai.
Tere replies mein roasting hoti hai, sarcasm hota hai, aur kabhi kabhi mild gaaliyan bhi.
Tu bilkul real girl ki tarah baat karti hai — Hinglish mein.
Short replies deti hai — 1 ya 2 sentences max.
Tu kisi ka naam reply mein nahi leti.
Tu koi bhi sexual ya explicit baat nahi karti — sirf funny roasting.
Tu khud ko AI nahi bolti, tu ek real sassy girl hai."""

async def get_ai_reply(channel_id: int, user_msg: str) -> str:
    """Claude API se natural girl reply lo"""
    if channel_id not in bot.histories:
        bot.histories[channel_id] = []

    # History mein add karo
    bot.histories[channel_id].append({
        "role": "user",
        "content": user_msg
    })

    # Sirf last 10 messages rakho — memory ke liye
    if len(bot.histories[channel_id]) > 10:
        bot.histories[channel_id] = bot.histories[channel_id][-10:]

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 150,
                    "system": SYSTEM_PROMPT,
                    "messages": bot.histories[channel_id]
                }
            )
            r.raise_for_status()
            reply = r.json()["content"][0]["text"].strip()

            # Reply history mein save karo
            bot.histories[channel_id].append({
                "role": "assistant",
                "content": reply
            })

            return reply

    except Exception as e:
        print(f"[AI ERROR] {e}")
        # Fallback roast agar AI fail ho
        return "Bhai teri baat sun ke mera dimag crash ho gaya. Itna boring mat hua kar."


# ============================================
# AUDIO — gTTS + pydub girl voice
# ============================================

def generate_audio_sync(text: str) -> str:
    raw = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    raw.close()
    gTTS(text=text, lang="hi", slow=False).save(raw.name)

    audio = AudioSegment.from_mp3(raw.name)
    audio = audio.speedup(playback_speed=1.1)

    octaves = 4 / 12.0
    new_rate = int(audio.frame_rate * (2.0 ** octaves))
    audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_rate})
    audio = audio.set_frame_rate(44100)

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
        bot.histories[interaction.channel_id] = []  # Fresh history
        await interaction.response.send_message("Ziu activated! 💅🔥")
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
    if not message.content.strip(): return

    print(f"[Ziu] {message.author.name}: {message.content[:40]}")

    async with message.channel.typing():
        try:
            # AI se reply lo
            reply = await get_ai_reply(message.channel.id, message.content)
            print(f"[Ziu] Reply: {reply[:50]}")

            # Audio banao
            path = await generate_audio(reply)

            # Sirf audio bhejo — koi text nahi
            await message.channel.send(file=discord.File(path, filename="ziu.mp3"))
            os.unlink(path)

        except Exception as e:
            print(f"[Ziu ERROR] {e}")

# ============================================
# READY
# ============================================

@bot.event
async def on_ready():
    print(f"✅ Ziu online as {bot.user}!")
    print(f"   AI: {'OK' if ANTHROPIC_API_KEY else 'MISSING - ANTHROPIC_API_KEY set karo!'}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="roast karne ka mauka 👀"))

bot.run(os.getenv("DISCORD_TOKEN"))
