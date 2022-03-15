import discord
import datetime
from dotenv import load_dotenv
from discord.commands import Option, permissions
from discord.ext import tasks
from pytz import timezone
import books.libgen as libgen
import Rankcard
from io import BytesIO


from db import (
	get_user_balance, 
	get_user_rank, 
	insert_user, 
	get_role, 
	apply_to_job, 
	get_applications, 
	add_salaries, 
	get_entries, 
	set_entries, 
	get_latest_events,
	get_latest_jobs,
	get_event_name,
	get_job_name,
	get_previous_application, 
)

from views import *
from xp import assign_xp, curr_xp_for_level, get_xp
from utils import *
from roles.roles import IGNORE_ROLES, ROLE_TO_SALARY, role_or_higher
from scheduler import *
import quizlet
import chegg as chg

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

rankcard = Rankcard.RANKCARD()

async def college_search(ctx:discord.AutocompleteContext):
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	return [college for college in college_roles]

async def giveaway_search(ctx:discord.AutocompleteContext):
	if not await redisClient.exists('giveaways'):
		return []
	
	return list(map(lambda x: x.decode('utf-8'), await redisClient.smembers('giveaways')))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL')
ADMIN_ROLE = int(os.getenv('ADMIN_ROLE'))
POLLS_CHANNEL = int(os.getenv('POLLS_CHANNEL'))
invite_map = dict()

guild_ids = [939394818428243999]

@tasks.loop(time=[datetime.time(hour=3, minute=0, second=0)], reconnect=True)
async def get_would_you_rather():
	question, answers = await get_poll()
	if question and answers:
		embed = discord.Embed(title=question, color=0xbaffc0)
		for i, answer in enumerate(answers):
			embed.add_field(name = f':{index_to_num[i + 1]}:',  value=answer, inline=False)
		
		curr_mess = await bot.get_channel(POLLS_CHANNEL).send(embed=embed)
		for i in range(len(answers)):
			emoji = index_to_unicode[i + 1]
			await curr_mess.add_reaction(emoji)

@tasks.loop(time=[datetime.time(hour=6, minute=0, second=0)])
async def pay_salaries():
	for role in ROLE_TO_SALARY:
		salary = ROLE_TO_SALARY[role]
		members = discord.utils.get(bot.guilds[0].roles, name=role).members

		members = map(lambda x: (salary, x.id), members)
		await add_salaries(members)
		print("All salaries paid for role: %s" % role)
		

@tasks.loop(time=[datetime.time(hour=6, minute=0, second=0)], reconnect=True)
async def loop_trivia_question():
	question, correct, answers = await get_trivia_question()
	
	if question and correct and answers:
		trivia = {
		"question": question,
		"correct": correct,
		"answers": answers
		}
		trivia_json = json.dumps(trivia)
	await redisClient.set("trivia", trivia_json)
	await redisClient.delete("trivia-players")
	prize = determine_trivia_prize()
	await redisClient.set("trivia-prize", prize)

@tasks.loop(seconds=30)
async def check_events():
	events = await get_latest_events()
	if events:
		for event in events:
			channels = event.get('channels')
			if channels:
				for channel in channels:
					channel = bot.get_channel(int(channel))
					if channel:
						embed = discord.Embed(title=event.get('name'), description=event.get('description'), color=0xffffff)
						embed.add_field(name="Hosted by", value=event.get('hosted'), inline=False)
						embed.add_field(name="Date", value=event.get('date'), inline=False)
						embed.set_footer(text="Event ID: %s" % event.get('id'))
						link =  event.get('link')
						view = LinkView(link, "Event Link")
						view.add_item(EventButton(event.get('id'), event.get('name')))
						await channel.send(embed=embed, view=view)
						scheduler.add_job(notify_event, 'date', run_date=event.get('date'), timezone=timezone('Canada/Mountain'), args=[event.get('id')])
					
					
@tasks.loop(seconds=30)
async def check_jobs():
	jobs = await get_latest_jobs()
	
	if jobs:
		for job in jobs:
			channels = job.get('channels')
			if channels:
				for channel in channels:
					if channel:
						channel = bot.get_channel(int(channel))
						embed = discord.Embed(title=job.get('name'), description=job.get('description'), color=0x00ffff)
						embed.add_field(name="Organization", value=job.get('organization'), inline=False)
						embed.add_field(name="Location", value=job.get('location'), inline=False)
						embed.add_field(name="Disciplines", value=job.get('disciplines'), inline=False)
						embed.set_footer(text="JOB ID: %s" % job.get('id'))
						link =  job.get('applyurl')
						view = LinkView(link, "Apply URL")
						view.add_item(JobButton(job.get('id'), job.get('name')))
						await channel.send(embed=embed, view=view)
					
							
