from tools.file_manager import FileManager

# Case 1: Existing file
print(FileManager.read("notes.txt"))
# Expected: "This is my note."

# Case 2: Non-existent file
try:
    FileManager.read("missing.txt")
except FileNotFoundError as e:
    print("Caught:", e)

# Case 3: Directory path
try:
    FileManager.read("Documents/")
except IsADirectoryError as e:
    print("Caught:", e)
