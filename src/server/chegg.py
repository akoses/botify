from flask import Flask
from db import get_chegg_html

app = Flask(__name__)

@app.route('/chegg/<chegg_id>')
async def get_chegg(chegg_id):
	html = await get_chegg_html(chegg_id)
	return html