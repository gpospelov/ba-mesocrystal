"""
Create function to build various mesocrystal builders.
"""
from .mesocrystal_builder import FixedCylinder
from .mesocrystal_builder import FuzzyCylinder


def create_mesocrystal_builder(config, material):
    """
    Returns new mesocrystal builder of given type.
    """
    class_name = config["meso_builder_type"]
    return globals()[class_name](config, material)
