"""
Local Texture Search is a command line Python 3 program which takes an image as input and looks for similar images. The
program has two modes: the first looks for an identical, higher resolution version of the input image, and the second
looks for images which are visually similar to the input.
"""

# Imports
import cv2
import glob
import io
import multiprocessing
import os
import sys
import time
import numpy as np
from PIL import Image, UnidentifiedImageError


def mse(image_a, image_b):
    """ Calculate the mean squared error between images"""
    # Code source: https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def image_compare(filename_list=None, compare_file="", log_filename="", verbose=False, compare=False,
                  highlowres=False):
    """
    Compare images and log if similar. Uses MSE for finding identical images with different resolutions
    and SIFT to find structurally similar images via keypoint matching.
    """

    # Resize and load key image into memory
    try:
        with Image.open(compare_file) as img:
            temp_img = img.resize((1024, 1024))
            buf = io.BytesIO()
            temp_img.save(buf, format="PNG")
            key_buf = buf.getvalue()
            key_img = cv2.imdecode(np.frombuffer(key_buf, np.uint8), cv2.IMREAD_UNCHANGED)
    # Ensure key file is an image
    except UnidentifiedImageError:
        print("Error: invalid compare_file, ensure file is an image")
        exit(1)
    except PermissionError:
        print("Error: insufficient permissions to read compare_file, ensure your account has access to compare_file")
        exit(1)

    # Convert to black and white
    key_img = cv2.cvtColor(key_img, cv2.COLOR_BGR2GRAY)

    # Run time and file processing count
    time_start = time.perf_counter()
    processed = 0

    # Perform image comparisons
    for file_name in filename_list:
        processed += 1
        # Load comparison image into memory
        try:
            with Image.open(file_name) as img:
                temp_img = img.resize((1024, 1024))
                buf = io.BytesIO()
                temp_img.save(buf, format="PNG")
                tex_buf = buf.getvalue()
                tex_img = np.frombuffer(tex_buf, np.uint8)
        # Catch errors from bad file names
        except FileNotFoundError:
            continue
        # Skip file if it is not an image
        except UnidentifiedImageError:
            continue
        # Skip file if program does not have permission to read
        except PermissionError:
            continue
        # Convert numpy array into cv2 image
        tex_img = cv2.imdecode(tex_img, cv2.IMREAD_UNCHANGED)
        # Convert image to grayscale
        tex_img = cv2.cvtColor(tex_img, cv2.COLOR_BGR2GRAY)

        # Use SIFT in compare mode
        if compare:
            # Original code by Aishwarya Singh, article available at:
            # https://www.analyticsvidhya.com/blog/2019/10/detailed-guide-powerful-sift-technique-image-matching-python/

            # Create instance of SIFT class for image processing
            sift = cv2.SIFT_create()

            # Calculate descriptors for image comparison
            descriptors_1 = sift.detectAndCompute(key_img, None)[1]
            descriptors_2 = sift.detectAndCompute(tex_img, None)[1]

            # Create instance of Brute-force descriptor matcher
            bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
            try:
                # Find matches between image descriptors
                matches = bf.match(descriptors_1, descriptors_2)
                # Log name of image if it is similar enough to key image
                if len(matches) > 400:
                    with open(log_filename, "a") as f:
                        if verbose:
                            print(log_filename)
                        f.write(file_name + " " + " SIFT Matches:" + str(len(matches)) + "\n")
                if verbose:
                    print(f"SIFT: {len(matches)}")
            # Pass if matches cannot be calculated
            except cv2.error:
                pass

        # Use MSE in highlowres mode
        elif highlowres:
            # Calculate MSE between images
            comparison_mse = mse(key_img, tex_img)
            if verbose:
                print(f"MSE: {comparison_mse}")

            # Log filename if it is similar enough to key image
            if comparison_mse < 1000:
                with open(log_filename, "a") as f:
                    if verbose:
                        print(log_filename)
                    f.write(file_name + " " + str(comparison_mse) + " \n")

    # Performance and logging
    time_stop = time.perf_counter()
    if verbose:
        print(f"Ran in {time_stop - time_start:0.4f} seconds")
        print(f"Processed {processed} files")


