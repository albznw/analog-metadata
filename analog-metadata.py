#!/bin/python3
import json
import os
import re
import datetime
import time
import piexif

print("Run this program in order to fix the timestamps after they have been scanned by OdenLab")

# Walk through all directories and fetch all photos
last_dir = None
processed_photos = 0

for root, directories, files in os.walk(os.getcwd()):
    print(f"Checking {root}")

    # If the folder contains a "roll.json" file then it should be processed
    roll_path = os.path.join(root, "roll.json")
    try:
        with open(roll_path, "r") as roll_f:
            roll_information = json.load(roll_f)
    except:
        # Jump over this folder
        continue

    # Check if the roll is already processed
    if roll_information.get("date_processed"):
        print(f'Old roll {roll_information["start_date"]} - {roll_information["end_date"]}')
        continue

    # New roll equals new timestamps
    print(f'New roll: {roll_information["start_date"]} - {roll_information["end_date"]}')
    start_date = datetime.datetime.strptime(roll_information["start_date"], "%d.%m.%Y")
    end_date = datetime.datetime.strptime(roll_information["end_date"], "%d.%m.%Y")
    timestamp = end_date

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
                exif_dict["0th"][piexif.ImageIFD.Make] = roll_information["camera_make"]
                exif_dict["0th"][piexif.ImageIFD.Model] = roll_information["camera_model"]
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
        json.dump(roll_information, roll_f)

    # Rename folder
    os.rename(
        root, 
        f'{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}'
    )

print(f"All done, processed {processed_photos} photos")
