import requests
from bs4 import BeautifulSoup

def get_libgen_books(query:str):
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
	
	url = 'https://libgen.rs/search.php'
	res = requests.get(url, params=query)
	soup = BeautifulSoup(res.text, 'html.parser')
	results = soup.find_all('tr')
	embeds = []
	for result in results[3:-1]:
		td_tags = result.find_all('td')
		if len(td_tags) < 3:
			continue
		title = td_tags[2].text
		author = td_tags[1].text
		link_tags = td_tags[-4].find_all('a')
		
		embed = {
			'title': title,
			'author': author,
			'link': link_tags[0]['href'],
		}
		embeds.append(embed)
		
	return embeds[:10]

books = get_libgen_books('Lord of the Rings')

