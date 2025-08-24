import discord
import json
from parser import MessageParser
from data import BlockData

class BotMarketClient(discord.Client):

    async def on_ready(self):
        print(f"{self.user} connected and running")

    async def on_message(self, message):
        if message.author == self.user: return
        parsedMsg : MessageParser = MessageParser(message)
        parsedMsg.parse()
        BlockData.storeData(parsedMsg)
        
