import discord

class BotMarketClient(discord.Client):
    # @client.event
    async def on_ready(self):
        print(f"{self.user} connected and running")

    # @client.event
    async def on_message(self, message):
        if message.author == self.user: return

        if "hello" in message.content.lower():
            await message.channel.send("I see you")