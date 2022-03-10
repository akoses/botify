import json
import random
import aiohttp
import asyncio
import html
import discord
import datetime
CURRENT_GIVEAWAYS = dict()

def days_to_seconds(days):
	return days * 86400

def find_invite_by_code(invite_list, code):
    for inv in invite_list:     
        if inv.code == code:      
            return inv

async def fetch(session, url, params=''):
    async with session.get(url, params=params) as response:
        return await response.text()


async def get_poll():
	data = {}

	async with aiohttp.ClientSession() as session:
		try:
			data = await fetch(session, "https://www.reddit.com/r/WouldYouRather/top.json?sort=top&t=day&limit=10")
			data = json.loads(data)
			poll = data['data']['children'][random.randrange(10)]['data']
			poll_question = poll['title']
			poll_answers = list(map(lambda x: x['text'], poll['poll_data']['options']))
			return poll_question, poll_answers[:10]
		except Exception as e:
			print(e)
			return None, None


async def get_trivia_question():
	data = {}
	async with aiohttp.ClientSession() as session:
		try:
			data = await fetch(session, "https://opentdb.com/api.php?amount=1&type=multiple")
			data = json.loads(data)
			
			question = data['results'][0]['question']
			question = html.unescape(question)
			correct_answer = data['results'][0]['correct_answer']
			correct_answer = html.unescape(correct_answer)
			incorrect_answers = data['results'][0]['incorrect_answers']
			incorrect_answers = list(map(html.unescape, incorrect_answers))
			return question, correct_answer, incorrect_answers
		except Exception as e:
			return None, None, None

def determine_trivia_prize():
	choices = [1000*i for i in range(1, 101)]
	weights = [1.07**i for i in reversed(range(1, 101))]
	
	return random.choices(choices, weights=weights, k=1)[0]


async def create_giveaway(ctx, name, prize, winners, time, description):
	giveaway_time = datetime.datetime.now() + datetime.timedelta(hours=int(time))
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

	global CURRENT_GIVEAWAYS
	CURRENT_GIVEAWAYS[name] = giveaway_obj

	await ctx.channel.send(embed=giveaway)


async def giveaway_entry(ctx, name, entries):
	
	giveaway_obj = CURRENT_GIVEAWAYS[name]
	entry = {
			'user': ctx.author.id,
		'username': ctx.author.name,
		'entries': entries
	}

	giveaway_obj['entries'].append(entry)




if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(get_poll())
