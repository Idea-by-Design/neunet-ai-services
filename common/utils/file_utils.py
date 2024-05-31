import os

def get_file_extension(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower()
