"""
Build single MesoCrystal for given MesoParameters.
"""
import math
import bornagain as ba
from bornagain import nm, deg
import random


class MesoCrystalBuilder:
    """
    Meso crystal sample builder
    """
    def __init__(self, config, particle_material):
        self.m_config = config
        self.particle_material = particle_material
        self.m_lattice_length_a = config["lattice_length_a"]
        self.m_lattice_length_c = config["lattice_length_c"]
        self.m_nparticles = config["nparticles"]
        self.m_nanoparticle_radius = config["nanoparticle_radius"]
        self.m_sigma_nanoparticle_radius = config["sigma_nanoparticle_radius"]
        self.m_meso_height = config["meso_height"]
        self.m_meso_radius = config["meso_radius"]
        self.particle_pos_sigma = config["particle_pos_sigma"]
        self.m_rotation_x = config["rotation_x"]
        self.m_rotation_z = config["rotation_z"]
        pass

    def create_lattice(self, length_a, length_c):
        result = ba.Lattice.createHexagonalLattice(length_a, length_c)
        result.setSelectionRule(ba.SimpleSelectionRule(-1, 1, 1, 3))
        return result

    def create_particle(self, material):
        return None

    def create_outer_formfactor(self):
        return None

    def create_basis(self, material, lattice):
        particle = self.create_particle(material)

        bas_a = lattice.getBasisVectorA()
        bas_b = lattice.getBasisVectorB()
        bas_c = lattice.getBasisVectorC()

        position_0 = ba.kvector_t(0.0, 0.0, 0.0)
        position_1 = 1.0/3.0*(2.0*bas_a + bas_b + bas_c)
        position_2 = 1.0/3.0*(bas_a + 2.0*bas_b + 2.0*bas_c)
        pos_vector = [position_0, position_1, position_2]
        basis = ba.ParticleComposition()
        basis.addParticles(particle, pos_vector)
        return basis

    def create_meso(self):

        lattice = self.create_lattice(self.m_lattice_length_a,
                                      self.m_lattice_length_c)

        basis = self.create_basis(self.particle_material, lattice)

        ff_meso = self.create_outer_formfactor()

        npc = ba.Crystal(basis, lattice)
        npc.setPositionVariance(self.particle_pos_sigma*self.particle_pos_sigma)
        result = ba.MesoCrystal(npc, ff_meso)

        if self.m_rotation_z != 0.0:
            rotZ = ba.RotationZ(self.m_rotation_z*deg)
            result.setRotation(rotZ)

        if self.m_rotation_x != 0.0:
            rotX = ba.RotationX(self.m_rotation_x*deg)
            result.rotate(rotX)

        return result


class FixedCylinder(MesoCrystalBuilder):
    """
    Meso crystal sample builder
    """
    def __init__(self, config, particle_material):
        super().__init__(config, particle_material)

    def create_particle(self, material):
        return ba.Particle(material, ba.FormFactorFullSphere(self.m_nanoparticle_radius))

    def create_outer_formfactor(self):
        return ba.FormFactorCylinder(self.m_meso_radius, self.m_meso_height)


class FuzzyCylinder(MesoCrystalBuilder):
    """
    Meso crystal sample builder
    """
    def __init__(self, config, particle_material):
        super().__init__(config, particle_material)

    def create_particle(self, material):
        scale_param = math.sqrt(math.log((self.m_sigma_nanoparticle_radius/self.m_nanoparticle_radius)**2 + 1.0))
        particle = ba.Particle(material, ba.FormFactorSphereLogNormalRadius(self.m_nanoparticle_radius, scale_param, self.m_nparticles))
        # particle = ba.Particle(material, ba.FormFactorFullSphere(np_radius))
        return particle

    def create_outer_formfactor(self):
        return ba.FormFactorCylinder(self.m_meso_radius, self.m_meso_height)

