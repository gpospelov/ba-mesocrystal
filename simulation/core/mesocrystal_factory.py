"""
Builds collection of mesocrystals
"""
from core.create_mesocrystal_builder import create_mesocrystal_builder
import copy
import numpy as np
import numpy.random as npr
import random
import math


class MesoCrystalFactory:
    """
    Base class to generate collection of mesocrystals according to some arrangement.
    External MesoCrystalBuilder is used to generate single mesocrystal.
    """
    def __init__(self, config=None):
        self.m_config = config
        pass

    def surface_density(self):
        filling_ratio = self.m_config["surface_filling_ratio"]
        radius = self.m_config["meso_radius"]
        return filling_ratio/np.pi/radius/radius


class RotatedMesoFactory(MesoCrystalFactory):
    """
    Generates collection of 360 mesocrystals rotated around Z.
    External MesoCrystalBuilder is used to generate single mesocrystal.
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_phi_start = config["phi_start"]
        self.m_phi_stop = config["phi_stop"]
        self.m_phi_rotation_steps = config["phi_steps"]
        self.m_tilt_start = config["tilt_start"]
        self.m_tilt_stop = config["tilt_stop"]
        self.m_tilt_steps = config["tilt_steps"]
        self.m_meso_radius = config["meso_radius"]
        self.m_total_meso_area = 0.0
        self.m_meso_count = 0

    def build_mesocrystals(self, material=None):
        result = []

        dphi = (self.m_phi_stop - self.m_phi_start)/self.m_phi_rotation_steps
        dtilt = (self.m_tilt_stop - self.m_tilt_start)/self.m_tilt_steps

        for i_tilt in range(0, int(self.m_tilt_steps)):
            tilt = self.m_tilt_start + i_tilt * dtilt
            for i_phi in range(0, int(self.m_phi_rotation_steps)):
                self.m_meso_count+= 1
                phi = self.m_phi_start + i_phi*dphi

                cfg = copy.deepcopy(self.m_config)
                cfg["rotation_z"] = phi
                cfg["rotation_x"] = tilt
                meso_builder = create_mesocrystal_builder(cfg, material)

                mesocrystal = meso_builder.create_meso()
                self.m_total_meso_area += np.pi * self.m_meso_radius * self.m_meso_radius
                result.append((mesocrystal, 1.0))

        return result

    def surface_density(self):
        area = self.m_total_meso_area/self.m_config["surface_filling_ratio"]
        return 5e-02*self.m_meso_count/area
        # filling_ratio = self.m_config["surface_filling_ratio"]
        # return 5e-02*filling_ratio / (self.m_total_meso_area/self.m_meso_count)


class SingleMesoFactory(MesoCrystalFactory):
    """
    Generates single mesocrystal using MesoCrystalBuilder
    """
    def __init__(self, config=None):
        super().__init__(config)

    def build_mesocrystals(self, material):
        result = []

        meso_builder = create_mesocrystal_builder(self.m_config, material)
        mesocrystal = meso_builder.create_meso()

        result.append((mesocrystal, 1.0))

        return result


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

    def gate(self, a, b):
        return a + (b-a)*npr.random()

    def generate_phi(self):
        value = random.choice(self.m_phi_values)+self.gate(-5.0, 5.0)
        return value

    def generate_nanoparticle_radius(self):
        return npr.normal(self.m_nanoparticle_radius, self.m_sigma_nanoparticle_radius)

    def generate_tilt(self):
        return self.gate(-0.2, 0.2)

    def generate_meso_radius(self):
        # sizes = [50.0, 100.0, 1000.0, 1200.0]
        # return random.choice(sizes)
        # return self.gate(100, 1200)
        return self.gate(400, 1200)

    def generate_meso_height(self):
        # heights = [50.0, 100.0, 500.0, 550.0, 550.0]
        # return random.choice(heights)
        # return self.gate(100, 550)
        return self.gate(400, 550)

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
            cfg["sigma_meso_radius"] = meso_radius/100.
            cfg["meso_height"] = meso_height
            cfg["sigma_meso_height"] = meso_height/100.
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


class MixtureMesoFactory(MesoCrystalFactory):
    """
    Generates collection of random mesocrystals
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_meso_count = config["meso_count"]
        self.m_tilt_span = config["tilt_span"]
        self.m_phi_values = [0.0, 17.75, 28.3, 39.35, 57.5]
        self.m_nanoparticle_radius = config["nanoparticle_radius"]
        self.m_sigma_nanoparticle_radius = config["sigma_nanoparticle_radius"]
        self.m_lattice_length_a = config["lattice_length_a"]
        self.m_lattice_length_c = config["lattice_length_c"]
        self.m_meso_height = config["meso_height"]
        self.m_meso_radius = config["meso_radius"]
        self.m_total_meso_area = 0.0

    def gate(self, a, b):
        return a + (b-a)*npr.random()

    def generate_phi(self):
        return random.choice(self.m_phi_values)+self.gate(-5.0, 5.0)

    def generate_nanoparticle_radius(self):
        # return self.m_nanoparticle_radius
        return npr.normal(self.m_nanoparticle_radius, self.m_sigma_nanoparticle_radius)

    def generate_tilt(self):
        return self.gate(-self.m_tilt_span, self.m_tilt_span)

    def generate_meso_radius(self):
        return self.m_meso_radius

    def generate_meso_height(self):
        return self.m_meso_height

    def generate_lattice_length_a(self):
        return self.m_lattice_length_a

    def generate_lattice_length_c(self):
        return self.m_lattice_length_c
        # return self.m_lattice_length_c+self.gate(-2., 2.)
        # return npr.normal(self.m_lattice_length_c, 0.5)

    def generate_sequence(self, meso_count, material, weight):
        result = list()

        for i in range(0, meso_count):
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
            # cfg["sigma_meso_radius"] = meso_radius/100.
            cfg["meso_height"] = meso_height
            # cfg["sigma_meso_height"] = meso_height/100.
            cfg["lattice_length_a"] = lattice_a
            cfg["lattice_length_c"] = lattice_c

            meso_builder = create_mesocrystal_builder(cfg, material)
            mesocrystal = meso_builder.create_meso()

            self.m_total_meso_area += np.pi*meso_radius*meso_radius
            result.append((mesocrystal, weight))

        return result

    def build_mesocrystals(self, material):
        result = list()

        # small
        self.m_meso_height = 200
        self.m_meso_radius = 200
        self.m_tilt_span = 0.5
        self.m_lattice_length_c = 31.1
        result += self.generate_sequence(int(self.m_meso_count*0.5), material, 0.4)
        # print("aaa", len(result))

        self.m_meso_height = 800
        self.m_meso_radius = 2000
        self.m_tilt_span = 0.1
        self.m_lattice_length_c = 31.1
        result += self.generate_sequence(int(self.m_meso_count*0.5), material, 0.6)
        print("bbb", len(result))
        return result

    def surface_density(self):
        area = self.m_total_meso_area/self.m_config["surface_filling_ratio"]
        return 1e-02*self.m_meso_count/area
        # filling_ratio = self.m_config["surface_filling_ratio"]
        # return 5e-02*filling_ratio / (self.m_total_meso_area/self.m_meso_count)

