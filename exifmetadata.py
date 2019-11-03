import piexif

# https://piexif.readthedocs.io/en/latest/

# this function writes exif_tag_content for rating 0-5 stars
def write_exif_tag_rating(filename, exif_tag_content):
    if not(isinstance(exif_tag_content, int) or exif_tag_content is None):
        raise ValueError("either int or None must be provided")
    if isinstance(exif_tag_content, int):
        if exif_tag_content < 0 or exif_tag_content > 5:
            raise ValueError("value must be in range from 0 to 5")
    exif_dict = piexif.load(filename)
    for ifd_name in exif_dict:
        if (ifd_name=="0th"):
            # explicitly remove the dict entry if None
            if exif_tag_content is not None:
                # 0x4746 	18246 	Image 	Exif.Image.Rating 	Short 	Rating tag used by Windows scale to ***** stars
                exif_dict[ifd_name][18246] = exif_tag_content
            else:
                if 18246 in exif_dict[ifd_name]:
                    del exif_dict[ifd_name][18246]

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filename)

# this function reades exif_tag_content rating 0-5 stars
def read_exif_tag_rating(filename):
    exif_dict = piexif.load(filename)
    for ifd_name in exif_dict:
        try:
            if (ifd_name=="0th"):
                value = exif_dict[ifd_name][18246]
        except KeyError:
            # if key not present we return 0
            return None
    return value