@bot.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	print(f'{bot.user.name} has connected to Discord!')
	invites = await bot.guilds[0].invites()
	for invite in invites:
		invite_map[invite.code] = invite
	
	scheduler.start()
	global guild_ids
	guild_ids = list(map(lambda x: x.id,bot.guilds))

	print(guild_ids)
	if not get_would_you_rather.is_running():
		get_would_you_rather.start()

	if not pay_salaries.is_running():
		pay_salaries.start()
	
	if not loop_trivia_question.is_running():
		loop_trivia_question.start()

	if not check_events.is_running():
		check_events.start()
	
	if not check_jobs.is_running():
		check_jobs.start()



@bot.event
async def on_invite_create(invite):
	"""
	This event is called when a new invite is created.
	"""
	invite_map[invite.code] = invite

@bot.event
async def on_interaction(interaction):

	if str(interaction.type) == "InteractionType.application_command":
		await bot.process_application_commands(interaction)
	if interaction.message:
		components = interaction.message.components
		if components and len(components[0].children) == 2:

			await interaction.response.defer()
			button = components[0].children[1]

			component_id = button.custom_id
			if await redisClient.sismember('interaction-ids', str(interaction.id)):
				return
			interaction_type = await redisClient.hget("type-"+component_id, "TYPE")
			if interaction_type:
				interaction_type = interaction_type.decode("utf-8") 
				if interaction_type == "EVENT":
					event_name = await redisClient.hget("type-"+component_id, "NAME")
					if await redisClient.sismember(component_id, interaction.user.id):
						await interaction.user.send("You have already registered for this event.")
						return
					await assign_xp(bot, "ATTEND_EVENT", interaction.user.id)
					await redisClient.sadd(component_id, interaction.user.id)

					await interaction.user.send(content="You have successfully signed up to be notified of {}!".format(event_name.decode("utf-8")))
				elif interaction_type == "JOB":
					job_name = await redisClient.hget("type-"+component_id, "NAME")
					previous_application = await get_previous_application(interaction.user.id, int(component_id))
					if previous_application:
						await interaction.user.send("You have already applied to this job.")
						return
					await apply_to_job(interaction.user.id, int(component_id))
					await assign_xp(bot, "APPLY", interaction.user.id)
					await interaction.user.send(content="You have successfully applied to {}!".format(job_name))

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
	await insert_user(member.id)
	invites_after_join = await member.guild.invites()

	for invite in invite_map.values():
		if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
			inviter = invite.inviter
			
			await assign_xp(bot, "REFERRAL", inviter.id)
			role = discord.utils.get(member.guild.roles, name="Lower Year Student")
			await member.add_roles(role)

@bot.slash_command(name="ping", description="Pong!", guild_ids=guild_ids)
async def ping(ctx):
	await ctx.respond('Pong!')


@bot.slash_command(name="balance", description="Shows the current balance for a user's account", guild_ids=guild_ids)
async def balance(ctx):
	bal = await get_user_balance(ctx.interaction.user.id)
	embed = discord.Embed(
		title=f"{ctx.interaction.user.name}'s Account",
		colour=discord.Colour.from_rgb(123, 221, 98),
	)
	embed.add_field(name="🏦 Balance 🏦", value=bal[0])
	await ctx.interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="rank", description="Shows the ranking for a given user",guild_ids=guild_ids)
async def rank(ctx):
	await ctx.defer()	
	
	rank = await get_user_rank(ctx.interaction.user.id)
	total_xp, level = await get_xp_levels(ctx.interaction.user.id)
	curr_xp = curr_xp_for_level(total_xp, level)
	next_xp = get_xp(level + 1)
	avatar_url = ''
	if not ctx.interaction.user.avatar:
		dis = int(ctx.interaction.user.discriminator) % 5
		avatar_url = f'https://cdn.discordapp.com/embed/avatars/{str(dis)}.png'
	else:
		avatar_url = ctx.interaction.user.avatar.url
	card = rankcard.rank_card(
		username=ctx.interaction.user.name,
		avatar=avatar_url,
		level=level,
		rank=rank,
		current_xp=curr_xp,
		custom_background='#202020',
		xp_color='#1E90FF',
		next_level_xp=next_xp
	)
	with BytesIO() as file:
		card.save(file, "PNG")
		file.seek(0)
		f = discord.File(file, filename="rankcard.png")
		await ctx.send(file=f)
		await ctx.delete()

