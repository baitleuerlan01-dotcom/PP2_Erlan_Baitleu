import shutil
import os

source = "source_folder/file.txt"
destination = "destination_folder/file.txt"

# create folders if not exist
os.makedirs("source_folder", exist_ok=True)
os.makedirs("destination_folder", exist_ok=True)

# move file
if os.path.exists(source):
    shutil.move(source, destination)
    print("File moved successfully")
else:
    print("File does not exist")
    