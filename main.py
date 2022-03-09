import discord
import os
from dotenv import load_dotenv
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands
import jobsearch.indeed as ind
import jobsearch.linkedin as lkn

from db import get_user_balance, get_user_rank, insert_user, get_role, apply_to_job, get_applications, attend_event
from xp import assign_xp
from utils import *
from roles.roles import IGNORE_ROLES, ROLE_TO_SALARY

intents = discord.Intents().all()

bot = commands.Bot(intents=intents)


async def college_search(ctx:discord.AutocompleteContext):
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	return [college for college in college_roles]


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL')
invite_map = dict()


@bot.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	print(f'{bot.user.name} has connected to Discord!')
	invites = await bot.guilds[0].invites()
	for invite in invites:
		invite_map[invite.code] = invite
	
	


@bot.event
async def on_invite_create(invite):
	"""
	This event is called when a new invite is created.
	"""
	invite_map[invite.code] = invite


@bot.event
async def on_invite_delete(invite):
	"""
	This event is called when an invite is deleted.
	"""
	del invite_map[invite.code]


@bot.event
async def on_message(message):
	"""
	Args:
		message (This event is called when a message is sent): _description_
	"""
	if message.author == bot.user:
		return
	
	await assign_xp(bot, "MESSAGE", message.author.id)

@bot.event
async def on_member_join(member):
	"""
	This event is called when a member joins the server.
	"""
	insert_user(member.id)
	invites_after_join = await member.guild.invites()

	for invite in invite_map.values():
		if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
			inviter = invite.inviter
			
			await assign_xp(bot, "REFERRAL", inviter.id)
			role = discord.utils.get(member.guild.roles, name="Lower Year Student")
			await member.add_roles(role)

@bot.slash_command(name="ping", description="Pong!", guild_ids=[939394818428243999])
async def ping(ctx):
	await ctx.respond('Pong!')


@bot.slash_command(name="balance", description="Shows the current balance for a user's account", guild_ids=[939394818428243999])
async def balance(ctx):
	bal = get_user_balance(ctx.interaction.user.id)
	embed = discord.Embed(
		title=f"{ctx.interaction.user.name}'s Account",
		colour=discord.Colour.from_rgb(123, 221, 98),
	)
	embed.add_field(name="🏦 Balance 🏦", value=bal[0])
	await ctx.respond(embed=embed)


@bot.slash_command(name="rank", description="Shows the ranking for a given user", guild_ids=[939394818428243999])
async def rank(ctx):
	rank = get_user_rank(ctx.interaction.user.id)
	embed = discord.Embed(
		title=f"{ctx.interaction.user.name}'s Rank",
	)


@bot.slash_command(name="apply", description="Apply to a certain job given a job id", guild_ids=[939394818428243999])
async def apply(ctx,
	job_id: Option(int, "Enter the job id to apply")
):
	await apply_to_job(ctx.interaction.user.id, job_id)
	await assign_xp(bot, "APPLY", ctx.interaction.user.id)
	await ctx.respond(f"Applied to job {job_id} for {ctx.interaction.user.name}")


@bot.slash_command(name="salary", description="Shows a user's current salary.", guild_ids=[939394818428243999])
async def salary(ctx):
	role = get_role(ctx.interaction.user.id)
	embed = discord.Embed(
		title=f"💸 Your current salary is ${ROLE_TO_SALARY[role]} 💸"
	)
	await ctx.respond(embed=embed)


@bot.slash_command(name="applications", description="Show all my current applications", guild_ids=[939394818428243999])
async def applications(ctx):
	apps = get_applications(ctx.interaction.user.id)
	for app in apps:
		embed = discord.Embed(
			title=f"{app[0]}",
		)
		embed.add_field(name="📝 Date 📝", value=app[1])
		ctx.respond(embed=embed)


colleges = SlashCommandGroup(name="colleges", description="Commands for displaying and joining colleges")

@bot.slash_command(name="attendevent" ,description="Attend an event", guild_ids=[939394818428243999])
async def attendevent(ctx, event_id: Option(int, "Enter the event id")):
	await assign_xp(bot, "ATTEND_EVENT", ctx.interaction.user.id)
	await attend_event(ctx.interaction.user.id, event_id)
	await ctx.respond(f"Attended event {event_id} for {ctx.interaction.user.name}")


@bot.slash_command(name="indeed", description="Search for a job on Indeed", guild_ids=[939394818428243999])
async def indeed(ctx,
	title: Option(str, "Enter the job title")):
	embeds = ind.find_jobs(title)
	if not embeds:
		await ctx.respond("No jobs found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)

@bot.slash_command(name="linkedin", description="Search for a job on LinkedIn", guild_ids=[939394818428243999])
async def linkedin(ctx,
	title: Option(str, "Enter the job title")):
	
	embeds = lkn.find_jobs(title)
	if not embeds:
		await ctx.respond("No jobs found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)

@colleges.command(name="join", description="Join a college", guild_ids=[939394818428243999])
async def join(ctx,
	college: Option(str, "Enter the college name", autocomplete=college_search)
):	
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	role = discord.utils.get(ctx.interaction.guild.roles, name=college)
	if role.name in college_roles:
		await ctx.interaction.user.add_roles(role)
		await ctx.respond(f"You have now joined the {college} college!")
	else:
		await ctx.respond("That college does not exist.")
	

@colleges.command(name="list", description="Shows the available colleges", guild_ids=[939394818428243999])
async def display_colleges(ctx):
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	embed = discord.Embed(
		title="Available Colleges",
		colour=discord.Colour.from_rgb(23, 121, 198),
	)
	for role in college_roles:
		embed.add_field(name=role, value=f"`/colleges join {role}`", inline=False)

	await ctx.respond(embed=embed)

bot.add_application_command(colleges)


bot.run(TOKEN)