@bot.slash_command(name="apply", description="Apply to a certain job given a job id. Use this as an application tracker.",guild_ids=guild_ids)
async def apply(ctx,
	job_id: Option(int, "Enter the job id to apply")
):
	previous_application = await get_previous_application(ctx.interaction.user.id, job_id)
	if previous_application:
		await ctx.interaction.response.send_message("You have already applied to this job.")
		return
	
	job_name = await get_job_name(job_id)
	if not job_name:
		await ctx.interaction.response.send_message("There is no job with that id.")
		return
	await ctx.respond(f"Successfully tracking job **{job_name}** for {ctx.interaction.user.mention}")
	await apply_to_job(ctx.interaction.user.id, job_id)
	await assign_xp(bot, "APPLY", ctx.interaction.user.id)	

@bot.slash_command(name="salary", description="Shows a user's current salary.", guild_ids=guild_ids)
async def salary(ctx):
	role = await get_role(ctx.interaction.user.id)
	embed = discord.Embed(
		title=f"💸 Your current salary is ${ROLE_TO_SALARY[role]} 💸"
	)
	await ctx.respond(embed=embed)


@bot.slash_command(name="applications", description="Show all my current applications",guild_ids=guild_ids)
async def applications(ctx):
	apps = await get_applications(ctx.interaction.user.id)
	if not apps:
		await ctx.respond("You have no applications.")
		return
	for app in apps:
		embed = discord.Embed(
			title=f"{app.get('name')}",
		)
		embed.add_field(name="Organization", value=app.get('organization'), inline=False)
		embed.add_field(name="Location", value=app.get('location'), inline=False)
		embed.add_field(name="📝Application Date 📝", value=app.get('date').strftime("%Y-%m-%d %H:%M:%S"), inline=False)
		view = LinkView(app.get('applyurl'), "Apply URL")
		await ctx.respond(embed=embed, view=view)


@bot.slash_command(name="attend-event" ,description="Attend an event given an event id. You will be given a reminder for the event to start.",guild_ids=guild_ids)
async def attendevent(ctx, event_id: Option(int, "Enter the event id")):
	
	event_name = await get_event_name(event_id)
	previous_event = await redisClient.sismember(str(event_id), str(ctx.interaction.user.id))
	if previous_event:
		await ctx.interaction.response.send_message("You have already signed up for this event.")
		return
	if not event_name:
		await ctx.interaction.response.send_message("There is no event with that id.")
		return
	await redisClient.sadd(str(event_id), str(ctx.interaction.user.id))
	await assign_xp(bot, "ATTEND_EVENT", ctx.interaction.user.id)
	await ctx.respond(content="You have successfully signed up to be notified of {}!".format(event_name))



@bot.slash_command(name="trivia", description="Play a trivia game to win coins! You can only play once per day.",guild_ids=guild_ids)
async def trivia(ctx):
	if await redisClient.sismember('trivia-players', ctx.interaction.user.id):
		await ctx.interaction.response.send_message("You've already played today! Come back tomorrow to play again.", ephemeral=True)
		return
	trivia_message = f"""
	Hello **{ctx.interaction.user.name}**, welcome to the trivia game! \nYou will answer one question and if your answer is correct, you will be awarded between **1000** and **100,000** coins.\nYou will have **10** seconds to answer the question.\nPress the start button in order to begin!
	"""
	triviaView = TriviaView()  
	await ctx.interaction.response.send_message(trivia_message, ephemeral=True, view=triviaView)
	
	
@bot.slash_command(name="quizlet", description="Searches for quiz sets on Quizlet", guild_ids=guild_ids)
async def quizlet_search(ctx,
	query: Option(str, "What are you looking for?")
):
	await ctx.defer()
	embeds = await quizlet.find_content(query)
	
	if not embeds:
		await ctx.send("Nothing was found.")
		return
	for embed in embeds:
		await ctx.send(embed=embed)
	await ctx.delete()


@bot.slash_command(name="assign-xp", description="Assign XP to a user",guild_ids=guild_ids)
@permissions.has_role(ADMIN_ROLE)
async def assign_xp_to_user(ctx,
	xp: Option(int, "Enter the amount of XP to assign"),
	user: Option(discord.User, "Enter the user to assign XP to")):
	await assign_xp(bot, xp, user.id, xp)
	await ctx.respond(f"Assigned {xp} XP to {user.name}")



@bot.slash_command(name="chegg", description="Convert's chegg link to unblocked content.", guild_ids=guild_ids)
@permissions.has_any_role(*role_or_higher("Professor"))
async def chegg(ctx,
	link: Option(str, "Enter the chegg link")):
	await ctx.defer()
	chegg_link = await chg.convert_link(link)
	view = LinkView(chegg_link, "View Your Chegg")
	await ctx.respond(view=view)

