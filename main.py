import discord
import yaml
from discord.ext import commands
from loguru import logger

from creds import *

bot = commands.Bot(command_prefix='cc!', case_insensitive=True)
bot.setup = True
bot.custom_commands = {}


@bot.event
async def on_ready():
    if bot.setup:
        logger.info('Bot on')
        bot.setup = False
        with open('commands.yaml', 'r') as f:
            bot.custom_commands = yaml.safe_load(f)


@bot.event
async def on_message(message):
    guild = bot.custom_commands.get(message.guild.id)
    prefix = await bot.get_prefix(message)
    if guild:
        command_name = message.content[3:].lower()
        command = guild.get(command_name)
        if (command is not None) and prefix + command_name == message.content:
            for k, v in command.items():
                if k == 'message':
                    kwargs = {}
                    if e := v.get('embed'):
                        embed = discord.Embed()
                        kwargs['embed'] = embed
                        if title := e.get('title'):
                            embed.title = title
                        if color := e.get('color'):
                            try:
                                color = int(color, 16)
                                embed.colour = color
                            except ValueError:
                                return await message.channel.send('Error in embed color: Color seems to be invalid.')
                        if fields := e.get('fields'):
                            field_num = 1
                            for field in fields:
                                try:
                                    embed.add_field(name=field['name'], value=field['value'])
                                    field_num += 1
                                except KeyError:
                                    return await message.channel.send(f"Error in embed field {field_num}: "
                                                                      "Both name and value have to be set.")
                    if text := v.get('text'):
                        kwargs['content'] = text
                    await message.channel.send(**kwargs)


bot.run(TOKEN)
