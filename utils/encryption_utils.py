import __init__
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

from utils import yaml_utils


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


def save_key(key_file, key_phrase):
    # password = b"password"
    password = key_phrase.encode('utf-8')
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
    key_file = yaml_utils.get_secret_txt_path_from_config()
    with open(key_file, "rb") as f:
        key = f.read()
    return key


def get_secured_token():
    key = load_key()
    eencrypted_string = load_encrypted_string(yaml_utils.get_secret_bin_path_from_config())
    return decrypt_string(key, eencrypted_string)

# Below is a basic sequence of what you need to do in order to allow Fuse use your git.
# There is a secret.bin file with encrypted GITHUB OAuth account token that has access to the repo that you listed in the config
# You should add Fuse's git account as a collaborator, also be aware that in case you are creating new account for this (as I would suggest)
# Then you need to allow new account to do modifications (apparently by default it is off)

# If you want (and I believe you do) to use your own, you need to create your own pair of .bin and .txt files.
# Create new github account. Add it as a collaborator for the repo(s) you are interested in. Allow new accounts to make
# modifications in that repo or globally (yes, this is a thing). Then generate OAuth token and temporarily save have it ready

# WHY such approach? Welp, to allow Fuse to use some dummy created account to use a repository that that dummy
# account has access to. Why? To have packages, data and configs that are global to all Fuses.
# The key in txt file is never added to git, therefore unless 3rd party gets access to your PC it is ok, right?.. Right?..
# At least I hope I will not mess up and allow Fuse's user to access system file directly..

# When YOU need to generate encrypted password file... use uncommented code below

# So, the sequence
# I suggest you uncomment and do it step by step or so when it makes sense.
# 1. generate key
# key = save_key("secret.txt", "password")
# Notes here: although password can be the same, derived key is always different
# 2. Then copy file anywhere in Fuse you want your secret to be (I consider resources is the place)
# Notes: location of both secrets (.bin and .txt) can be inside Fuse or defined by absolute path in config
# 2.5 So once you created and moved secret and updated config, you can
# ===> just load it from config-defined place
# key = load_key()
# # 3. prepare actual git pass (or auth token)
# string = "password/token"
# # 4. encrypt it
# encrypted_string = encrypt_string(key, string)
# # 5. Save the encrypted string file
# save_encrypted_string(encrypted_string, "secret.bin")
# 6. Once again, copy it to resources, I think this one I made mandatory to go there
# 7. to check that it worked, why don't you decrypt it here?
# eencrypted_string = load_encrypted_string("secret.bin")
# ddecrypted_string = decrypt_string(key, eencrypted_string)
# print(ddecrypted_string)

# Once again, I repeat. .bin file is kinda under 2 layers of encryption, it is relatively safe to upload it to repo
# .txt key must be local. Once again it is different every time no matter what password you used. Therefore if you lost
# it once, you can't just remake the key. One time generated thing, by design

# Note: if you think you fucked up and the token is not that secure, just revoke it and try with new one.
# Git's token can be revoked from settings of account that owns the token
