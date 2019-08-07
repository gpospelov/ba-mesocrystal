"""
Create function to build various mesocrystal factories.
"""
from .mesocrystal_factory import RotatedMesoFactory
from .mesocrystal_factory import SingleMesoFactory
from .mesocrystal_factory import RandomMesoFactory


def create_mesocrystal_factory(config):
    """
    Returns new mesocrystal factory of given type.
    """
    class_name = config["meso_factory_type"]
    return globals()[class_name](config)
