import json
import time
from aux.settings import results_dir


def save_to_file(data, identifier):
    """Save the given data to a file with a unique identifier and timestamp."""
    file_name = f"{results_dir}/{identifier}_result_{time.strftime('%Y%m%d-%H%M%S')}.json"
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)
    return file_name
