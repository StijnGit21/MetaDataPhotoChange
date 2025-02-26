import os
from PIL import Image
import piexif
from datetime import datetime

# --------------- Constants ---------------
FOLDER_PATH = r"C:\Users\stijn\Downloads"  # Folder containing the photos
NEW_DATE_STR = "2021-12-27 12:00:00"  # New date in 'YYYY-MM-DD HH:MM:SS' format

# Set to True if you want to update the GPS location
UPDATE_LOCATION = False
LATITUDE = 51.4364687
LONGITUDE = 5.4844615
# ------------------------------------------

# Function to convert decimal coordinates to EXIF GPS format
def decimal_to_dms(decimal):
    degrees = int(decimal)
    minutes = int((abs(decimal) - abs(degrees)) * 60)
    seconds = (abs(decimal) - abs(degrees) - minutes / 60) * 3600
    return [(abs(degrees), 1), (minutes, 1), (int(seconds * 100), 100)]

# Function to set GPS coordinates in EXIF data
def set_gps_location(exif_dict, latitude, longitude):
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: decimal_to_dms(latitude),
        piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: decimal_to_dms(longitude),
    }
    exif_dict['GPS'] = gps_ifd

# Function to create a new EXIF dict with date and optional GPS
def create_exif_dict(new_date, latitude=None, longitude=None):
    exif_dict = {
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: new_date.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8'),
            piexif.ExifIFD.DateTimeDigitized: new_date.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8'),
        },
        'GPS': {}
    }
    
    if latitude is not None and longitude is not None:
        set_gps_location(exif_dict, latitude, longitude)
    
    return exif_dict

# Function to modify the date and location in the EXIF data of an image
def modify_image_metadata(image_path, new_date, latitude=None, longitude=None):
    try:
        # Open the image
        img = Image.open(image_path)

        # Check if EXIF data exists
        if 'exif' not in img.info:
            print(f"No EXIF data found for {image_path}. Creating new EXIF data.")
            exif_dict = create_exif_dict(new_date, latitude, longitude)
            exif_bytes = piexif.dump(exif_dict)

            # Save the image with new EXIF data
            img.save(image_path, exif=exif_bytes)
            print(f"Added new metadata for {image_path}")
        else:
            # Get the exif data
            exif_dict = piexif.load(img.info['exif'])

            # Modify the existing EXIF data
            formatted_date = new_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = formatted_date.encode('utf-8')
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = formatted_date.encode('utf-8')

            # Set GPS location if latitude and longitude are provided
            if latitude is not None and longitude is not None:
                set_gps_location(exif_dict, latitude, longitude)

            # Create the new EXIF data and save it back to the image
            exif_bytes = piexif.dump(exif_dict)
            img.save(image_path, exif=exif_bytes)
            print(f"Updated metadata for {image_path}")
    except Exception as e:
        print(f"Error updating {image_path}: {e}")

# Function to process all images in a folder
def update_all_images_in_folder(folder_path, new_date, latitude=None, longitude=None):
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            print(f"Processing {image_path}")
            modify_image_metadata(image_path, new_date, latitude, longitude)

if __name__ == "__main__":
    try:
        # Convert the date string to a datetime object
        new_date = datetime.strptime(NEW_DATE_STR, "%Y-%m-%d %H:%M:%S")

        # Call the function to update the date and location in all images
        if UPDATE_LOCATION:
            update_all_images_in_folder(FOLDER_PATH, new_date, LATITUDE, LONGITUDE)
        else:
            update_all_images_in_folder(FOLDER_PATH, new_date)

        print("Metadata update completed.")
    except ValueError as e:
        print(f"Error: {e}")
