import sys
import os
import time
import subprocess
import zipfile
from hashlib import sha256
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES

BLOCK_SIZE = AES.block_size
secret_message = "Theyll never guess that minecraft was the enemy all along. And the treasure? The diamonds we mined along the way? Certainly not!"
KEY = sha256(secret_message.encode()).digest()
def decrypt_file_with_progress(input_path, output_path, key):
    with open(input_path, 'rb') as fin:
        iv = fin.read(BLOCK_SIZE)
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        data = fin.read()

    decrypted = unpad(cipher.decrypt(data), BLOCK_SIZE)

    with open(output_path, 'wb') as f:
        f.write(decrypted)

    print(f"✅ Decrypted archive → {output_path}")

def extract_zip(zip_path, output_folder):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output_folder)
    print(f"📂 Extracted to {output_folder}")
    os.remove(zip_path)

def self_delete():
    exe = sys.argv[0]
    if exe.endswith('.exe'):
        bat = f"""
        @echo off
        timeout /t 2 > NUL
        del "{exe}"
        """
        bat_path = "cleanup.bat"
        with open(bat_path, 'w') as f:
            f.write(bat)
        subprocess.Popen([bat_path], shell=True)
        print("💣 This program will now self-destruct...")
        time.sleep(1)

def decrypt_and_extract(enc_file, output_folder):
    temp_zip = "temp_decrypted_maze.zip"
    decrypt_file_with_progress(enc_file, temp_zip, KEY)
    extract_zip(temp_zip, output_folder)
    # self_delete()

if __name__ == "__main__":
    decrypt_and_extract("Haha.enc", "Your Files")