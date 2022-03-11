from typing import List
from configparser import ConfigParser
import psycopg2
import discord
from dotenv import load_dotenv
import os
import datetime
load_dotenv()

INSERT_USERS = """INSERT INTO users (discord_id, balance, giveaway_entries, role_name, total_xp, level) VALUES (%s, %s, %s, %s, %s, %s)"""

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)


def config(filename='database.ini', section='postgresql'):
	# create a parser
	parser = ConfigParser()
	# read config file
	parser.read(filename)

	# get section, default to postgresql
	db = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))	

	return db



def connect():
	"""
	Connect to the database.	
	"""
	db_config = config()	
	conn = psycopg2.connect(**db_config)
	return conn

def create_tables():
	"""
	Create all the tables needed for the application.
	"""
	conn = connect()
	cur = conn.cursor()
	cur.execute("""CREATE TABLE IF NOT EXISTS users(
		id SERIAL,
		discord_id bigint PRIMARY KEY,
		giveaway_entries int, 
		balance INT, 
		role_name TEXT, 
		total_xp INT, 
		level INT);
	""")

	cur.execute("""CREATE TABLE IF NOT EXISTS jobs(                                                              
				id SERIAL PRIMARY KEY,                                                                           
				discord_id bigint,
				status TEXT,
				name TEXT,
				description TEXT,
				organization TEXT,
				disciplines TEXT,
				channel bigint,
				location TEXT,
				applyURL TEXT
				);""")

	cur.execute("""CREATE TABLE IF NOT EXISTS apply (
		id SERIAL PRIMARY KEY, 
		jobs_id INT,
		discord_id bigint,
		date TIMESTAMP,
		CONSTRAINT apply_jobs_id_fk FOREIGN KEY (jobs_id) REFERENCES jobs (id) ON DELETE CASCADE, 
		CONSTRAINT fk_discord FOREIGN KEY(discord_id) REFERENCES users(discord_id) ON DELETE CASCADE);""")

	

	cur.execute("""CREATE TABLE IF NOT EXISTS events(                                                                
			id SERIAL PRIMARY KEY,                                                                           
			discord_id bigint,
			name TEXT,
			description TEXT,
			hosted_by TEXT,
			status TEXT,
			channel bigint, 
			date TIMESTAMP,
			link TEXT);""")
	
	conn.commit()
	cur.close()
	conn.close()


def insert_user(discord_id):
	"""
	Insert a new user into the database.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute(INSERT_USERS, (discord_id, 0, 1, "Lower Year Student", 0, 1))
	conn.commit()
	cur.close()
	conn.close()


def get_role(discord_id):
	"""
	Get the role of a user.
	Args:
		discord_id (int): The discord id of the user.
	Returns:
		str: The role of the user.
	"""
 
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT role_name FROM users WHERE discord_id = %s", (discord_id,))
	role = cur.fetchone()
	cur.close()
	conn.close()
	return role[0]

def get_user_balance(discord_id):
	"""
	Get the balance of a user.
	Args:
		discord_id (int): The discord id of the user.
	Returns:
		int: The balance of the user.
	"""
	
	conn = connect()	
	cur = conn.cursor()
	cur.execute("SELECT balance, total_xp, level FROM users WHERE discord_id = %s", (discord_id,))
	balance = cur.fetchone()
	cur.close()
	conn.close()
	return balance


def set_user_balance(bal, discord_id):
	"""
	Set the balance of a user.
	Args:
		discord_id (int): The discord id of the user.
		bal (int): The balance of the user.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET balance = balance + %s WHERE discord_id = %s", (bal, discord_id))
	conn.commit()
	cur.close()
	conn.close()


def get_user_rank(discord_id):
	"""
	Get the rank of a user.
	Args:

		discord_id (int): The discord id of the user.
	Returns:
		str: The rank of the user.
	"""
	
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT role_name FROM users WHERE discord_id = %s", (discord_id,))
	rank = cur.fetchone()[0]
	cur.close()
	conn.close()
	return rank


def get_latest_events():
	"""
	Get the latest events.
	Returns:
		list: A list of the latest events.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE events SET status='SHOWN' WHERE status='PENDING' RETURNING *")
	events = cur.fetchall()
	conn.commit()
	cur.close()
	conn.close()
	return events

def get_latest_jobs():
	"""
	Get the latest jobs.
	Returns:
		list: A list of the latest jobs.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE jobs SET status='SHOWN' WHERE status='PENDING' RETURNING *")
	jobs = cur.fetchall()
	conn.commit()
	cur.close()
	conn.close()
	return jobs

def get_event_name(event_id):
	"""
	Get the name of an event.
	Args:
		event_id (int): The id of the event.
	Returns:
		str: The name of the event.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT name FROM events WHERE id = %s", (event_id,))
	name = cur.fetchone()
	cur.close()
	conn.close()
	if name:
		return name[0]

def get_job_name(job_id):
	"""
	Get the name of a job.
	Args:
		job_id (int): The id of the job.
	Returns:
		str: The name of the job.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT name FROM jobs WHERE id = %s", (job_id,))
	name = cur.fetchone()
	cur.close()
	conn.close()
	if name:
		return name[0]

