
from bs4 import BeautifulSoup
import discord
import aiohttp
from utils import fetch

async def get_libgen_books(query:str):
	"""
	Gets all books associated with a lib gen query
	Args:
		query (str): _description_
	"""
	query = {
		'req': query,
		'column': 'def',
		'view': 'simple',
		'phrase': 1,
		'res':25
	}
	async with aiohttp.ClientSession() as session:
		url = 'https://libgen.rs/search.php'
		res = await fetch(session, url, query)
		soup = BeautifulSoup(res, 'html.parser')
		results = soup.find_all('tr')
		embeds = []
		for result in results[3:-1]:
			td_tags = result.find_all('td')
			if len(td_tags) < 3:
				continue
			title = td_tags[2].text
			author = td_tags[1].text
			link_tags = td_tags[-4].find_all('a')
			
			embed = discord.Embed(
				title=title,
				url=link_tags[0]['href']
			)
			if author:
				embed.add_field(name="Author", value=author)
			embeds.append(embed)
			
		return embeds[:10]



