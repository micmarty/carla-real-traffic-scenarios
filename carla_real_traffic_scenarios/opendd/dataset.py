import sqlite3
from pathlib import Path
from typing import NamedTuple, Tuple, Dict

import numpy as np
from PIL import Image

_BLACKLISTED_SESSION_NAMES_DUE_TO_WRONG_GEOREFERENCE = [
    'rdb6_2DJI_0006', 'rdb6_2DJI_0007', 'rdb6_2DJI_0008', 'rdb6_2DJI_0009', 'rdb6_DJI_0016', 'rdb3_M1DJI_0021'
]
BLACKLISTED_SESSION_NAMES = _BLACKLISTED_SESSION_NAMES_DUE_TO_WRONG_GEOREFERENCE

class Place(NamedTuple):
    name: str
    image_size: Tuple[int, int]
    image_path: str
    world_params: np.ndarray


class OpenDDDataset:

    def __init__(self, dataset_dir):
        dataset_dir = Path(dataset_dir)
        self.dataset_dir = dataset_dir.as_posix()
        self.db_path = (dataset_dir / 'rdb1to6.sqlite').as_posix()
        self.time_slots = self._fetch_time_slots(self.db_path)  # TODO: divide on TRAIN and TEST
        self.places: Dict[str, Place] = self._fetch_places(dataset_dir)

    def _fetch_time_slots(self, db_path):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'")
            session_names = [row[0] for row in cursor.fetchall()]
            session_names = [n for n in session_names if n not in BLACKLISTED_SESSION_NAMES]
            return session_names

    def _fetch_places(self, dataset_dir):
        georeferenced_images_dir = dataset_dir / 'image_georeferenced'

        places = {}
        for image_path in georeferenced_images_dir.glob('*.jpg'):
            image_size = Image.open(image_path.as_posix()).size

            name = image_path.stem
            world_file_path = image_path.parent / f'{name}.tfw'
            with world_file_path.open('r') as wf:
                world_params = np.array([float(line) for line in wf])

            places[name] = Place(name, image_size, image_path.as_posix(), world_params)
        return places