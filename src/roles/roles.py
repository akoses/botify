"""
	Roles and their required levels
"""
import os
ROLE_TO_LEVEL = {
	"Chancellor": 100,
	"President":90,
	"Vice President":80,
	"Dean":70,
	"Department Head": 60,
	"Professor":50,
	"Post Doc":40,
	"Teaching Assistant":30,
	"Graduate":20,
	"Upper Year Student":10,
	"Lower Year Student":1,
	"Drop Out":0
}

ROLE_TO_ID = {

	"Chancellor": 950211602169364480,
	"President": 950211602865602671,
	"Vice President": 950211603721248779,
	"Dean": 950211604698525776,
	"Department Head": 950211605487038504,
	"Professor": 950211606359474217,
	"Post Doc": 950211607760355378,
	"Teaching Assistant": 950211608553066527,
	"Graduate": 950211609656184863,
	"Upper Year Student": 950211610549575701,
	"Lower Year Student": 950211611568799764,
}

LEVEL_TO_ROLE = {
	100: "Chancellor",
	90: "President",
	80: "Vice President",
	70: "Dean",
	60: "Department Head",
	50: "Professor",
	40: "Post Doc",
	30: "Teaching Assistant",
	20: "Graduate",
	10: "Upper Year Student",
	1: "Lower Year Student",
	0: "Drop Out"
}

ROLE_TO_COLOUR ={
	"Chancellor": (168,	210, 251),
	"President":(255, 170, 153),
	"Vice President":(102, 103, 171),
	"Dean":(255,226,116),
	"Department Head":(8,141,165),
	"Professor":(10,117,173),
	"Post Doc":(255,64,64),
	"Teaching Assistant":(199,103,176),
	"Graduate":(162,190,255),
	"Upper Year Student":(102, 103,171),
	"Lower Year Student":(182,215,168),
	"Drop Out":(0, 0, 0)
}


ROLE_TO_ENTRIES = {
	"Chancellor": 60,
	"President":55,
	"Vice President":50,
	"Dean":45,
	"Department Head": 40,
	"Professor":35,
	"Post Doc":30,
	"Teaching Assistant":25,
	"Graduate":20,
	"Upper Year Student":15,
	"Lower Year Student":10,
}


ROLE_TO_SALARY = {
	"Chancellor": 1024000,
	"President": 512000,
	"Vice President": 256000,
	"Dean": 128000,
	"Department Head": 64000,
	"Professor": 32000,
	"Post Doc": 16000,
	"Teaching Assistant": 8000,
	"Graduate": 4000,
	"Upper Year Student": 2000,
	"Lower Year Student": 1000,
}

IGNORE_ROLES = {
'@everyone',
'Botify',
'Drop Out',
'Lower Year Student',
'Upper Year Student',
'Graduate',
'Teaching Assistant',
'Post Doc',
'Professor',
'Department Head',
'Dean',
'Vice President',
'President',
'Chancellor',
'Simple Poll',
'new role',
'Admin',
'carl-bot',
'muted',
'MEE6',
"Chegg",
"Job Searcher",
"DISBOARD.org",
}


def salary_to_weekly(salary:int):
	"""
	Get the weekly salary for a given salary
	"""
	return salary/52


def get_level_to_role(level:int):
	"""
	Get the role for a given level
	"""
	return LEVEL_TO_ROLE[(level // 10) * 10]


def get_role_to_salary(role:str):
	"""
	Get the salary for a given role
	"""
	return ROLE_TO_SALARY[role]


def role_or_higher(role:str):
	"""
	Get the array of ids for a role higher than the role specified.
	"""
	roles =  [id for role_l, id in ROLE_TO_ID.items() if ROLE_TO_LEVEL[role_l] >= ROLE_TO_LEVEL[role]]
	roles.append(int(os.getenv('ADMIN_ROLE')))
	roles.append(953367475964223569)
	return roles

if __name__ == "__main__":
	print(role_or_higher("Upper Year Student"))