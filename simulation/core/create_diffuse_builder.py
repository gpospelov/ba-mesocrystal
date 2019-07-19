from .diffuse_builder import RandomSizeParticles


def create_diffuse_builder(config):
    """
    Returns new diffuse background builder for given type.
    """
    class_name = config["diffuse_builder_type"]
    return None if class_name == "None" else globals()[class_name](config)
