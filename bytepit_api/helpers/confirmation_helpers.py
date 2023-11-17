from bytepit_api.database.queries import set_verified_user, get_user_by_verification_token


def activate_user(verification_token: str):
    user = get_user_by_verification_token(verification_token)
    if not user:
        return False
    if user.is_verified:
        return False
    return set_verified_user(user.id)