@bot.slash_command(name="books", description="Search for a book or textbook with LibGen",guild_ids=guild_ids)
async def books(ctx,
	title: Option(str, "Enter the book name or author")):
	await ctx.defer()
	embeds = await libgen.get_libgen_books(title)
	if not embeds:
		await ctx.respond("No books found")
	else:
		for embed in embeds:
			await ctx.respond(embed=embed)
		await ctx.delete()

##################################
#College Commands 
##################################
colleges = bot.create_group(name="colleges",
description="Commands for displaying and joining colleges")

@colleges.command(name="join", description="Join a college", guild_ids=guild_ids)
async def join(ctx,
	college: Option(str, "Enter the college name", autocomplete=college_search)
):	
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	role = discord.utils.get(ctx.interaction.guild.roles, name=college)
	if role and role.name in college_roles:
		await ctx.interaction.user.add_roles(role)
		await ctx.respond(f"You have now joined the {college} college!")
	else:
		await ctx.respond("That college does not exist.")
	

@colleges.command(name="list", description="Shows the available colleges", guild_ids=guild_ids)
async def display_colleges(ctx):
	college_roles = set(map(lambda x: x.name, ctx.interaction.guild.roles)) - IGNORE_ROLES
	embed = discord.Embed(
		title="Available Colleges",
		colour=discord.Colour.from_rgb(23, 121, 198),
	)
	for role in college_roles:
		embed.add_field(name=role, value=f"`/colleges join {role}`", inline=False)
	await ctx.respond(embed=embed)

@colleges.command(name="create", description="Request to create a new college",guild_ids=guild_ids)
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

@giveaway.command(name="start", description="Start a giveaway",guild_ids=guild_ids)
async def start_giveaway(ctx):
	
	def auth_check(m):
		return m.author == ctx.interaction.user

	def num_check (m):
		return m.author == ctx.interaction.user and is_valid_decimal(m.content)

	try:
		await ctx.delete()
		await ctx.respond(f"Hello {ctx.interaction.user.mention}, what is the name of your giveaway?")
		giveaway_name = await bot.wait_for('message', timeout=60,  check=auth_check)
		await ctx.respond(f"What is the prize for the giveaway?")
		giveaway_prize = await bot.wait_for('message', timeout=60, check=auth_check)
		await ctx.respond(f"How many winners do you want?")
		giveaway_winners = await bot.wait_for('message', timeout=60,check=num_check)
		await ctx.respond(f"How many hours do you want the giveaway to last?")
		giveaway_time = await bot.wait_for('message', timeout=60,  check=num_check)
		await ctx.respond(f"What is the description for the giveaway?", )
		giveaway_description = await bot.wait_for('message', timeout=60, check=auth_check)
		await ctx.respond(f"What is the required level to enter the giveaway?")
		giveaway_level = await bot.wait_for('message', timeout=60, check=num_check)
		await ctx.channel.purge(limit=14)
		await ctx.respond(f"Your giveaway has been created and is scheduled to be drawn in {giveaway_time.content} hours.")
		await create_giveaway(ctx, giveaway_name.content, 
			giveaway_prize.content, 
			int(giveaway_winners.content), 
			float(giveaway_time.content), 
			giveaway_description.content,
			int(giveaway_level.content))
	
	except asyncio.TimeoutError:
		await ctx.respond("You took too long to answer a question. Cancelling giveaway.")
		return
	


@giveaway.command(name="enter", description="Enter a giveaway", guild_ids=guild_ids)
async def enter_giveaway(ctx, 
	name:Option(str, "Enter the name of the giveaway",
	autocomplete=giveaway_search),
	entries: Option(int, "Enter the number of entries. Defaults to 1", default=1)):
	entry_count = await get_entries(ctx.interaction.user.id)
	_, curr_level = await get_xp_levels(ctx.interaction.user.id)
	giveaway_obj = await redisClient.get(name)
	if giveaway_obj:
		giveaway_obj = json.loads(giveaway_obj)
		if giveaway_obj['required_level'] > curr_level:
			await ctx.respond(f"You do not meet the required level to enter this giveaway.")
			return

	if entry_count < entries:
		await ctx.respond(f"Sorry, you do not have enough giveaway entries. You have {entry_count} entries.")
	else:
		try:
			await giveaway_entry(ctx.interaction.user, name, entries)
			await ctx.respond(f"You have entered {entries} entries. You now have {entry_count - entries} entries remaining.")
			await set_entries(ctx.interaction.user.id, entry_count - entries)
		except Exception as e:
			print(e)
			await ctx.respond(f"There is no giveaway with the name {name}.")

bot.run(TOKEN)


