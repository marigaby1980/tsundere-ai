import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from google import genai

# --- Setup ---
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MEMORY_FILE = "user_memory.json"

# Load/Save helper
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f)

user_memory = load_memory()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is online and ready. Slash commands synced.')

# --- Slash Command: /likevalue ---
@bot.tree.command(name="likevalue", description="Check how much I (secretly) like someone.")
@app_commands.describe(member="The user you want to check (optional)")
async def likevalue(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    score = user_memory.get(str(target.id), 0)
    
    if score > 5:
        msg = f"Hmph. {target.display_name} is... okay, I guess. Don't tell them I said that!"
    elif score < -5:
        msg = f"Why would you ask about {target.display_name}? They're a total pain."
    else:
        msg = f"{target.display_name}? Just another baka to me."
    await interaction.response.send_message(msg, ephemeral=True)

# --- Message Handling ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    uid = str(message.author.id)
    if uid not in user_memory:
        user_memory[uid] = 0

    if bot.user.mentioned_in(message):
        # 1. Analyze Sentiment
        try:
            sentiment_prompt = f"Analyze: '{message.content}'. Output only a number between -1 (rude) and 1 (kind)."
            sentiment_resp = client.models.generate_content(model="gemini-1.5-flash-8b", contents=sentiment_prompt)
            sentiment_val = float(sentiment_resp.text.strip())
            
            # 2. Update Score (Capped between -10 and 10)
            user_memory[uid] = max(-10, min(10, user_memory[uid] + int(sentiment_val * 3)))
            save_memory(user_memory)
            
            # 3. Generate Response
            score = user_memory[uid]
            mood = "flustered and tsundere" if score > 5 else "cold and annoyed" if score < -5 else "classic Tsundere"
            
            async with message.channel.typing():
                response = client.models.generate_content(
                    model="gemini-1.5-flash-8b", 
                    contents=message.content,
                    config={"system_instruction": f"Persona: {mood}. Never state the score."}
                )
                await message.channel.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Ugh, I'm having a technical issue. Don't look at me like that!")

    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
