"""
Contains create function to build layout factories from class name
"""

from .diffuse_builder import RandomSizeParticles


def create_layout_factory(class_name, config):
    return globals()[class_name](config)
