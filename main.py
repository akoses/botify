import discord
import datetime
import os
from dotenv import load_dotenv
from discord.commands import Option, permissions
from discord.ext import commands, tasks
import jobsearch.indeed as ind
import jobsearch.linkedin as lkn
import books.libgen as libgen
from db import (
	get_user_balance, 
	get_user_rank, 
	insert_user, 
	get_role, 
	apply_to_job, 
	get_applications, 
	attend_event, 
	add_salaries, 
	set_user_balance, 
	get_entries, 
	set_entries
)

from xp import assign_xp
from utils import *
from roles.roles import IGNORE_ROLES, ROLE_TO_SALARY
from scheduler import *

intents = discord.Intents().all()

bot = commands.Bot(intents=intents)

index_to_num = {
	1: "one",
	2: "two",
	3: "three",
	4: "four",
	5: "five",
	6: "six",
	7: "seven",
	8: "eight",
	9: "nine",
	10:"ten",
}


index_to_unicode = {
	1:  '1️⃣',
	2: '2️⃣',
	3: '3️⃣',
	4: '4️⃣',
	5: '5️⃣',
	6: '6️⃣',
	7: '7️⃣',
	8: '8️⃣',
	9: '9️⃣',
	10:'🔟',
}

TRIVIA_PLAYERS = set()

async def college_search(ctx:discord.AutocompleteContext):
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	return [college for college in college_roles]

async def giveaway_search(ctx:discord.AutocompleteContext):
	if not CURRENT_GIVEAWAYS:
		return []
	return list(CURRENT_GIVEAWAYS.keys())

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL')
ADMIN_ROLE = int(os.getenv('ADMIN_ROLE'))
invite_map = dict()


@tasks.loop(time=[datetime.time(hour=4, minute=0, second=0)])
async def get_would_you_rather():
	question, answers = await get_poll()
	if question and answers:
		embed = discord.Embed(title=question, color=0x00ff00)
		for i, answer in enumerate(answers):
			embed.add_field(name = f':{index_to_num[i + 1]}:',  value=answer, inline=False)
		
		curr_mess = await bot.get_channel(939423795763105825).send(embed=embed)
		for i in range(len(answers)):
			emoji = index_to_unicode[i + 1]
			await curr_mess.add_reaction(emoji)

@tasks.loop(time=[datetime.time(hour=7, minute=0, second=0)])
async def pay_salaries():
	for role in ROLE_TO_SALARY:
		salary = ROLE_TO_SALARY[role]
		members = discord.utils.get(bot.guilds[0].roles, name=role).members

		members = map(lambda x: (salary, x.id), members)
		await add_salaries(members)
		print("All salaries paid for role: %s" % role)
		TRIVIA_PLAYERS.clear()



@bot.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	print(f'{bot.user.name} has connected to Discord!')
	invites = await bot.guilds[0].invites()
	for invite in invites:
		invite_map[invite.code] = invite
	

	if not get_would_you_rather.is_running():
		get_would_you_rather.start()

	if not pay_salaries.is_running():
		pay_salaries.start()

	

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
	await ctx.interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="rank", description="Shows the ranking for a given user", guild_ids=[939394818428243999])
async def rank(ctx):
	rank = get_user_rank(ctx.interaction.user.id)
	embed = discord.Embed(
		title=f"{ctx.interaction.user.name}'s Rank",
	)


@bot.slash_command(name="apply", description="Apply to a certain job given a job id. Use this as an application tracker.", guild_ids=[939394818428243999])
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


@bot.slash_command(name="attend-event" ,description="Attend an event given an event id. You will be given a reminder for the event to start.", guild_ids=[939394818428243999])
async def attendevent(ctx, event_id: Option(int, "Enter the event id")):
	await assign_xp(bot, "ATTEND_EVENT", ctx.interaction.user.id)
	await attend_event(ctx.interaction.user.id, event_id)
	await ctx.respond(f"Attended event {event_id} for {ctx.interaction.user.name}")



