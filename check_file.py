import os

# Get the path to the assets folder
base_path = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(base_path, 'assets')

print("------------------------------------------------")
print(f"CHECKING FOLDER: {assets_path}")
print("------------------------------------------------")

try:
    files = os.listdir(assets_path)
    print("FILES FOUND:")
    for f in files:
        print(f" - {f}")
except FileNotFoundError:
    print("ERROR: The 'assets' folder does not exist!")