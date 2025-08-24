import discord
import os
from dotenv import load_dotenv
from clientHandlers import BotMarketClient
from data import dataMain
import threading


intents = discord.Intents.default()
intents.message_content = True


load_dotenv()
client = BotMarketClient(intents = intents)

dataThread = threading.Thread(target= dataMain, daemon=True)

dataThread.start()
client.run(os.getenv("TOKEN"))
