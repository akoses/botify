from flask import Flask
import sys
sys.path.append("..")
from db import get_chegg_html

app = Flask(__name__)
app.secret_key = '65424aade74fb238e247c341'
@app.route('/chegg/<chegg_id>')
async def get_chegg(chegg_id):
	html = await get_chegg_html(chegg_id)
	return html


if __name__ == "__main__":
	app.run()
