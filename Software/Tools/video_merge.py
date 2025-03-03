import os
import glob
import subprocess

"""First of all make sure "ffmpeg-master-latest-win64-lgpl.zip" from 
 https://github.com/BtbN/FFmpeg-Builds/releases is installed on your computer"""

"""By processing this code you will be asked if:
 1. you want to convert MJPEG- files into MP4 in one single folder, merge them and save them 
    in an output folder.
 2. you want to convert MJPEG- files into MP4 in a mainfolder with subfolders, that 
    contain the MJPEG-files.Every MJPEG in the subfolder will be converted, merged and
    saved in the respective subfolder.
 3. you want to merge already existing MP4- files in a single folder.

    you have to preset the path for your folders before starting the code."""


def delete_zero_kb_files(folder, extension="*.mjpeg"):
    """
    Deletes all files with the specified extension and a size of 0 kb, because they somehow break the code.
    """
    files = glob.glob(os.path.join(folder, extension))
    for file in files:
        if os.path.getsize(file) == 0:  # Check if the file is 0 KB
            print(f"Deleting 0 KB file: {os.path.basename(file)}")
            os.remove(file)


def convert_and_merge_mjpeg(input_folder, output_folder, output_file):
    # Path for your ffmpeg.exe- file
    ffmpeg_path = "C:\\Users\\michi\\PycharmProjects\\PythonProject1\\ffmpeg\\ffmpeg-master-latest-win64-gpl\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"  # Adjust the path!

    # Testing if ffmpeg exists
    if not os.path.exists(ffmpeg_path):
        print(f"Error: FFmpeg not found under {ffmpeg_path}")
        return

    # Testing if an output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Finds all MJPEG- files in a directory
    mjpeg_files = sorted(glob.glob(os.path.join(input_folder, "*.mjpeg")))
    if not mjpeg_files:
        print(f"No MJPEG- files found in {os.path.basename(input_folder)}.")
        return

    temp_files = []

    # Converts MJPEG into MP4
    for i, mjpeg_file in enumerate(mjpeg_files):
        temp_mp4 = os.path.join(output_folder, f"temp_{i}.mp4")
        command = [
            ffmpeg_path, "-y", "-i", mjpeg_file, "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", "30",
            temp_mp4
        ]  # In case you're asking: FFmpeg doesn't change the resolution that is already given by the MJPEG- file.
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            temp_files.append(temp_mp4)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {mjpeg_file}: {e}")
            continue

    # Creates a list of the converted files
    list_file = os.path.join(output_folder, "file_list.txt")
    with open(list_file, "w") as f:
        for temp_file in temp_files:
            f.write(f"file '{temp_file}'\n")

    # Merging of the videos
    merged_output = os.path.join(output_folder, output_file)
    merge_command = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c:v", "libx264", "-preset", "slow", "-crf",
        "18", "-r", "30", merged_output
    ]
    try:
        subprocess.run(merge_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Merged video saved as: {os.path.basename(merged_output)}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")

    # Deleting the single mp4- videos
    for temp_file in temp_files:
        os.remove(temp_file)
    os.remove(list_file)


def merge_existing_mp4(input_folder, output_folder, output_file):
    # Path for your ffmpeg.exe- file
    ffmpeg_path = "C:\\Users\\michi\\PycharmProjects\\PythonProject1\\ffmpeg\\ffmpeg-master-latest-win64-gpl\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"  # Adjust the path!

    # Testing if ffmpeg exists
    if not os.path.exists(ffmpeg_path):
        print(f"Error: FFmpeg not found under {ffmpeg_path}")
        return

    # Testing if an output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Finds all MP4- files in a directory
    mp4_files = sorted(glob.glob(os.path.join(input_folder, "*.mp4")))
    if not mp4_files:
        print(f"No MP4- files found in {os.path.basename(input_folder)}.")
        return

    # Creates a list of the MP4 files for FFmpeg
    list_file = os.path.join(output_folder, "file_list.txt")
    with open(list_file, "w") as f:
        for mp4_file in mp4_files:
            f.write(f"file '{mp4_file}'\n")

    # Merging of the videos
    merged_output = os.path.join(output_folder, output_file)
    merge_command = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c:v", "copy", merged_output
    ]
    try:
        subprocess.run(merge_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Merged video saved as: {os.path.basename(merged_output)}")
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")

    # Deleting the temporary file list
    os.remove(list_file)


def process_folder_with_subfolders(main_folder):
    # Process sub- folders in the main folder
    for root, dirs, files in os.walk(main_folder):
        if root == main_folder:  # Skip the main folder itself
            continue
        # Go through all subfolders in the main folder
        print(f"Processing subfolder: {root}")
        output_folder = root  # Saving the video file in the processed sub folder
        folder_name = os.path.basename(root)  # Extracts the name of the sub-folder
        output_file = f"{folder_name}_merged.mp4"  # Naming the video like the sub-folder
        delete_zero_kb_files(root)  # Deletes all the 0 KB files in the sub-folder
        convert_and_merge_mjpeg(root, output_folder, output_file)


def main():
    # Path's for of the directories
    input_folder_single = "C:\\Users\\michi\\Desktop\\clipsmp4"  # Last 2 backslashes are unnecessary
    output_folder_single = "C:\\Users\\michi\\Desktop\\clipsmp4"
    main_folder_with_subfolders = "C:\\Users\\michi\\Desktop\\clips5"

    """Asking the user if he wants to process one single folder with MJPEG- files, one main folder with subfolders,
    or merge existing MP4 files in a folder."""

    print("Type 1, 2, or 3:")
    print("1: Process one folder with MJPEG-files")
    print("2: Process one main folder with subfolders containing MJPEG-files")
    print("3: Merge existing MP4 files in a folder")
    choice = input("Your choice: ")

    if choice == "1":
        # Processes 1 folder with MJPEG files
        print(f"Processing folder: {os.path.basename(input_folder_single)}")
        delete_zero_kb_files(input_folder_single)  # Deletes all the 0 KB files
        video_name = os.path.basename(input_folder_single)
        output_file = f"{video_name}_merged.mp4"  # Name of the output MP4 file
        convert_and_merge_mjpeg(input_folder_single, output_folder_single, output_file)
    elif choice == "2":
        # Processes a folder with subfolders
        print(f"Processing main folder with subfolders: {os.path.basename(main_folder_with_subfolders)}")
        process_folder_with_subfolders(main_folder_with_subfolders)
    elif choice == "3":
        # Merges existing MP4 files in a folder
        print(f"Processing folder: {os.path.basename(input_folder_single)}")
        delete_zero_kb_files(input_folder_single, "*.mp4")  # Deletes all the 0 KB MP4 files
        output_file = "merged.mp4"  # Name of the output MP4 file
        merge_existing_mp4(input_folder_single, output_folder_single, output_file)
    else:
        print("Invalid choice. Type 1, 2, or 3.")


if __name__ == "__main__":
    main()