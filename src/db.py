from typing import List
from configparser import ConfigParser
import asyncpg
import discord
from dotenv import load_dotenv
import os
import datetime
load_dotenv()

INSERT_USERS = """INSERT INTO users (discord_id, balance, giveaway_entries, role_name, total_xp, level) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (discord_id) DO NOTHING"""

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)


def config(filename='database.ini', section='postgresql'):
	# create a parser
	parser = ConfigParser()
	# read config file
	path = os.path.abspath(os.path.dirname(__file__))
	parser.read(os.path.join(path, filename))
	
	
	# get section, default to postgresql
	db = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))	
	return db



async def connect():
	"""
	Connect to the database.	
	"""
	db_config = config()	
	conn = await asyncpg.connect(**db_config)
	return conn

async def create_tables():
	"""
	Create all the tables needed for the application.
	"""
	conn = await connect()
	await conn.execute("""CREATE TABLE IF NOT EXISTS users(
		id SERIAL,
		discord_id bigint PRIMARY KEY,
		giveaway_entries int, 
		balance INT, 
		role_name TEXT, 
		total_xp INT, 
		level INT);
	""")

	await conn.execute("""CREATE TABLE IF NOT EXISTS jobs(                                                              
				id SERIAL PRIMARY KEY,                                                                           
				status TEXT,
				name TEXT,
				description TEXT,
				organization TEXT,
				disciplines TEXT,
				channels TEXT[],
				location TEXT,
				applyURL TEXT
				);""")

	await conn.execute("""CREATE TABLE IF NOT EXISTS apply (
		id SERIAL PRIMARY KEY, 
		jobs_id INT,
		discord_id bigint,
		date TIMESTAMP,
		CONSTRAINT apply_jobs_id_fk FOREIGN KEY (jobs_id) REFERENCES jobs (id) ON DELETE CASCADE, 
		CONSTRAINT fk_discord FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE);""")

	
	await conn.execute("""CREATE TABLE IF NOT EXISTS events (                                                                
			id SERIAL PRIMARY KEY,                                                                           
			name TEXT,
			description TEXT,
			hosted_by TEXT,
			status TEXT,
			channels TEXT[], 
			date TIMESTAMP,
			link TEXT);""")
	
	await conn.execute("""CREATE EXTENSION "uuid-ossp";""")

	await conn.execute("""CREATE TABLE IF NOT EXISTS chegg(
		id uuid PRIMARY KEY DEFAULT uuid_generate_v4(), 
		created_at TIMESTAMPTZ DEFAULT NOW(), 
		html TEXT);""")


	await conn.close()
	await conn.close()


async def insert_user(discord_id):
	"""
	Insert a new user into the database.
	"""

	conn = await connect()

	await conn.execute(INSERT_USERS, discord_id, 0, 1, "Lower Year Student", 0, 1)

	await conn.close()


async def get_role(discord_id):
	"""
	Get the role of a user.
	Args:
		discord_id (int): The discord id of the user.
	Returns:
		str: The role of the user.
	"""
 
	conn = await connect()

	row = await conn.fetchrow("SELECT role_name FROM users WHERE discord_id = $1", discord_id)
	
	await conn.close()
	return row.get('role_name')

async def get_user_balance(discord_id):
	"""
	Get the balance of a user.
	Args:
		discord_id (int): The discord id of the user.
	Returns:
		int: The balance of the user.
	"""
	
	conn = await connect()	

	row = await conn.fetchrow("SELECT balance, total_xp, level FROM users WHERE discord_id = $1", discord_id)

	await conn.close()
	return row.get('balance'), row.get('total_xp'), row.get('level')


async def set_user_balance(bal, discord_id):
	"""
	Set the balance of a user.
	Args:
		discord_id (int): The discord id of the user.
		bal (int): The balance of the user.
	"""

	conn = await connect()
	await conn.execute("UPDATE users SET balance = balance + $1 WHERE discord_id = $2", bal, discord_id)

	await conn.close()


async def get_user_rank(discord_id):
	"""
	Get the rank of a user.
	Args:

		discord_id (int): The discord id of the user.
	Returns:
		str: The rank of the user.
	"""
	
	conn = await connect()

	row = await conn.fetchrow("SELECT role_name FROM users WHERE discord_id = $1", discord_id)

	await conn.close()
	return row.get('role_name')


async def get_latest_events():
	"""
	Get the latest events.
	Returns:
		list: A list of the latest events.
	"""

	conn = await connect()
	events = await conn.fetch("UPDATE events SET status='SHOWN' WHERE status='PENDING' RETURNING *")

	await conn.close()
	return events

async def get_latest_jobs():
	"""
	Get the latest jobs.
	Returns:
		list: A list of the latest jobs.
	"""

	conn = await connect()
	jobs = await conn.fetch("UPDATE jobs SET status='SHOWN' WHERE status='PENDING' RETURNING *")

	await conn.close()
	return jobs

async def get_event_name(event_id):
	"""
	Get the name of an event.
	Args:
		event_id (int): The id of the event.
	Returns:
		str: The name of the event.
	"""

	conn = await connect()
	row = await conn.fetchrow("SELECT name FROM events WHERE id = $1", event_id)

	await conn.close()
	if row.get('name'):
		return row.get('name')

