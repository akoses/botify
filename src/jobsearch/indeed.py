from bs4 import BeautifulSoup
import discord
import aiohttp
import sys
sys.path.append('..')
from utils import fetch
import asyncio

async def find_jobs(job_title: str, location=None):

	async with aiohttp.ClientSession() as session:
		params = {
			'q': job_title,
		}
		if location is not None:
			params['l'] = location
		res = await fetch(session, 'https://ca.indeed.com/jobs', params)
		soup = BeautifulSoup(res, 'html.parser')
		
		res = soup.find_all('a', {'class': ['tapItem', 'fs-unmask', 'result']}) 
		embeds = []
		for job in res:
			title = job.find('h2', {'class': 'jobTitle'})
			company = job.find('span', {'class':'companyName'})
			location = job.find('div', {'class':'companyLocation'})
			if title and company and location:
				
				embed = discord.Embed(
					title=title.text,
					url=f'https://ca.indeed.com{job.get("href")}',
					
				)
				embed.add_field(name="Company", value=company.text, inline=False)
				embed.add_field(name="Location", value=location.text, inline=False)
				embeds.append(embed)
		return embeds[:8]

if  __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(find_jobs('Nurse Extern', 'Scarborough, ON'))
