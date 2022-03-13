import requests
from bs4 import BeautifulSoup
import urllib.parse
import discord
import aiohttp
from utils import fetch

async def find_jobs(job_title: str):
	
	async with aiohttp.ClientSession() as session:
		params = {
			'keywords': job_title,
			'location': 'Canada',
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
				embed = discord.Embed(
					title=title.text,
					url=link.get("href"),
					
				)
				embed.add_field(name="Company", value=company.text, inline=False)
				embed.add_field(name="Location", value=location.text, inline=False)
				embeds.append(embed)
			
		return embeds[:5]

