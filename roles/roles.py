"""
	Roles and their required levels
"""

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
'MEE6'
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
	for role, level_required in ROLE_TO_LEVEL.items():
		if level >= level_required:
			return role
	return "Drop Out"


def get_role_to_salary(role:str):
	"""
	Get the salary for a given role
	"""
	return ROLE_TO_SALARY[role]

