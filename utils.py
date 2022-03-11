import json
import random
import aiohttp
import asyncio
import html
import discord
from discord.ext import commands
import redis

intents = discord.Intents().all()
TRIVIA_PLAYERS = set()
bot = commands.Bot(intents=intents)
redisClient =  redis.Redis(host='localhost', port=6379, db=0)

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
	



if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(get_poll())
