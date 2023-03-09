import os
import shutil
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

# Ask the user to select the source folder
source_folder_path = filedialog.askdirectory(title="Select source folder")

# Ask the user to select the destination folder
destination_folder_path = filedialog.askdirectory(title="Select destination folder")

# Iterate over all files in the source folder
for filename in os.listdir(source_folder_path):
    # Construct the full file paths
    source_file_path = os.path.join(source_folder_path, filename)
    destination_file_path = os.path.join(destination_folder_path, filename)
    # Check if the file is a regular file (i.e. not a directory)
    if os.path.isfile(source_file_path):
        # Copy the file to the destination folder
        shutil.copy(source_file_path, destination_file_path)




# Define a function to handle the button click event
file_path = st.file_uploader("Upload a file")

# Display the folder path and name of the selected file
if file_path is not None:
    file_name = file_path.name
    file_abs_path = os.path.abspath(file_path.name)
    folder_path = os.path.dirname(file_abs_path)
    st.write("Folder path:", folder_path)
    st.write("File name:", file_name)

source_folder = "C:/Users/chiwundurad/Desktop/Files/Apps/Python/db_backups"
dest_folder = folder_path

# Get the list of files in the source folder
files = os.listdir(source_folder)

# Download each file to the destination folder
for file in files:
    file_path = os.path.join(source_folder, file)
    dest_path = os.path.join(dest_folder, file)
    # shutil.copyfile(file_path, dest_path)

# Display a success message
st.write("All files downloaded successfully!")