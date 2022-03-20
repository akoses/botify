from bs4 import BeautifulSoup
import discord
import aiohttp
from pyppeteer import launch
import sys
sys.path.append('..')
from utils import fetch
import asyncio
async def find_jobs(job_title: str, location="Canada"):

	async with aiohttp.ClientSession() as session:
		if "Canada" not in location:
			location = f"{location}, Canada"
		params = {
			'keywords': job_title,
			'location': location,
		}
		res = await fetch(session, 'https://www.linkedin.com/jobs/search/', params)
		soup = BeautifulSoup(res, 'html.parser')

		res = soup.find_all('div', {'class':['job-search-card']})
		
		embeds = []
		for job in res:
			title = job.find('h3', {'class': 'base-search-card__title'})
			company = job.find('a', {'class': 'hidden-nested-link'})
			location = job.find('span', {'class': 'job-search-card__location'})
			link = job.find('a', {'class': 'base-card__full-link'})

			if title and company and location:
				print(title.text, company.text, location.text)
				embed = discord.Embed(
					title=title.text,
					url=link.get("href"),
					
				)
				embed.add_field(name="Company", value=company.text, inline=False)
				embed.add_field(name="Location", value=location.text, inline=False)
				embeds.append(embed)
		
		return embeds[:8]

if  __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(find_jobs('Software Engineer Intern', 'Montreal'))
