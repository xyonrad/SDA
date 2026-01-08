import getpass
import hashlib

pwd = getpass.getpass("DEV password: ")
print(hashlib.sha256(pwd.encode("utf-8")).hexdigest())

