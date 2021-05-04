# Analog Metadata
This python script allows you to add metadata to your pictures that you've taken
with your beloved analog camera. Of course, as the neat freak that you are, you
want the camera make and model as well as the film stock and film speed in the
metadata of those pictures. Not to mention, having the pictures ordered in the
order that you took them. This script does all of that! (More or **less**)

# Prerequisites
You have to have python3 installed and the python package
[piexif](https://pypi.org/project/piexif/).

# Usage

Your project should have a structure like this
```
roll_folder_1
    | pictures
    | roll.json
roll_folder_2
    | pictures
    | roll.json
roll_folder_3
    | pictures
    | roll.json
analog_metadata.py
```
Basically, where each roll have it's own folder containing all the pictures form
that roll.

The `roll.json` file should contain the information about that particular roll.
```json
{
    "camera_make": "Konica",    // The camera make
    "camera_model": "FC-1",     // The camera model
    "film_speed": "200",        // The film speed
    "film_stock": "Kodak Gold", // The film stock
    "film_format": "35",        // The format of the film
    "start_date": "01.07.2019", // The date you took the first picture
    "end_date": "05.08.2019",   // The date you took the last picture
    "date_developed": "31.08.2019" // The date the roll got developed
}
```

The script will use the end date as the timestamp for each of the photos.

[Here](roll.json) you have a template of the roll.json file. Just copy it to the folder with the structure as mentioned above.

You run the script by `python3 analog-metadata.py` or `./analog_metadata.py`
depending on your system.

The script will then rename the folder to `{start date}-{end date}` and also
rename all the pictures according to `{end date}-analog-{sequence}`. It's
important that you leave `roll.json` in the folder as it tells the script that
the pictures within that folder has been processed.

# Remarks
* The script only process `jpeg`, `jpg` and `png` files