class TriviaButton(discord.ui.Button):
	def __init__(self, answer, correct, index):
		super().__init__(
            label=answer,
            style=discord.enums.ButtonStyle.secondary,
            custom_id=f'{index} {correct}',
        )


	async def callback(self, interaction):
		correct = self.custom_id.split(" ")[1]
		prize = determine_trivia_prize()
		if correct == self.label:
			await interaction.response.edit_message(content="That's correct! You've just won ${} coins! Come back tomorrow to play again.".format(prize), view=None)
			set_user_balance(prize, interaction.user.id)
		else:
			await interaction.response.edit_message(content="That's incorrect! The correct answer is {}. You could have won ${} coins. Come back tomorrow to play again.".format(correct, prize), view=None)
		await assign_xp(bot, "TRIVIA", interaction.user.id)
		TRIVIA_PLAYERS.add(interaction.user.id)


class AnswerView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=10)

async def create_college_fn(guild, college):
	"""
	Create a college role for the server.
	"""
	if not guild:
		guild = college['requested_by'].guild
	
	college_name = college['name'].rstrip().replace(' ', '-')
	role = await guild.create_role(name=college_name, mentionable=True)
	category = await guild.create_category(name=college_name, reason=college['reason'], position=6)
	await category.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True)
	await category.set_permissions(guild.default_role, read_messages=False, connect=False)
	await guild.create_text_channel(name=f"{college_name}-opportunities", category=category, reason=college['reason'])
	await guild.create_text_channel(name=f"{college_name}-events", category=category, reason=college['reason'])
	await guild.create_text_channel(name=f"{college_name}-general", category=category, reason=college['reason'])
	
	creator = college['requested_by']
	len_roles = len(guild.roles)
	await role.edit(position=(len_roles - 11))
	await creator.add_roles(role)
	await creator.send(f"Your new college {college_name} has been created!")
	

class CollegeRequestView(discord.ui.View):
	def __init__(self, college_data):
		super().__init__(timeout=None)
		self.college = college_data
	
	@discord.ui.button(label="Approve", style=discord.enums.ButtonStyle.success)
	async def approve(self, button, interaction):
		await create_college_fn(interaction.guild, self.college)
		await interaction.response.edit_message(content="College has been approved.", delete_after=10, view=None, embed=None)
	@discord.ui.button(label="Deny", style=discord.enums.ButtonStyle.danger)
	async def deny(self, button, interaction):
		await interaction.response.edit_message(content="College denied.", delete_after=10, view=None, embed=None)
		await interaction.user.send("Your college request has been denied.")


class TriviaView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=30)

	@discord.ui.button(label="Start",style=discord.ButtonStyle.primary)
	async def callback(self, button, interaction):
		question, correct, answers = await get_trivia_question()
		if not question or not answers or not correct:
			await interaction.response.edit_message(content="No more questions. Come back tomorrow to play again.", view=None)
			TRIVIA_PLAYERS.clear()
			return

		answers.append(correct)
		random.shuffle(answers)
		
		answerView = AnswerView()

		for i, answer in enumerate(answers):
			button = TriviaButton(answer, correct, i)
			answerView.add_item(button)
		
		await interaction.response.edit_message(content=question, view=answerView)
	

@bot.slash_command(name="trivia", description="Play a trivia game to win coins! You can only play once per day.", guild_ids=[939394818428243999])
async def trivia(ctx):
	if ctx.interaction.user.id in TRIVIA_PLAYERS:
		await ctx.interaction.response.send_message("You've already played today! Come back tomorrow to play again.", ephemeral=True)
		return
	trivia_message = f"""
	Hello **{ctx.interaction.user.name}**, welcome to the trivia game! \nYou will answer one question and if your answer is correct, you will be awarded between **1000** and **100,000** coins.\nYou will have **10** seconds to answer the question.\nPress the start button in order to begin!
	"""
	triviaView = TriviaView()
	triviaView.message = await ctx.interaction.response.send_message(trivia_message, ephemeral=True, view=triviaView)
	triviaView.ctx = ctx
	


@bot.slash_command(name="assign-xp", description="Assign XP to a user", guild_ids=[939394818428243999])
@permissions.has_role(ADMIN_ROLE)
async def assign_xp_to_user(ctx,
	xp: Option(int, "Enter the amount of XP to assign"),
	user: Option(discord.User, "Enter the user to assign XP to")):
	await assign_xp(bot, xp, user.id, xp)
	await ctx.respond(f"Assigned {xp} XP to {user.name}")


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


