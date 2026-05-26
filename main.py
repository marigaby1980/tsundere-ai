import os
import json
import discord
from discord.ext import commands
from google import genai

# Setup
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MEMORY_FILE = "user_memory.json"

# Load memory from disk
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        user_memory = json.load(f)
else:
    user_memory = {}

def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        json.dump(user_memory, f)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    uid = str(message.author.id)
    if uid not in user_memory:
        user_memory[uid] = 0

    if bot.user.mentioned_in(message):
        # Mood Logic: Score determines the 'hidden' personality
        score = user_memory[uid]
        
        # Influence the score based on interaction
        user_memory[uid] += 1
        save_memory()

        # Dynamic System Instruction
        # We don't tell the AI to "be hostile," we tell it to "adopt a persona"
        if score > 10:
            mood = "You are acting flustered, denying that you like them, and stuttering. You are clearly becoming attached."
        elif score < -5:
            mood = "You are cold, brief, and very annoyed. You want them to leave you alone."
        else:
            mood = "You are classic Tsundere. Annoyed, but willing to answer."

        try:
            async with message.channel.typing():
                response = client.models.generate_content(
                    model="gemini-1.5-flash-8b",
                    contents=message.content,
                    config={"system_instruction": f"Persona: {mood}. Stay in character. Never explicitly state your affection score."}
                )
                await message.channel.send(response.text)
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
