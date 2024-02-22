import yaml
import pathlib

# Assuming that this file is in /src, this is the path to the root folder
ROOTPATH = pathlib.Path(__file__).parent.parent

# Change this if the config file is located elsewhere
CONFIGDIR = ROOTPATH / 'src'

# Name of the config file
CONFIGFILE='config.yaml'


def load_config():
    '''
    Loads and returns the config file contents as a dictionary.
    '''
    with open( CONFIGDIR / CONFIGFILE ,'r') as file:
        config = yaml.safe_load(file)
    return config

def getdir(dirname: str):
    '''
    Returns full path to the directory specified in dirname as a string.
    @param dirname: Name of the directory. Must be exactly as it is in configfile and under section 'directories'.
    '''
    config = load_config()
    path = config['directories'][dirname]
    return str(ROOTPATH.joinpath(path))

def get_filepath(dirname: str, filename: str):
    '''
    Returns full path to file 'filename' located in directory 'dirname'. 'dirname' must be a valid entry in config file under 'directories'.
    '''
    dirpath = pathlib.Path(getdir(dirname))
    return str(dirpath / filename)

def get_image(filename):
    '''
    Convenience function to simplify image path acquisition. Equivalent to get_filepath('images', filename).
    '''
    return get_filepath('images', filename)
