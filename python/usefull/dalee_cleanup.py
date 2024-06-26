''' This script converts all .webp files in given directory into .png format and saves them
into other specified directory. Then it removes originals. 
This script was created in order to clean up rather messy downloads from Dalee image 
generator.
'''

#==================================================================================================
#                                               IMPORTS
#==================================================================================================
from __future__ import annotations # Type hints can now be used for methods returning their
                                   # own class
import os # Interactions with filesystem
import argparse # Parsing terminal command parameters
from PIL import Image # Image processing
from collections.abc import Iterator # Type hints


#==================================================================================================
#                                            FILE PROCESSING
#==================================================================================================

class ImageWriter:
    '''
    A class for writing images to a specified output path.

    Attributes:
        _IMAGE_FILENAME_FORMAT (str): The format string for generating image filenames.
        _output_path (str): The path where the images will be saved.
        _image_count (int): The current count of images written.
    '''

    _IMAGE_FILENAME_FORMAT: str = '{:03d}.png'

    def __init__(self, output_path: str)-> None:
        '''
        Initializes an ImageWriter instance.

        Args:
            output_path (str): The path where images will be saved.
        '''
        if not os.path.exists(output_path):
            print(f'Path {output_path} do not exists. Created path.')
            os.mkdir(output_path)
        
        self._output_path = output_path
        self._image_count = 1
        while os.path.exists(self._build_image_path()):
            self._image_count += 1
        print(f'Initial image count is {self._image_count-1}.')

    def _build_image_path(self)-> str:
        '''
        Builds the full path for the next image to be written.

        Returns:
            str: The full path for the next image.
        '''
        return os.path.join(self._output_path,
                            ImageWriter._IMAGE_FILENAME_FORMAT.format(self._image_count))
            
    def write_image(self, image: Image)-> None:
        '''
        Writes the provided image to the output path.

        Args:
            image (PIL.Image): The image to be written.
        '''
        image_path = self._build_image_path()
        image.save(image_path, 'png')
        print(f'Saved image at {image_path}')
        self._image_count += 1

class ImageSource:
    '''
    A class for iterating over images in a specified source path.

    Attributes:
        _source_list (list): A list of paths to input images.
        _destructive (bool): A flag indicating whether images should be removed after iteration.
    '''

    def __init__(self, source_path: str, destructive: bool=False,
                 recursive: bool= False)-> None:
        '''
        Initializes an ImageSource instance.

        Args:
            source_path (str): The path where input images are located.
            destructive (bool, optional): Flag indicating whether images should be removed after iteration. Defaults to False.
            recursive (bool, optional): Flag indicating whether to recursively search for images in subdirectories. Defaults to False.
        '''
        if not os.path.exists(source_path):
            raise OSError(f'Source path {source_path} do not exist.')
        self._source_list = self._generate_source_list(source_path, recursive)
        self._destructive = destructive
        print(f'Found {len(self._source_list)} input images.')
    
    @staticmethod
    def _generate_source_list(source_path:str, recursive:bool)-> list[str]:
        '''
        Recursively generates a list of input image paths from the specified source path.

        Args:
            source_path (str): The path where input images are located.
            recursive (bool): Flag indicating whether to recursively search for images in subdirectories.

        Returns:
            list: A list of paths to input images.
        '''
        input_list = []
        for file in os.scandir(source_path):
            if os.path.isdir(file):
                # This is bad, I should find better way to check if folder is hidden 
                if recursive and not file.name[0] == '.':
                    input_list.extend(ImageSource._generate_source_list(source_path, recursive))
            else:
                if file.name.split('.')[-1] == 'webp':
                    input_list.append(file.path)
        return input_list

    def __iter__(self)-> ImageSource:
        '''
        Returns an iterator object.

        Returns:
            ImageSource: An iterator object.
        '''
        return self

    def __next__(self):
        '''
        Returns the next image from the source path.

        Returns:
            PIL.Image: The next image from the source path.

        Raises:
            StopIteration: If there are no more images to iterate over.
        '''
        try:
            path = self._source_list.pop()
            img = Image.open(path).convert('RGB')
            if self._destructive:
                os.remove(path)
            return img
        except IndexError:
            raise StopIteration()

#==================================================================================================
#                                            ARGUMENT PARSING
#==================================================================================================

def parse_arguments()-> argparse.Namespace:
    '''
    Parses command-line arguments.

    Returns:
        argparse.Namespace: An object containing parsed arguments.
    '''
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--source_path', type=str, required=True,
                        help='Path from which .webp images will be read.')
    parser.add_argument('-o', '--output_path', type=str, required=True,
                        help='Folder to which .png image will be saved.')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='If this is set then subfolders of source paht will also be searched for images')
    parser.add_argument('-d', '--destructive', action='store_true',
                        help='If this is active then source images will be deleted after conversion.')
    return parser.parse_args()

#==================================================================================================
#                                             MAIN
#==================================================================================================
def main(args: argparse.Namespace)-> None:
    '''
    Main function for converting .webp images to .png format.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    '''
    sources = ImageSource(args.source_path, args.destructive, args.recursive)
    writer = ImageWriter(args.output_path)
    for image in sources:
        writer.write_image(image)

if __name__ == '__main__':
    main(parse_arguments())