
def days_to_seconds(days):
	return days * 86400

def find_invite_by_code(invite_list, code):
    for inv in invite_list:     
        if inv.code == code:      
            return inv
