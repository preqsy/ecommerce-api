import re

def validate_password(password) -> bool:
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d|\W).{6,}$"
    if re.match(pattern, password):
        return True
    else:
        return False
    


