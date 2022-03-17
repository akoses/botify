from bs4 import BeautifulSoup
import urllib
import asyncio
import discord
from pyppeteer import launch

async def find_content(question:str):
	
	base_url = 'https://quizlet.com/search'
	params = {
		'query':question,
		'type':'sets',
	}
	
	query = urllib.parse.urlencode(params)
	browser = await launch(options={'args': ['--no-sandbox']})
	page = await browser.newPage()
	await page.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36");
	url = base_url+'?'+ query
	await page.goto(url, {'waitUntil': 'networkidle2'})
	card_container = await page.querySelector('.SetsView-resultList')
	cards = await card_container.querySelectorAll('.SetPreviewCard-metadata')
	embeds = []
	for i in range(len(cards)):	
		await page.waitForSelector('.SetPreviewCard-metadata')
		
		cards = await page.querySelectorAll('.SetPreviewCard-metadata')
		title = await cards[i].querySelector('.SetPreviewCard-title')
		terms = await cards[i].querySelector('.AssemblyPillText')
		title = await page.evaluate('el => el.textContent', title)
		terms = await page.evaluate('el => el.textContent', terms)
		await page.evaluate('card => card.click()', cards[i])
		await page.waitFor(800)
		
		embed = discord.Embed(
				title=title,
				url=page.url,
			)
		embed.add_field(name="Terms", value=terms, inline=False)
		embeds.append(embed)
		await page.waitFor(800)
		await page.goBack()
		
	
	return embeds


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(find_content('Chem 101'))
