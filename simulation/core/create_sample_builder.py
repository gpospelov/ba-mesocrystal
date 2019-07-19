"""
Create function to build various sample builders.
"""
from .sample_builder_ver0 import SampleBuilderVer0
from .sample_builder_ver1 import SampleBuilderVer1
from .sample_builder_ver2 import SampleBuilderVer2


def create_sample_builder(config):
    """
    Returns new sample builder of given type.
    """
    class_name = config["sample_builder_type"]
    return globals()[class_name](config)
