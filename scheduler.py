import asyncio
import random
import discord
import datetime
from pytz import timezone
from utils import *
from db import get_event
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

jobstores = {
	'default': RedisJobStore(),
}

scheduler = AsyncIOScheduler(event_loop=bot.loop, jobstores=jobstores)


async def create_giveaway(ctx, name, prize, winners, gtime, description):
	giveaway_time = datetime.datetime.now(timezone('Canada/Mountain')) + datetime.timedelta(hours=int(gtime))
	
	giveaway = discord.Embed(
		title=name,
		description=description,
		color=0xAFC2D5
	)

	giveaway.add_field(name="Prize  :money_with_wings: ", value=f"{prize}")
	giveaway.add_field(name="Winners :trophy:", value=f"{winners} ")
	giveaway.add_field(name="Draw Date :hourglass:", value=f"{giveaway_time.strftime('%B %d, %Y %I:%M %p')} ")
	giveaway.set_footer(text=f"Use the /giveaway enter {name} command to enter the giveaway.")
	
	giveaway_obj = {
		'name': name,
		'prize': prize,
		'winners': winners,
		'description': description,
		'giveaway_time': giveaway_time,
		'entries':[]
	}

	
	redisClient.set(name, json.dumps(giveaway_obj, default=str))
	redisClient.sadd('giveaways', name)
	await ctx.channel.send(embed=giveaway)
	
	scheduler.add_job(end_giveaway, 'date', run_date=giveaway_time, timezone=timezone('Canada/Mountain'), args=[name])

def giveaway_entry(user, name, entries):
	
	giveaway_obj = json.loads(redisClient.get(name))
	
	entry = {
		'user': user.id,
		'username': user.name,
		'entries': entries
	}

	giveaway_obj['entries'].append(entry)
	redisClient.set(name, json.dumps(giveaway_obj, default=str))


async def end_giveaway(gid):
	giveaway = json.loads(redisClient.get(gid))
	redisClient.delete(gid)
	redisClient.srem('giveaways', gid)
	entries = giveaway['entries']
	if len(entries) < 1:
		await bot.get_channel(939423795763105825).send(content=f"**No one entered {giveaway['name']} so there are no winners! :cry:**")
		return
	entry_weights = map(lambda e: e['entries'], entries)

	# The number of winners for the giveaway
	winners = giveaway['winners']
	choices = random.choices(entries, weights=entry_weights, k=winners)
	# The prize for the giveaway
	prize = giveaway['prize']
	embeds = []

	for entry in choices:
		user = bot.get_user(entry['user'])
		avatar = user.avatar
		embed = discord.Embed(
		title=f" {giveaway['name']} Winner",
		
		description=f"Congratulations, {user.mention} has won: {prize}!",
		color=0xABC2D5)
		embed.set_thumbnail(url=avatar.url)
		embeds.append(embed)

	if len(embeds) > 0:	
		await bot.get_channel(939423795763105825).send(content=f"**Winner of {giveaway['name']}**", embed=embeds[0])
	else:
		await bot.get_channel(939423795763105825).send(content=f"Winners of {giveaway['name']}", embeds=embeds)
	
		
async def notify_event(event_id):
	
	event = get_event(event_id)
	embed = discord.Embed(
		title=f"**{event[2]}**",
		description=f"{event[3]}",
		color=0xABC2D5,
	)
	
	embed.add_field(name="Hosted By", value=f"{event[4]}")
	embed.set_footer(text=event[7])
	user_ids = list(map(int, redisClient.smembers(str(event_id))))
	users = list(map(bot.get_user, user_ids))
	button = discord.ui.Button(style=discord.ButtonStyle.link, url=event[7], label='Join Event')
	view = discord.ui.View()
	view.add_item(button)
	for user in users:
		await user.send(content=f"**{event[2]} is starting right away!**", embed=embed, view=view)

	redisClient.delete(event_id)



	