async def get_job_name(job_id):
	"""
	Get the name of a job.
	Args:
		job_id (int): The id of the job.
	Returns:
		str: The name of the job.
	"""

	conn = await connect()
	row = await conn.fetchrow("SELECT name FROM jobs WHERE id = $1", job_id)

	if row.get('name'):
		return row.get('name')

async def get_applications(user_id):
	"""
	Get all applications for a user.
	Args:
		user_id (int): The user id.
	Returns:
		list: A list of applications.
	"""
	
	conn = await connect()

	applications = await conn.fetch("""SELECT j.*, a.*
			FROM jobs j, apply a
			WHERE j.id = a.jobs_id
			AND a.discord_id = $1""", user_id)

	return applications


async def get_previous_application(user_id, job_id):
	"""
	Get the previous application of a user.
	Args:
		user_id (int): The user id.
	Returns:
		list: A list of the previous application.
	"""

	conn = await connect()

	rows = await conn.fetch("SELECT * FROM apply WHERE jobs_id = $1 AND discord_id= $2", job_id, user_id)

	return rows



async def apply_to_job(discord_id, jobs_id):
	"""
	Apply to a job for a given user.
	"""
	conn = await connect()

	await conn.execute("""INSERT INTO apply (discord_id, jobs_id, date) SELECT $1, $2, $3
		WHERE NOT EXISTS 
		(SELECT * FROM apply WHERE discord_id = $4 AND jobs_id = $5)""", 
		discord_id, jobs_id, datetime.datetime.now(), discord_id, jobs_id) 


	await conn.close()

async def insert_chegg(html):
	"""
	Insert a new chegg link.
	"""

	conn = await connect()

	row = await conn.fetchrow("""INSERT INTO chegg (html) VALUES ($1) RETURNING id""", html)
	await conn.close()
	return row.get('id')

async def add_salaries(members):
	"""
	Add a salary to a users.
	"""

	conn = await connect()

	await conn.executemany("UPDATE users SET balance = balance + $1 WHERE discord_id = $2", members)

	await conn.close()

async def get_chegg_html(chegg_id):
	"""
	Get the html of a chegg link.
	"""

	conn = await connect()

	row = await conn.fetchrow("SELECT html FROM chegg WHERE id = $1", chegg_id)

	await conn.close()
	return row.get('html')



async def set_role(discord_id, role):
	"""
	Set the role of a user.
	Args:

		discord_id (int): The discord id of the user.
		role (str): The role of the user.
	"""

	if not role:
		return
	conn = await connect()

	await conn.execute("UPDATE users SET role_name=$1 WHERE discord_id = $2", role.name, discord_id)

	await conn.close()


async def get_event(event_id):
	"""
	Get an event.
	Args:
		event_id (int): The event id.
	Returns:
		tuple: The event.
	"""

	conn = await connect()

	event = await conn.fetchrow("SELECT * FROM events WHERE id = $1", event_id)

	await conn.close()
	return event

async def get_entries(discord_id):
	"""
	Get all entries for a user.
	Args:
		discord_id (int): The discord id of the user.
	Returns:
		list: A list of entries.
	"""
	conn = await connect()
	row = await conn.fetchrow("SELECT giveaway_entries FROM users WHERE discord_id = $1", discord_id)

	await conn.close()
	return row.get('giveaway_entries')

async def set_entries(discord_id, entries):
	"""
	Set all entries for a user.
	Args:
		discord_id (int): The discord id of the user.
		entries int: A number of entries.
	"""
	
	conn = await connect()

	await conn.execute("UPDATE users SET giveaway_entries=$1 WHERE discord_id = $2", entries, discord_id)

	await conn.close()

async def insert_many_users(users:List[str]):
	"""	
	Insert many users into the database.
	"""
	conn = await connect()
	mapped_users = []
	def fn(discord_id):
		return (discord_id, 0, 10, "Lower Year Student", 0, 1)
	
	for user in users:
		new_user = fn(user)
		mapped_users.append(new_user)
	
	await conn.executemany(INSERT_USERS, mapped_users)

	await conn.close()
	print("Inserted all users")


async def get_xp_levels(
	discord_id
):
	"""
	Get the xp levels of a user.
	"""
	conn = await connect()


	row = await conn.fetchrow("SELECT total_xp, level FROM users WHERE discord_id = $1", discord_id)


	await conn.close()
	return row.get('total_xp'), row.get('level')


async def set_xp_levels(
	discord_id,
	total_xp,
	level,
	entries=0
	):
	"""
	Set the xp levels of a user.
	"""
	conn = await connect()
	await conn.execute("UPDATE users SET total_xp = $1, level = $2, giveaway_entries = giveaway_entries + $3 WHERE discord_id = $4", total_xp, level, entries, discord_id)
	await conn.close()


async def delete_invites(channel_id):
	"""
	Delete all invites from a channel.
	Args:
		channel_id (int): The channel id.
	"""

	welcome_channel = client.get_channel(channel_id)
	invites = await welcome_channel.invites()
	for invite in invites:
		if invite.inviter == client.user:
			await invite.delete()
	print("Deleted all bot invites")

@client.event
async def on_ready():
	"""
	This event is called when the bot is ready.
	"""
	
	print(f'{client.user.name} has connected to Discord!')
	await create_tables()
	members = client.guilds[0].members
	await insert_many_users(list(map(lambda x: x.id, members)))
	await client.close()




if __name__ == '__main__':
	client.run(TOKEN)