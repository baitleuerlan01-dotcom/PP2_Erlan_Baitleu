import os

path = "test_folder"

# create directory
os.makedirs(path, exist_ok=True)

# create subdirectories
os.makedirs(path + "/docs", exist_ok=True)
os.makedirs(path + "/images", exist_ok=True)
os.makedirs(path + "/videos", exist_ok=True)

print("Directories created.\n")

# list directories
print("List of directories:")
for item in os.listdir(path):
    if os.path.isdir(os.path.join(path, item)):
        print(item)