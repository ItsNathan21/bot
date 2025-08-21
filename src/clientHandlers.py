import discord
import json
from parser import MessageParser

class BotMarketClient(discord.Client):

    async def on_ready(self):
        print(f"{self.user} connected and running")

    async def on_message(self, message):
        if message.author == self.user: return
        parsedMsg : MessageParser = MessageParser(message)
        parsedMsg.parse()
        print(parsedMsg.buyingData)
        print(parsedMsg.sellingData)

    async def on_message_delete(self, message):
        await message.channel.send(f"@{message.author.name} I see you deleted something")
