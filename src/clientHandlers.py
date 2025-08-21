import discord
import json

class BotMarketClient(discord.Client):

    async def on_ready(self):
        print(f"{self.user} connected and running")

    async def on_message(self, message):
        if message.author == self.user: return
        
        await message.channel.send(f"{message.content}")

    async def on_message_delete(self, message):
        await message.channel.send(f"@{message.author.name} I see you deleted something")