def multithreading_compare(filename_list, argument_dict, use_threading):
    """
    Split list of files into number of parts equal to thread count,
    have each threaded process handle a portion of the files.
    """

    # Divide filename list length
    mod = len(filename_list) % use_threading
    share_of_files = round((len(filename_list) - mod) / use_threading)

    filename_list_chunks = []
    # Split filename list into portions for each process to handle
    for i in range(1, use_threading + 1):
        index_1 = (i - 1) * share_of_files
        # Assign share_of_files long piece of filename_list to all but last process
        if i < use_threading:
            index_2 = i * share_of_files
            filename_list_chunks.append(filename_list[index_1:index_2])
        # Assign rest of filename_list to last process
        else:
            filename_list_chunks.append(filename_list[index_1:])

    # Create threads, assign each a portion of the files to handle, start threads
    # As a safety precaution, threads are not created iteratively.
    if use_threading >= 2:
        argument_dict["filename_list"] = filename_list_chunks[0]
        process_1 = multiprocessing.Process(
            target=image_compare, kwargs=argument_dict)
        process_1.start()

        argument_dict["filename_list"] = filename_list_chunks[1]
        process_2 = multiprocessing.Process(
            target=image_compare, kwargs=argument_dict)
        process_2.start()

    if use_threading >= 3:
        argument_dict["filename_list"] = filename_list_chunks[2]
        process_3 = multiprocessing.Process(
            target=image_compare, kwargs=argument_dict)
        process_3.start()

    if use_threading >= 4:
        argument_dict["filename_list"] = filename_list_chunks[3]
        process_4 = multiprocessing.Process(
            target=image_compare, kwargs=argument_dict)
        process_4.start()


def main():
    # Command line argument Handling:

    # File to compare textures to
    argument_dict = {"compare_file": f"{os.getcwd()}/{sys.argv[1]}"}
    if not os.path.isfile(argument_dict["compare_file"]):
        print("Error: compare file not found, check if file exists or see README.md for syntax")
        exit(1)

    # Get and format path to texture
    texture_path = sys.argv[2].replace("\\", "/")
    if not (texture_path[:-1] == "/"):
        texture_path += "/"
    if not os.path.isdir(texture_path):
        print("Error: path_to_textures is not a valid directory, see README.md for formatting examples")
        exit(1)

    # Handle optional arguments and options
    argument_dict["verbose"] = False
    use_threading = 0
    for parameter in sys.argv[2:]:
        # Check for threading argument, handle potential user inputs
        if "threading=" in parameter:
            use_threading = parameter[len("threading="):]
            try:
                use_threading = int(use_threading)
            except ValueError:
                print("Error: thread count could not be converted to a number, enter a number for thread count or"
                      "see README.md for usage.")
                exit(1)
            if use_threading not in range(2, 5):
                print("Error: thread count must be between 2 and 4")
                exit(1)
        # Check for verbose mode option
        if parameter == "-v":
            argument_dict["verbose"] = True
        # Check for compare mode argument
        if parameter == "compare":
            argument_dict["compare"] = True
        # Check for highlowres mode argument
        if parameter == "highlowres":
            argument_dict["highlowres"] = True

    # Disable highlowres mode if compare option is passed
    search_modes = ["compare", "highlowres"]
    # Ensure at least one argument was passed for search_mode
    if not any(key in search_modes for key in argument_dict.keys()):
        print("Error: must provide either 'compare' or 'highlowres' for required argument search_mode.")
        exit(1)
    # Ensure user provides exactly one argument for search_mode
    elif "compare" in argument_dict.keys() and "highlowres" in argument_dict.keys():
        print("Error: more than one argument for search_mode provided, see README.md for more details.")
        exit(1)

    # Prepare log filename
    time_prefix = time.strftime(r"%m_%d_%y_%H_%M_%S%p", time.localtime(time.time()))
    argument_dict["log_filename"] = f"{time_prefix}_matches.txt"

    # List of files to compare to key
    filename_list = glob.glob((texture_path + "*"))
    # Ensure path_to_textures contains files
    if len(filename_list) == 0:
        print("Error: no files in path_to_textures, are you sure you provided the right directory?")

    # Function calls for threaded / normal image comparison:
    if use_threading != 0:
        multithreading_compare(filename_list, argument_dict, use_threading)
    else:
        argument_dict["filename_list"] = filename_list
        image_compare(**argument_dict)


if __name__ == "__main__":
    # Tell multithreading how to start each process
    multiprocessing.set_start_method("spawn")
    main()
