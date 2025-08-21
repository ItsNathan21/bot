import discord
import os
from dotenv import load_dotenv
from clientHandlers import BotMarketClient


intents = discord.Intents.default()
intents.message_content = True


load_dotenv()
client = BotMarketClient(intents = intents)
client.run(os.getenv("TOKEN"))
