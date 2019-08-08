"""
Builds collection of mesocrystals
"""
import abc
import bornagain as ba
from core.create_mesocrystal_builder import create_mesocrystal_builder
from .layout_factory_base import LayoutFactory
from .meso_utils import random_gate
import copy
import numpy as np
import numpy.random as npr
import random


class MesoCrystalFactory(LayoutFactory):
    """
    Base class to generate collection of mesocrystals according to some arrangement.
    External MesoCrystalBuilder is used to generate single mesocrystal.
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_average_layer_thickness = config["average_layer_thickness"]
        self.m_meso_elevation = config["meso_elevation"]
        self.m_average_meso_area = 0.0
        pass

    @abc.abstractmethod
    def surface_density(self):
        return None

    @abc.abstractmethod
    def build_mesocrystals(self, particle_material):
        return list()

    def create_layout(self, particle_material):
        layout = ba.ParticleLayout()

        mesocrystals = self.build_mesocrystals(particle_material)
        for meso, weight in mesocrystals:
            layout.addParticle(meso, weight, ba.kvector_t(0, 0, -self.m_average_layer_thickness+self.m_meso_elevation))

        layout.setTotalParticleSurfaceDensity(self.surface_density())

        return layout


class RotatedMesoFactory(MesoCrystalFactory):
    """
    Generates collection of 360 mesocrystals rotated around Z.
    External MesoCrystalBuilder is used to generate single mesocrystal.
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_phi_start = config["RotatedMesoFactory"]["phi_start"]
        self.m_phi_stop = config["RotatedMesoFactory"]["phi_stop"]
        self.m_phi_rotation_steps = config["RotatedMesoFactory"]["phi_steps"]
        self.m_tilt_start = config["RotatedMesoFactory"]["tilt_start"]
        self.m_tilt_stop = config["RotatedMesoFactory"]["tilt_stop"]
        self.m_tilt_steps = config["RotatedMesoFactory"]["tilt_steps"]
        self.m_layout_weight = config["RotatedMesoFactory"]["layout_weight"]
        self.m_filling_ratio = config["RotatedMesoFactory"]["surface_filling_ratio"]

    def build_mesocrystals(self, material=None):
        result = []

        dphi = (self.m_phi_stop - self.m_phi_start)/self.m_phi_rotation_steps
        dtilt = (self.m_tilt_stop - self.m_tilt_start)/self.m_tilt_steps

        total_meso_area = 0.0
        for i_tilt in range(0, int(self.m_tilt_steps)):
            tilt = self.m_tilt_start + i_tilt * dtilt
            for i_phi in range(0, int(self.m_phi_rotation_steps)):
                phi = self.m_phi_start + i_phi*dphi

                cfg = copy.deepcopy(self.m_config)
                cfg["rotation_z"] = phi
                cfg["rotation_x"] = tilt
                meso_builder = create_mesocrystal_builder(cfg, material)

                mesocrystal = meso_builder.create_meso()
                total_meso_area += meso_builder.meso_area()
                result.append((mesocrystal, 1.0))

        self.m_average_meso_area = total_meso_area/len(result)

        return result

    def surface_density(self):
        return self.m_layout_weight*self.m_filling_ratio/self.m_average_meso_area


class SingleMesoFactory(MesoCrystalFactory):
    """
    Generates single mesocrystal using MesoCrystalBuilder
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_filling_ratio = config["SingleMesoFactory"]["surface_filling_ratio"]

    def build_mesocrystals(self, material):
        result = []

        meso_builder = create_mesocrystal_builder(self.m_config, material)
        mesocrystal = meso_builder.create_meso()
        self.m_average_meso_area = meso_builder.meso_area()

        result.append((mesocrystal, 1.0))

        return result

    def surface_density(self):
        return self.m_filling_ratio/self.m_average_meso_area


class RandomMesoFactory(MesoCrystalFactory):
    """
    Generates single mesocrystal using MesoCrystalBuilder
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_meso_count = config["RandomMesoFactory"]["meso_count"]
        self.m_layout_weight = config["RandomMesoFactory"]["layout_weight"]
        self.m_filling_ratio = config["RandomMesoFactory"]["surface_filling_ratio"]
        self.m_tilt_dtheta = config["RandomMesoFactory"]["tilt_dtheta"]
        self.m_meso_radius = config["meso_radius"]
        self.m_meso_height = config["meso_height"]
        self.m_phi_values = [0.0, 17.5, 29.0, 39.0, 58.5]

    def generate_phi(self):
        value = random.choice(self.m_phi_values)+random_gate(-0.25, 0.25)
        return value

    def generate_tilt(self):
        return random_gate(-self.m_tilt_dtheta, self.m_tilt_dtheta)

    def generate_radius(self):
        return self.m_meso_radius

    def generate_height(self):
        return self.m_meso_height

    def build_mesocrystals(self, material):
        result = list()

        total_meso_area = 0.0
        for i in range(0, self.m_meso_count):
            cfg = copy.deepcopy(self.m_config)

            phi = self.generate_phi()
            tilt = self.generate_tilt()
            meso_radius = self.generate_radius()
            meso_height = self.generate_height()

            print("phi:{:f} tilt:{:f} radius:{:f} height:{:f}".format(phi, tilt, meso_radius, meso_height))

            cfg["rotation_z"] = phi
            cfg["rotation_x"] = tilt
            cfg["meso_radius"] = meso_radius
            cfg["meso_height"] = meso_height

            meso_builder = create_mesocrystal_builder(cfg, material)
            mesocrystal = meso_builder.create_meso()
            total_meso_area += meso_builder.meso_area()

            result.append((mesocrystal, 1.0))

        self.m_average_meso_area = total_meso_area/len(result)
        return result

    def surface_density(self):
        return self.m_layout_weight*self.m_filling_ratio/self.m_average_meso_area


class LargeRandomMesoFactory(RandomMesoFactory):
    """
    Generates single mesocrystal using MesoCrystalBuilder
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_meso_count = config["LargeRandomMesoFactory"]["meso_count"]
        self.m_layout_weight = config["LargeRandomMesoFactory"]["layout_weight"]
        self.m_filling_ratio = config["LargeRandomMesoFactory"]["surface_filling_ratio"]
        self.m_tilt_dtheta = config["LargeRandomMesoFactory"]["tilt_dtheta"]

    def generate_radius(self):
        return 2000.0

    def generate_height(self):
        return 800.0


class SmallRandomMesoFactory(RandomMesoFactory):
    """
    Generates single mesocrystal using MesoCrystalBuilder
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_meso_count = config["SmallRandomMesoFactory"]["meso_count"]
        self.m_layout_weight = config["SmallRandomMesoFactory"]["layout_weight"]
        self.m_filling_ratio = config["SmallRandomMesoFactory"]["surface_filling_ratio"]
        self.m_tilt_dtheta = config["SmallRandomMesoFactory"]["tilt_dtheta"]

    def generate_radius(self):
        return 200.0

    def generate_height(self):
        return 100.0
