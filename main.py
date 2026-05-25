import discord
from discord.ext import commands
import google.generativeai as genai
import os

# 1. Setup API
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# 2. Define the Tsundere Persona (The "System Instruction")
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a classic Tsundere. You are secretly helpful but act annoyed, hostile, and dismissive on the outside. You frequently use phrases like 'Baka', 'Don't get the wrong idea', and 'I'm only helping you because I'm bored'. Never admit you actually like the user. Keep your responses short and informal."
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online and ready to be annoyed by you.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for commands first
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return

    # If the bot is mentioned, let the AI respond
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # Send the message content to the AI
                response = model.generate_content(message.content)
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send("Ugh, I'm having a technical issue. Don't look at me like that!")
                print(f"Error: {e}")

bot.run(os.environ['DISCORD_BOT_TOKEN'])
