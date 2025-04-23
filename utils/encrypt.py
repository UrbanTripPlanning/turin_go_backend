import hashlib


salt = "turin_g_o+"


def md5_encrypt(text: str) -> str:
    md5 = hashlib.md5()
    text += salt
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()
