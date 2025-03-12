#duplicate music files finder
#finds duplicate music files in a folder based on metadata and audio hash   


import os
import hashlib
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from pydub import AudioSegment

def get_metadata(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".mp3":
            audio = EasyID3(file_path)
        elif ext == ".flac":
            audio = FLAC(file_path)
        elif ext == ".m4a" or ext == ".mp4":
            audio = MP4(file_path)
        else:
            return None
        
        artist = audio.get("artist", ["Unknown"])[0]
        title = audio.get("title", ["Unknown"])[0]
        album = audio.get("album", ["Unknown"])[0]
        return artist, title, album
    except Exception:
        return None

def get_audio_hash(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        raw_data = audio.raw_data
        return hashlib.md5(raw_data).hexdigest()
    except Exception:
        return None

def find_duplicates(music_folder):
    metadata_map = {}
    hash_map = {}
    
    for root, _, files in os.walk(music_folder):
        for file in files:
            file_path = os.path.join(root, file)
            metadata = get_metadata(file_path)
            
            if metadata:
                key = (metadata[0].lower(), metadata[1].lower())  # (artist, title)
                if key in metadata_map:
                    metadata_map[key].append(file_path)
                else:
                    metadata_map[key] = [file_path]
            
            file_hash = get_audio_hash(file_path)
            if file_hash:
                if file_hash in hash_map:
                    hash_map[file_hash].append(file_path)
                else:
                    hash_map[file_hash] = [file_path]
    
    duplicates = {k: v for k, v in metadata_map.items() if len(v) > 1}
    hash_duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}
    
    return duplicates, hash_duplicates

def print_duplicates(duplicates, description):
    print(f"\n=== {description} ===")
    for key, files in duplicates.items():
        print(f"\nDuplicate: {key}")
        for f in files:
            print(f"  - {f}")

if __name__ == "__main__":
    folder_path = input("Enter the path to your music folder: ")
    metadata_duplicates, hash_duplicates = find_duplicates(folder_path)
    
    print_duplicates(metadata_duplicates, "Metadata-Based Duplicates")
    print_duplicates(hash_duplicates, "Audio Hash-Based Duplicates")
