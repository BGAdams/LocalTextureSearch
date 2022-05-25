# Local Texture Search
Local Texture Search is a command line Python 3 program which takes an image as input and looks for similar images. The
program has two modes: the first looks for an identical, higher resolution version of the input image, and the second
looks for images which are visually similar to the input.

### Installation:

##### Requirements:
- Python 3.x (ideally Python 3.9.2 or higher) with configured PATH environment variable
(https://www.python.org/downloads/release/python-396/)
- pip (https://pip.pypa.io/en/stable/installation/)

**Steps:**

1. Extract the .zip folder containing the files for Local Texture Search into a directory of your choice (you will need
read/write permissions for that directory).
2. Open command prompt and navigate to the directory you extracted the Local Texture Search .zip file into using the 
_cd_ command
3. Run the command "pip install -r requirements.txt" to install the required Python modules



### Command line usage:
**Windows:**
python image_compare.py [required:compare_file] [required:path_to_textures] [required: search_mode] 
optional:threading=[thread_count] option:-v 
option:-compare

**Mac / Linux:**
python3 image_compare.py [required:compare_file] [required:path_to_textures] optional:threading=[thread_count] option:-v 
option:-compare

### Arguments:

Required arguments (denoted as [required:argument] above) must be provided in the same order as above, and before any 
optional arguments.

Optional arguments must be in the format argument=value, and must be capitalized exactly as they are above.
They can be provided in any order as long as they are after all required arguments.

Options have the form -[specifier] where specifier is a letter or word. Options must be provided after required 
arguments and exactly as written above.

#### Required arguments:

- **compare_file**: the image file to search for / compare to other images. Must be in the same directory as 
image_compare.py, must have file extension included in the name. Do not provide the full path, only the file name. 
Examples: selfie.jpg, mario_skin.png, t_god_skin_dif.dds.

- **path_to_images**: the absolute path to the folder which contains the images to be compared with the compare_file. 
Examples: 
- Windows: C:\Users\John\Desktop\Photos, ./photos
- UNIX: /home/ubuntu/pictures, 
    ./pictures (path must be subfolder of folder containing image_compare.py for ./ syntax to work). 

**search_mode**: tells the program what kind of search to perform.
- **highlowres**: search for identical, higher resolution image based on a lower resolution input
- **compare**: search for an image that is visually similar to the input image, slower than highlowres mode.

##### Optional arguments:

**WARNING**: Threading is very CPU intensive and may cause lag and/or overheating. Do not use this option if you are not
comfortable monitoring your CPU's usage / temperature. 

- **threading**: default = off, passing values from 2-4 will enable that many threads. Each thread is essentially
another version of the program running in parallel. The CPU usage of the program is multiplied by the number of threads,
so with 3 threads the program is 3 times as CPU intensive, but also runs around 3 times faster.
Passing values outside of the defined range will leave threading disabled.
	
##### Options:
- **-v**: verbose mode, program will print all file comparison outputs, and print the log file's name when a match is 
found.

### Logging:

Matching file names are logged to a text file which is named after the time and date when the program started. Log files
are saved in the same directory as image_compare.py.

### Examples:
Examples which run Local Texture Search on the provided sample imageset. 

For the examples, you can visually compare the compare_file in the command to the files named in the log to see the progam's accuracy, and what it considers a "similar" image to be.

UNIX:
- **highlowres**: python3 image_compare.py highlowres.png ./sample_imageset/ highlowres -v
- **compare**: python3 image_compare.py compare.dds ./sample_imageset/ compare -v

Windows:
- **highlowres**: python image_compare.py highlowres.png ./sample_imageset/ highlowres -v
- **compare**: python image_compare.py compare.dds ./sample_imageset/ compare -v