@bot.slash_command(name="books", description="Search for a book or textbook with LibGen", guild_ids=[939394818428243999])
async def books(ctx,
	title: Option(str, "Enter the book name or author")):
	embeds = await libgen.get_libgen_books(title)
	if not embeds:
		await ctx.respond("No books found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)


##################################
#College Commands 
##################################
colleges = bot.create_group(name="colleges",
description="Commands for displaying and joining colleges")

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

@colleges.command(name="create", description="Request to create a new college", guild_ids=[939394818428243999])
async def create_college(ctx):
	try:
		await ctx.respond("What is the name of the college you would like to create?")
		college_name = await bot.wait_for("message", timeout=30)
		await ctx.respond(f"What is the description of the college you would like to create?")
		college_description = await bot.wait_for("message", timeout=30)
		await ctx.respond(f"What is the reason for the college you would like to create?")
		college_reason = await bot.wait_for("message", timeout=30)
		await ctx.channel.purge(limit=6)
		await ctx.respond(f"Your college is now under review. We will inform you if we have approved your request.")
		guild_owner = ctx.guild.owner
		embed = discord.Embed(
			title=f"New College Request",
		)
		embed.add_field(name="Name", value=college_name.content, inline=False)
		embed.add_field(name="Description", value=college_description.content, inline=False)
		embed.add_field(name="Reason", value=college_reason.content, inline=False)
		embed.add_field(name="Requested By", value=ctx.interaction.user.mention, inline=False)
		college = {
			"name": college_name.content,
			"description": college_description.content,
			"reason": college_reason.content,
			"requested_by": ctx.interaction.user,
		}

		view = CollegeRequestView(college)
		await guild_owner.send(embed=embed, view=view)
	except Exception as e:
		await ctx.respond(f"You took too long.")


##################################
#Giveaway Commands 
##################################
giveaway = bot.create_group(name="giveaway",
description="Commands for running and entering giveaways")

@giveaway.command(name="start", description="Start a giveaway", guild_ids=[939394818428243999])
async def start_giveaway(ctx):

	def num_check (m):
		return m.author == ctx.interaction.user and m.content.isdigit()

	try:
		await ctx.delete()
		await ctx.respond(f"Hello {ctx.interaction.user.mention}, what is the name of your giveaway?")
		giveaway_name = await bot.wait_for('message', timeout=60)
		await ctx.respond(f"What is the prize for the giveaway?")
		giveaway_prize = await bot.wait_for('message', timeout=60, )
		await ctx.respond(f"How many winners do you want?")
		giveaway_winners = await bot.wait_for('message', timeout=60,check=num_check)
		await ctx.respond(f"How many hours do you want the giveaway to last?")
		giveaway_time = await bot.wait_for('message', timeout=60,  check=num_check)
		await ctx.respond(f"What is the description for the giveaway?")
		giveaway_description = await bot.wait_for('message', timeout=60)
		await ctx.channel.purge(limit=14)
		await ctx.respond(f"Your giveaway has been created and is scheduled to be drawn in {giveaway_time.content} hours.")
		await create_giveaway(ctx, giveaway_name.content, 
			giveaway_prize.content, 
			int(giveaway_winners.content), 
			int(giveaway_time.content), 
			giveaway_description.content)
	
	except asyncio.TimeoutError:
		await ctx.respond("You took too long to answer a question. Cancelling giveaway.")
		return
	


@giveaway.command(name="enter", description="Enter a giveaway",  guild_ids=[939394818428243999])
async def enter_giveaway(ctx, 
	name:Option(str, "Enter the name of the giveaway",
	autocomplete=giveaway_search),
	entries: Option(int, "Enter the number of entries. Defaults to 1", default=1)):
	entry_count = await get_entries(ctx.interaction.user.id)

	if entry_count < entries:
		await ctx.respond(f"Sorry, you do not have enough giveaway entries. You have {entry_count} entries.")
	else:
		try:
			giveaway_entry(ctx.interaction.user, name, entries)
			await ctx.respond(f"You have entered {entries} entries. You now have {entry_count - entries} entries remaining.")
			await set_entries(ctx.interaction.user.id, entry_count - entries)
		except Exception as e:
			print(e)
			await ctx.respond(f"There is no giveaway with the name {name}.")

bot.run(TOKEN)


