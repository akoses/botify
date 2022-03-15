import discord
from discord.commands import Option
from discord.ext import commands
intents = discord.Intents().all()
bot = commands.Bot(intents=intents)

import jobsearch.linkedin as lkn
import jobsearch.indeed as ind
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('JOB_TOKEN')

@bot.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	print(f'{bot.user.name} has connected to Discord!')

@bot.slash_command(name="linkedin", description="Search for a job on LinkedIn")
async def linkedin(ctx,
	title: Option(str, "Enter the job title")):
	print(f'{ctx.author.name} has searched for {title}')
	await ctx.defer()
	embeds = await lkn.find_jobs(title)
	if not embeds:
		await ctx.respond("No jobs found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)
		await ctx.delete()

@bot.slash_command(name="indeed", description="Search for a job on Indeed")
async def indeed(ctx,
	title: Option(str, "Enter the job title")):
	await ctx.defer()
	embeds = await ind.find_jobs(title)
	if not embeds:
		await ctx.respond("No jobs found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)
		await ctx.delete()



bot.run(TOKEN)