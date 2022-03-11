import discord
from utils import *
from xp import assign_xp
from db import *
import json

class LinkView(discord.ui.View):
	def __init__(self, url, label, timeout=None):
		super().__init__(timeout=timeout)
		self.url = url
		self.label = label
		self.add_item(
			discord.ui.Button(label=self.label, url=self.url)
		)


class EventButton(discord.ui.Button):
	def __init__(self, event_id, event_name):
		super().__init__(
			label="Attend Event",
			style=discord.enums.ButtonStyle.primary
		)
		self.id = event_id
		self.name = event_name
	async def callback(self, interaction):
		redisClient.rpush(self.id, interaction.user.id)
		await assign_xp(bot, "ATTEND_EVENT", interaction.user.id)
		await interaction.user.send(content="You have successfully signed up to be notified of {}!".format(self.name))

class JobButton(discord.ui.Button):
	def __init__(self, job_id, job_name):
		super().__init__(
			label="Track Application",
			style=discord.enums.ButtonStyle.primary, 
		)
		self.id = job_id
		self.name = job_name
	async def callback(self, interaction):
		await assign_xp(bot, "APPLY", interaction.user.id)
		await apply_to_job(interaction.user.id, self.id)
		await interaction.user.send(content=f"You have successfully tracked the role {self.name}! You can check your other applications using the `/applications` command.")


class CollegeRequestView(discord.ui.View):
	def __init__(self, college_data):
		super().__init__(timeout=None)
		self.college = college_data
	
	@discord.ui.button(label="Approve", style=discord.enums.ButtonStyle.success)
	async def approve(self, button, interaction):
		await create_college_fn(interaction.guild, self.college)
		await interaction.response.edit_message(content="College has been approved.", delete_after=10, view=None, embed=None)
	@discord.ui.button(label="Deny", style=discord.enums.ButtonStyle.danger)
	async def deny(self, button, interaction):
		await interaction.response.edit_message(content="College denied.", delete_after=10, view=None, embed=None)
		await interaction.user.send("Your college request has been denied.")


class TriviaView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=30)

	@discord.ui.button(label="Start",style=discord.ButtonStyle.primary)
	async def callback(self, button, interaction):
		trivia = json.loads(redisClient.get("trivia"))
		question, correct, answers = trivia['question'], trivia['correct'], trivia['answers']
		
		answers.append(correct)
		random.shuffle(answers)
		
		answerView = AnswerView()

		for i, answer in enumerate(answers):
			button = TriviaButton(answer, correct, i)
			answerView.add_item(button)
		
		await interaction.response.edit_message(content=question, view=answerView)
		redisClient.sadd("trivia-players", str(interaction.user.id))
		

class AnswerView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=10)


class TriviaButton(discord.ui.Button):
	def __init__(self, answer, correct, index):
		super().__init__(
            label=answer,
            style=discord.enums.ButtonStyle.secondary,
            custom_id=f'{index} {correct}',
        )


	async def callback(self, interaction):
		correct = self.custom_id.split(" ")[1]
		prize = int(redisClient.get('trivia-prize'))
		if correct == self.label:
			await interaction.response.edit_message(content="That's correct! You've just won ${} coins! Come back tomorrow to play again.".format(prize), view=None)
			set_user_balance(prize, interaction.user.id)
		else:
			await interaction.response.edit_message(content="That's incorrect! The correct answer is {}. You could have won ${} coins. Come back tomorrow to play again.".format(correct, prize), view=None)
		await assign_xp(bot, "TRIVIA", interaction.user.id)
		

