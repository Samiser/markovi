import os
from discord.ext import commands
import asyncio
import json
import random
import re
from markovboi import MarkovBoi

m = MarkovBoi()

with open('secrets.json', 'r') as f:
    TOKEN = json.loads(f.read())['TOKEN']

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} is in the house!!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(message.content)

    m.parse_message(str(message.author.id), message.content)

    await bot.process_commands(message)

    if random.randint(1,100) < 5:
        await message.channel.send(m.gen_message('000000000000000000'))

@bot.command()
async def scan(ctx, user=None):
    count = 0

    async for msg in ctx.message.channel.history(limit=10000):
        if not msg.author.bot and not msg.content.startswith(('-','s?', '!')):
            count += 1
            m.parse_message(str(msg.author.id), msg.content)

    await ctx.channel.send(f'last {count} messages in this channel scanned and indexed')

@bot.command()
async def copy(ctx, user=None, seed=None):
    if user and user.lower() == 'all':
        user = '000000000000000000'
    elif user:
        try:
            user = re.findall(r'\d{18}', user)[0]
        except:
            await ctx.channel.send('**error:** first arg must be a valid user or "all"')
    else:
        user = str(ctx.author.id)

    if len(user) != len(str(ctx.author.id)):
        return

    if seed:
        await ctx.channel.send(m.gen_message(user, seed))
    else:
        await ctx.channel.send(m.gen_message(user))

bot.run(TOKEN)
