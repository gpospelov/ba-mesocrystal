"""
Contains create function to build layout factories from class name
"""

from .diffuse_builder import RandomSizeParticles
from .mesocrystal_factory import RotatedMesoFactory
from .mesocrystal_factory import SingleMesoFactory
from .mesocrystal_factory import RandomMesoFactory
from .mesocrystal_factory import SmallRandomMesoFactory
from .mesocrystal_factory import LargeRandomMesoFactory


def create_layout_factory(class_name, config):
    return globals()[class_name](config)
