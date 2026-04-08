import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import random
import tempfile
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

# ============================================
# 🔥 ZIU — ROAST GIRL BOT
# ============================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class ZiuBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # Active channels — sirf inhi mein baat karegi Ziu
        self.active_channels = set()

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced!")

bot = ZiuBot()

# ============================================
# ROAST LINES
# ============================================

ROAST_TEMPLATES = [
    "Haan haan, tune kaha '{msg}' — wah kya intelligence! Mujhe laga tha tu kuch aqalmand bolega, par nahi. Typical! 😂",
    "'{msg}' — yeh sun ke mera IQ 10 point gir gaya. Tu khush hai apne aap se? 💅",
    "Oye tune kaha '{msg}' — aur main soch rahi thi tu boring nahi hoga. Galat thi main! 🙄",
    "'{msg}'?? Seriously?? Bhai teri soch itni choti hai ki ant bhi na ghuse usme! 😭",
    "Tune kaha '{msg}' — aur mujhe laga koi C-grade movie ka dialogue bol raha hai! 🎬",
    "Arre '{msg}' — yeh sun ke meri neend aa gayi. Tu sleeping pill se bhi zyada effective hai! 😴",
    "'{msg}' bol ke tune kya socha? Ki main impress ho jaungi? Cute try though! 💅",
    "Oh ho '{msg}' bola! Waah waah, genius ho tum bilkul. NAHI! 😂🔥",
]

GENERIC_ROASTS = [
    "Teri personality kisi pirated site se download ki lagti hai — full of bugs, zero quality! 💻",
    "Tu itna useless hai ki WiFi bhi tujhse better connection deta hai! 📶",
    "Tera confidence aur teri aukat mein Mariana Trench jitna farak hai! 🌊",
    "Teri life story ka title hoga — L pe L: A Masterpiece of Failure! 📖",
    "Tu itna slow hai ki kachhua bhi tujhe overtake kar ke chala gaya zindagi mein! 🐢",
    "Honey, your vibe is giving error 404 — personality not found! 💅",
    "You are the human equivalent of a loading screen that never finishes! ⌛",
    "Tera dimag Chrome browser ki tarah hai — 47 tabs open, sab crash! 😭",
    "Main tujhe roast karna chahti thi but phir realize kiya — tu khud ek joke hai! 😂",
    "Bhai teri smartness ka level airplane mode pe hai — completely off! ✈️",
]

INTROS = [
    "Ohhh tune kuch bola? Chal sun le mujhse —",
    "Aacha aacha, toh yeh baat hai? Theek hai, sun —",
    "Haye haye, kya bola tune! Chal main samjhati hoon —",
    "Oh sweetie, really? Okay okay, sun zara —",
    "Aaaa gaya firse bolne! Chal roast time —",
]

OUTROS = [
    "Samjha? Nahi samjha? Expected! Bye!",
    "Yeh sirf trailer tha, full movie aur bhi buri hai teri!",
    "Okay ab ja aur kuch useful kar zindagi mein!",
    "Next time sochke bol, warna phir aaugi main!",
    "Okay I am done. Tu theek nahi hai. Bye!",
]

# ============================================
# AUDIO GENERATOR
# ============================================

def generate_audio(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save(tmp_path)
    return tmp_path


def build_roast(user_message: str = None) -> str:
    intro = random.choice(INTROS)
    outro = random.choice(OUTROS)

    if user_message and len(user_message.strip()) > 3:
        template = random.choice(ROAST_TEMPLATES)
        short_msg = user_message[:60] + "..." if len(user_message) > 60 else user_message
        roast_body = template.format(msg=short_msg)
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
        embed = discord.Embed(
            title="✅ Ziu Activated! 🔥",
            description=(
                "Main ab is channel mein active hoon!\n"
                "Jo bhi kuch bolega — main uski baat sun ke audio roast karungi! 💅\n\n"
                "`/ziu deactivate` se band kar sakte ho."
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    elif action == "deactivate":
        bot.active_channels.discard(channel_id)
        embed = discord.Embed(
            title="😴 Ziu Deactivated",
            description=(
                "Theek hai, main is channel mein chup ho jaati hoon.\n"
                "`/ziu activate` se wapas bula sakte ho! 👋"
            ),
            color=discord.Color.greyple()
        )
        await interaction.response.send_message(embed=embed)

# ============================================
# MESSAGE LISTENER — Context-aware auto roast
# ============================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    # Sirf active channels mein react karegi
    if message.channel.id not in bot.active_channels:
        return

    # Commands ignore
    if message.content.startswith("!") or message.content.startswith("/"):
        return

    # Natural delay
    await asyncio.sleep(random.uniform(1.0, 2.5))

    async with message.channel.typing():
        try:
            roast_text = build_roast(message.content)
            audio_path = generate_audio(roast_text)

            embed = discord.Embed(
                description=f"*{roast_text}*",
                color=discord.Color.red()
            )
            embed.set_author(
                name="Ziu 💅🔥",
                icon_url=bot.user.display_avatar.url
            )
            embed.set_footer(text=f"Roasting: {message.author.display_name}")

            await message.channel.send(embed=embed)
            await message.channel.send(
                file=discord.File(audio_path, filename="ziu_roast.mp3")
            )
            os.unlink(audio_path)

        except Exception as e:
            print(f"[Ziu Error] {e}")

# ============================================
# BOT READY
# ============================================

@bot.event
async def on_ready():
    print(f"✅ Ziu online as {bot.user}!")
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
    raise ValueError("❌ DISCORD_TOKEN .env mein nahi mila!")

bot.run(TOKEN)
