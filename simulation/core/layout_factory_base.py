import abc


class LayoutFactory(abc.ABC):
    """
    Base class to generate particle layouts.
    """
    def __init__(self, config):
        self.m_config = config

    @abc.abstractmethod
    def create_layout(self, particle_material):
        """
        Returns particle layout with particles or mesocrystal arangements
        """
