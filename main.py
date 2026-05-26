import os
import discord
from discord.ext import commands
from google import genai

# 1. Setup Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # We print this so we can see it in logs, but don't crash the container immediately
    print("CRITICAL: GEMINI_API_KEY is not set.")
    client = None
else:
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

@bot.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == bot.user:
        return

    # Process commands (like !help) first
    await bot.process_commands(message)

    # If the bot is mentioned, let the AI respond
    if bot.user.mentioned_in(message):
        if not client:
            await message.channel.send("My internal systems are broken (API Key missing). Hmph.")
            return

        async with message.channel.typing():
            try:
                # Use the new SDK method
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=message.content,
                    config={"system_instruction": system_instruction}
                )
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send("Ugh, I'm having a technical issue. Don't look at me like that!")
                print(f"Error: {e}")

# Run the bot
token = os.getenv('DISCORD_BOT_TOKEN')
if token:
    bot.run(token)
else:
    print("CRITICAL: DISCORD_BOT_TOKEN is missing!")