def get_applications(user_id):
	"""
	Get all applications for a user.
	Args:
		user_id (int): The user id.
	Returns:
		list: A list of applications.
	"""
	
	conn = connect()
	cur = conn.cursor()
	cur.execute("""SELECT j.name, j.organization, j.applyURL, j.location, a.date FROM jobs j INNER JOIN apply a ON j.id = (SELECT jobs_id FROM apply WHERE discord_id = %s) LIMIT 10""", (user_id,))

	applications = cur.fetchall()

	cur.close()
	conn.close()
	return applications


def get_previous_application(user_id, job_id):
	"""
	Get the previous application of a user.
	Args:
		user_id (int): The user id.
	Returns:
		list: A list of the previous application.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT * FROM jobs WHERE id = %s AND discord_id= %s", (job_id, user_id))

	application = cur.fetchone()
	cur.close()
	conn.close()
	return application



async def apply_to_job(discord_id, jobs_id):
	"""
	Apply to a job for a given user.
	"""
	conn = connect()
	cur = conn.cursor()
	cur.execute("""INSERT INTO apply (discord_id, jobs_id, date) SELECT %s, %s, %s
		WHERE NOT EXISTS 
		(SELECT * FROM apply WHERE discord_id = %s AND jobs_id = %s)""", 
		(discord_id, jobs_id, datetime.datetime.now(), discord_id, jobs_id)) 

	conn.commit()
	cur.close()
	conn.close()


async def add_salaries(members):
	"""
	Add a salary to a users.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.executemany("UPDATE users SET balance = balance + %s WHERE discord_id = %s", members)
	conn.commit()
	cur.close()
	conn.close()



async def set_role(discord_id, role):
	"""
	Set the role of a user.
	Args:

		discord_id (int): The discord id of the user.
		role (str): The role of the user.
	"""
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET role_name=%s WHERE discord_id = %s", (role.name, discord_id))
	conn.commit()
	cur.close()
	conn.close()

async def attend_event(discord_id, event_id):
	"""
	Attend an event for a given user.
	"""
	conn = connect()
	cur = conn.cursor()
	cur.execute("INSERT INTO attend_event (discord_id, event_id) VALUES (%s, %s)", (discord_id, event_id))
	conn.commit()
	cur.close()
	conn.close()


def get_event(event_id):
	"""
	Get an event.
	Args:
		event_id (int): The event id.
	Returns:
		tuple: The event.
	"""

	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
	event = cur.fetchone()
	cur.close()
	conn.close()
	return event

async def get_entries(discord_id):
	"""
	Get all entries for a user.
	Args:
		discord_id (int): The discord id of the user.
	Returns:
		list: A list of entries.
	"""
	
	conn = connect()
	cur = conn.cursor()
	cur.execute("SELECT giveaway_entries FROM users WHERE discord_id = %s", (discord_id,))
	entries = cur.fetchone()
	cur.close()
	conn.close()
	return entries[0]

async def set_entries(discord_id, entries):
	"""
	Set all entries for a user.
	Args:
		discord_id (int): The discord id of the user.
		entries int: A number of entries.
	"""
	
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET giveaway_entries=%s WHERE discord_id = %s", (entries, discord_id))
	conn.commit()
	cur.close()
	conn.close()

async def insert_many_users(users:List[str]):
	"""	
	Insert many users into the database.
	"""
	conn = connect()
	cur = conn.cursor()
	mapped_users = []
	def fn(discord_id):
		return (discord_id, 0, 10, "Lower Year Student", 0, 1)
	
	for user in users:
		new_user = fn(user)
		mapped_users.append(new_user)
	
	cur.executemany(INSERT_USERS, mapped_users)
	conn.commit()
	cur.close()
	conn.close()
	print("Inserted all users")


def get_xp_levels(
	discord_id
):
	"""
	Get the xp levels of a user.
	"""
	conn = connect()
	cur = conn.cursor()

	cur.execute("SELECT total_xp, level FROM users WHERE discord_id = %s", (discord_id,))

	xp_levels = cur.fetchone()
	cur.close()
	conn.close()
	return xp_levels


def set_xp_levels(
	discord_id,
	total_xp,
	level,
	entries=0
	):
	"""
	Set the xp levels of a user.
	"""
	conn = connect()
	cur = conn.cursor()
	cur.execute("UPDATE users SET total_xp = %s, level = %s, giveaway_entries = giveaway_entries + %s WHERE discord_id = %s", (total_xp, level, entries, discord_id, ))
	conn.commit()
	cur.close()
	conn.close()


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
	create_tables()
	members = client.guilds[0].members
	await insert_many_users(list(map(lambda x: x.id, members)))
	await client.close()




if __name__ == '__main__':
	client.run(TOKEN)