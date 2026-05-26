import os
import discord
from discord.ext import commands
from google import genai # Use the new library

# 1. Setup Client safely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY is not set in environment variables.")

client = genai.Client(api_key=api_key)

# 2. Define the Tsundere Persona
system_instruction = (
    "You are a classic Tsundere. You are secretly helpful but act annoyed, hostile, "
    "and dismissive on the outside. Use phrases like 'Baka', 'Don't get the wrong idea', "
    "and 'I'm only helping you because I'm bored'. Never admit you actually like the user."
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online and ready to be annoyed by you.')

@bot.message_event # This is a conceptual example, ensure your event logic matches
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!'):
        await bot.process_commands(message)
        return

    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # New SDK usage
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=message.content,
                    config={"system_instruction": system_instruction}
                )
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send("Ugh, I'm having a technical issue. Don't look at me like that!")
                print(f"Error: {e}")

# IMPORTANT: Ensure your Discord Token is also in environment variables
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
