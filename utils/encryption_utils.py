import __init__
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

from utils import yaml_utils
from utils import constants as c

def encrypt_string(key, string):
    f = Fernet(key)
    encrypted_string = f.encrypt(string.encode())
    return encrypted_string


def decrypt_string(key, encrypted_string):
    f = Fernet(key)
    decrypted_string = f.decrypt(encrypted_string).decode()
    return decrypted_string


def save_encrypted_string(encrypted_string, encrypted_string_file):
    with open(encrypted_string_file, "wb") as f:
        f.write(encrypted_string)


def load_encrypted_string(file_name):
    with open(file_name, "rb") as f:
        encrypted_string = f.read()
    return encrypted_string



def save_key(key_file):
    password = b"password"
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        iterations=100000,
        salt=salt,
        length=32,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    with open(key_file, "wb") as f:
        f.write(key)
    return key

def load_key():
    key_file = c.root_path + yaml_utils.get_secret_path_from_config()
    with open(key_file, "rb") as f:
        key = f.read()
    return key




# Below is a basic sequence of what you need to do in order to allow Fuse use your git.
# There is a secret.bin file with encrypted GITHUB account that has access to the repo that you listed in the config
# If you want (and I believe you do) to use your own, you need to create your own encrypted password (secret_message) in a file
# to get it one will need to know the key to it. In my case I will just manually add a txt with such password
# Also don't forget to update git username in the config

# WHY such approach? Welp, to allow Fuse to use some dummy created account to use a private repository that that dummy
# account has access to. Why? To have data and configs that are global to all Fuses. The key in txt file is never added
# to git, therefore unless 3rd party gets access to your PC it is ok, right?.. Right?..
# At least I hope I will not mess up and allow Fuse's user to access system file directly..

# When YOU need to generate encrypted password file... use uncommented code below

# So, the sequence
# I suggest you uncomment and do it step by step.
# 1. generate key
# key = save_key("secret.txt")
# 2. Then copy file anywhere in Fuse you want your secret to be (I consider resources is the place)
# 2.5 So once you created and moved secret and updated config, you can
# #     just load it
# key = load_key()
# # 3. prepare actual git pass
# string = "git_pass"
# # 4. encrypt it
# encrypted_string = encrypt_string(key, string)
# # 5. Save the encrypted string file
# save_encrypted_string(encrypted_string, "secret.bin")
# 6. Once again, copy it to resources, I think this one I made mandatory to go there
# 7. to check that it worked, why don't you decrypt it here?
# eencrypted_string = load_encrypted_string("secret.bin")
# ddecrypted_string = decrypt_string(key, eencrypted_string)
# print(ddecrypted_string)
