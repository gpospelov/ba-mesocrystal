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
        self.m_meso_count = config["meso_count"]
        self.m_phi_values = [0.0, 17.5, 29.0, 39.0, 58.5]
        self.m_nanoparticle_radius = config["nanoparticle_radius"]
        self.m_sigma_nanoparticle_radius = config["sigma_nanoparticle_radius"]
        self.m_lattice_length_a = config["lattice_length_a"]
        self.m_lattice_length_c = config["lattice_length_c"]
        self.m_total_meso_area = 0.0

    def generate_phi(self):
        value = random.choice(self.m_phi_values)+self.gate(-5.0, 5.0)
        return value

    def generate_nanoparticle_radius(self):
        return npr.normal(self.m_nanoparticle_radius, self.m_sigma_nanoparticle_radius)

    def generate_tilt(self):
        return random_gate(-0.2, 0.2)

    def generate_meso_radius(self):
        # sizes = [50.0, 100.0, 1000.0, 1200.0]
        # return random.choice(sizes)
        # return self.gate(100, 1200)
        return random_gate(400, 1200)

    def generate_meso_height(self):
        # heights = [50.0, 100.0, 500.0, 550.0, 550.0]
        # return random.choice(heights)
        # return self.gate(100, 550)
        return random_gate(400, 550)

    def generate_lattice_length_a(self):
        return npr.normal(self.m_lattice_length_a, 0.002)

    def generate_lattice_length_c(self):
        return npr.normal(self.m_lattice_length_c, 0.002)

    def build_mesocrystals(self, material):
        result = list()

        for i in range(0, self.m_meso_count):
            cfg = copy.deepcopy(self.m_config)

            phi = self.generate_phi()
            tilt = self.generate_tilt()
            nanoparticle_radius = self.generate_nanoparticle_radius()
            meso_radius = self.generate_meso_radius()
            meso_height = self.generate_meso_height()
            lattice_a = self.generate_lattice_length_a()
            lattice_c = self.generate_lattice_length_c()
            print("phi:{:f} tilt:{:f} nano_radius:{:f} m_radius:{:f} m_height:{:f} lattice_a:{:f} lattice_c:{:f}".format(phi, tilt, nanoparticle_radius, meso_radius, meso_height, lattice_a, lattice_c))

            cfg["rotation_z"] = phi
            cfg["rotation_x"] = tilt
            cfg["nanoparticle_radius"] = nanoparticle_radius
            cfg["meso_radius"] = meso_radius
            cfg["meso_height"] = meso_height
            cfg["lattice_length_a"] = lattice_a
            cfg["lattice_length_c"] = lattice_c

            meso_builder = create_mesocrystal_builder(cfg, material)
            mesocrystal = meso_builder.create_meso()

            self.m_total_meso_area += np.pi*meso_radius*meso_radius
            result.append((mesocrystal, 1.0))

        return result

    def surface_density(self):
        area = self.m_total_meso_area/self.m_config["surface_filling_ratio"]
        return 1e-02*self.m_meso_count/area
        # filling_ratio = self.m_config["surface_filling_ratio"]
        # return 5e-02*filling_ratio / (self.m_total_meso_area/self.m_meso_count)
