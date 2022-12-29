#!/bin/python3
import json
import os
import re
import datetime
import piexif

print("Run this program in order to fix the timestamps after they have been scanned by OdenLab")

# Walk through all directories and fetch all photos
last_dir = None
processed_photos = 0

for root, directories, files in os.walk(os.getcwd()):
    print(f"Checking {root}")

    # If the folder contains a "roll.json" file then it should be processed
    roll_path = os.path.join(root, "roll.json")
    if not os.path.exists(roll_path):
        # Jump over this folder of the json roll information file does not exist
        continue

    try:
        with open(roll_path, "r") as roll_f:
            roll_information = json.load(roll_f)
    except Exception as e:
        print(f"Could not open the json file in folder {roll_path}")
        print(e)
        continue
    
    # Check if the roll is already processed
    if roll_information.get("date_processed"):
        print(f'Old roll (already processed) {roll_information["start_date"]} - {roll_information["end_date"]}')
        continue

    # New roll equals new timestamps
    print(f'New roll: {roll_information["start_date"]} - {roll_information["end_date"]} on path: "{roll_path}"')

    roll_number = roll_information["roll_no"]
    
    try:
        start_date = datetime.datetime.strptime(roll_information["start_date"], "%d.%m.%Y")
        end_date = datetime.datetime.strptime(roll_information["end_date"], "%d.%m.%Y")
    except:
        print(f"An error occured processing the timestamps for roll number {roll_number} ({roll_path})")
    timestamp = end_date

    # Check if pictures are in reversed order
    try:
        reverse_order_tmp = roll_information["reverse_order"]
        reverse_order = True if reverse_order_tmp == "true" else False
    except:
        reverse_order = False

    # Sort (and maybe reverse) the files before processing
    files.sort()
    if reverse_order:
        files.reverse()

    photo_no = 0
    for file_name in files:
        if re.match(r".*((\.jpg)|(\.jpeg)|(\.JPG)|(\.JPEG))", file_name):
            # Process photo
            print(f"Processing: {file_name}")
            file_type = file_name[file_name.index(".")+1:].lower()
            photo_path = os.path.join(root, file_name)

            # Set new modified time
            exif_dict = piexif.load(photo_path)

            if roll_information:
                # Add roll information too if available
                if roll_information["camera_make"]:
                    exif_dict["0th"][piexif.ImageIFD.Make] = roll_information["camera_make"]
                if roll_information["camera_model"]:
                    exif_dict["0th"][piexif.ImageIFD.Model] = roll_information["camera_model"]
                if roll_information["film_speed"]:
                    exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = int(roll_information["film_speed"])

                exif_dict["Exif"][piexif.ExifIFD.UserComment] = \
                    f'ASCII0x0{roll_information["film_stock"]} {roll_information["film_speed"]} {roll_information["film_format"]}mm'\
                    .encode()

            date_str = timestamp.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, photo_path)

            # Rename file
            new_photo_path = os.path.join(root, end_date.strftime(
                f'%Y%m%d-analog-{str(photo_no).zfill(3)}.{file_type}'
            ))
            os.rename(photo_path, new_photo_path)
            
            # Advance things
            photo_no += 1
            processed_photos += 1
            timestamp = timestamp + datetime.timedelta(minutes=1)

    # Done with roll
    print(f"Processed {photo_no} number of photos in this folder")
    roll_information["date_processed"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # Update roll information
    with open(roll_path, "w") as roll_f:
        json.dump(roll_information, roll_f, ensure_ascii=False, indent=4)

    # Rename folder
    os.rename(
        root, 
        f'{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}'
    )

print(f"All done, processed {processed_photos} photos")
