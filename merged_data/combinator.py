from ImageCropper.extract import crop_folder_bg
from ImageFuser import overlay
from PythonUtils.file import unique_name
from PythonUtils.folder import get_abspath
from bg_data.bg_grabber import downloadGoogleImages
from Specifiations.config import configuration
import os

import logging
logger = logging.getLogger("CombinationModule")


def overlay_marker(marker_folder, bg_folder, combined_folder):
    """
    Combine markers and folders together to form the training data set.
    :param marker_folder: folders where markers images are replaced
    :param bg_folder: folders where patterns images are replaced
    :return:
    """
    new_folder_name = os.path.join(combined_folder, unique_name())
    os.makedirs(new_folder_name)

    for marker in marker_folder:
        for bg in bg_folder:
            new_file_name = os.path.join(new_folder_name, unique_name())
            overlay.randomly(bg, marker, new_file_name)
            logger.info("Generated " + new_file_name)

def download(config):
    """
    Download the entire list of images based on the parameters defined.
    :param config: the configuration for pathing.
    :return:
    """

    download_specs = \
        {"keywords": "black,black%20color,Office,patterns,logos,home,design,man-made",
         "limit": 5,
         "chromedriver": r"C:\bin\chromedriver.exe",
         "size": ">6MP",
         "format": "jpg",
         "print_urls": True}   # creating list of download_specs

    bg_list = downloadGoogleImages(download_specs, config.bg)




def prepare_training_data():
    """
    Download, crop, overlay, augment the markers on a series of images.
    :returns: 1. Augmented folder with marker, 2. Control folder without marker.
    """
    from ImageFuser.overlay import subfolder as overlay_subfolder
    from overlay_data.augmentation_sequence import MarkerAug, CombinedAug
    from overlay_data.augmentation import subfolder as augment_subfolder
    from ImageCropper.extract import crop_folder_bg

    # Download bg.
    root_folder = get_abspath(os.path.realpath(__file__), 2)
    paths = configuration(root_folder)

    download_files  = True
    augment_marker  = True
    augment_bg      = True
    augment_control = True

    # Crop bgs
    crop_folder = r"E:\Gitlab\MarkerTrainer\bg_data\cropped\2018-09-20T02_12_12.525422_500x500crop_downloads"
    control_folder = r"E:\Gitlab\MarkerTrainer\bg_data\cropped\2018-09-20T02_12_29.954455_500x500crop_downloads"

    if download_files:
        download(paths)
        crop_folder = crop_folder_bg(paths.download, paths.cropped, 500, 500)  # with over added soon
        control_folder = crop_folder_bg(paths.download, paths.cropped, 500, 500)  # server as control group

    # Augmented Marker
    aug_markers = r"E:\Gitlab\MarkerTrainer\augmented_data\Marker\2018-09-22T12_40_28.641438500px"
    if augment_marker:
        aug_markers = augment_subfolder(paths.overlay, paths.aug_overlay, MarkerAug(), 1, "500px")


    # Augmented bg
    aug_bg = r"E:\Gitlab\MarkerTrainer\augmented_data\Bg\2018-09-22T13_01_52.483939500px"
    if augment_bg:
        aug_bg = augment_subfolder(crop_folder, paths.aug_bg, MarkerAug(), 1, "500px")

    # Augmented bg used as control
    aug_bg_control = r"E:\Gitlab\MarkerTrainer\augmented_data\Bg\2018-09-22T12_41_09.122966500px"
    if augment_control:
        aug_bg_control = augment_subfolder(control_folder, paths.aug_bg, MarkerAug(), 1, "500px")

    # Overlay PRIME on cropped BG.
    overlaid_cropped_folder = overlay_subfolder(aug_markers, aug_bg, paths.combined)

    # Augment the overlaid images.
    augmented_folder = augment_subfolder(overlaid_cropped_folder, paths.aug_merged, CombinedAug(), 5, "500px")
    
    return augmented_folder, aug_bg_control

if __name__ == "__main__":
    #crop_bg(500, 500)
    #overlay_marker("C:\GitHub\MarkerTrainer\overlay_data\Prime", "C:\GitHub\MarkerTrainer\overlay_data\Background\cropped","C:\GitHub\MarkerTrainer\overlay_data\combined")
    prepare_training_data()
