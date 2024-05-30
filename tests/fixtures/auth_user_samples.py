from models.auth_user import AuthUser


def sample_auth_user_create():
    return {
        AuthUser.EMAIL: "obbyprecious@gmail.com",
        AuthUser.PASSWORD: "2Strong",
        AuthUser.DEFAULT_ROLE: "customer",
    }
