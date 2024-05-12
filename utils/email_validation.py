

def email_validate(email) -> bool:
    if email.find("+") != -1:
        return False
    if email.endswith("@googlemail.com"):
        return False
    if email.count(".") > 1:
        return False
    return True