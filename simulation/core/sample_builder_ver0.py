"""
Version of SampleBuilder from 2016.
Builds whole sample with 360 rotated mesocrystals at once.
"""
import numpy
import math
import bornagain as ba
from bornagain import nm, deg, angstrom


class SampleBuilderVer0:
    """
    Meso crystal sample builder
    """
    def __init__(self):

        # Elisabeth c = 31.3 +-0.1, a = 12.7+-0.1

        self.m_lattice_length_a = 12.45*nm
        self.m_lattice_length_c = 31.0*nm
        self.m_nanoparticle_radius = 5.0*nm
        self.m_sigma_nanoparticle_radius = 0.3*nm
        self.m_meso_height = 200*nm
        self.m_meso_radius = 800*nm
        self.m_sigma_meso_height = 20.0*nm
        self.m_sigma_meso_radius = 20.0*nm
        self.m_sigma_lattice_length_a = 0.5*nm
        self.m_roughness = 6.0*nm
        self.m_surface_filling_ratio = 0.25
        self.m_phi_start = 0.0*deg
        self.m_phi_stop = 360.0*deg
        self.m_phi_rotation_steps = 1
        self.m_tilt_start = 0.0*deg
        self.m_tilt_stop = 1.0*deg
        self.m_tilt_steps = 1.0
        self.m_alpha_i = 0.4*deg
        self.m_phi_i = 0.0*deg
        self.m_wavelength = 1.77*angstrom
        self.m_resolution_scale = 1.0

    def CreateMeso(self, material, meso_form_factor):
        radius = self.m_nanoparticle_radius

        lattice = self.CreateLattice(self.m_lattice_length_a, self.m_lattice_length_c)
        bas_a = lattice.getBasisVectorA()
        bas_b = lattice.getBasisVectorB()
        bas_c = lattice.getBasisVectorC()

        scale_param = math.sqrt(math.log((self.m_sigma_nanoparticle_radius/self.m_nanoparticle_radius)**2 + 1.0))
        particle = ba.Particle(material, ba.FormFactorSphereLogNormalRadius(radius, scale_param, 10))
        # particle = ba.Particle(material, ba.FormFactorFullSphere(radius))

        position_0 = ba.kvector_t(0.0, 0.0, 0.0)
        position_1 = 1.0/3.0*(2.0*bas_a + bas_b + bas_c)
        position_2 = 1.0/3.0*(bas_a + 2.0*bas_b + 2.0*bas_c)
        pos_vector = [position_0, position_1, position_2]
        basis = ba.ParticleComposition()
        basis.addParticles(particle, pos_vector)
        npc = ba.Crystal(basis, lattice)
        dw_factor = self.m_sigma_lattice_length_a*self.m_sigma_lattice_length_a/6.0
        npc.setDWFactor(dw_factor)
        result = ba.MesoCrystal(npc, meso_form_factor)
        return result

    def CreateLattice(self, a, c):
        result = ba.Lattice.createTrigonalLattice(a, c)
        result.setSelectionRule(ba.SimpleSelectionRule(-1, 1, 1, 3))
        return result

    # constructs the sample for current values of parameters
    def build_sample(self, wavelength=None):
        # create materials
        surface_density = self.m_surface_filling_ratio/numpy.pi/self.m_meso_radius/self.m_meso_radius
        n_particle = complex(1.0-2.84e-5, 4.7e-7)
        avg_n_squared_meso = 0.7886*n_particle**2 + 0.2114
        n_avg = numpy.sqrt(self.m_surface_filling_ratio*avg_n_squared_meso + 1.0 - self.m_surface_filling_ratio)
        n_particle_adapted = numpy.sqrt(n_avg**2 + n_particle**2 - 1.0)
        particle_material = ba.HomogeneousMaterial("nanoparticle", n_particle_adapted)

        ff_cyl = ba.FormFactorCylinder(self.m_meso_radius, self.m_meso_height)
        ff_meso = ba.FormFactorDecoratorDebyeWaller(ff_cyl, self.m_sigma_meso_height**2/2.0,
                                             self.m_sigma_meso_radius**2/2.0)

        # Create multilayer
        multi_layer = ba.MultiLayer()

        air_material = ba.HomogeneousMaterial("Air", 0.0, 0.0)
        substrate_material = ba.HomogeneousMaterial("Substrate", 7.57e-6, 1.73e-7)
        average_layer_material = ba.HomogeneousMaterial("AverageLayer", n_avg)
        air_layer = ba.Layer(air_material)
        avg_layer = ba.Layer(average_layer_material, self.m_meso_height)
        substrate_layer = ba.Layer(substrate_material)
        particle_decoration = ba.ParticleLayout()

        mesocrystal = self.CreateMeso(particle_material, ff_meso)

        dphi = (self.m_phi_stop - self.m_phi_start)/int(self.m_phi_rotation_steps)
        dtilt = (self.m_tilt_stop - self.m_tilt_start)/int(self.m_tilt_steps)

        for i_tilt in range(0, int(self.m_tilt_steps)):
            for i_phi in range(0, int(self.m_phi_rotation_steps)):

                phi = self.m_phi_start + i_phi*dphi
                rotZ = ba.RotationZ(phi)
                tilt = self.m_tilt_start + i_tilt*dtilt
                rotX = ba.RotationX(tilt)
                # print "phi", i_phi, rad2deg(phi), "tilt", i_tilt, rad2deg(tilt)

                mesocrystal.setRotation(rotZ)
                mesocrystal.rotate(rotX)

                particle_decoration.addParticle(mesocrystal, 1.0, ba.kvector_t(0, 0, -self.m_meso_height))

        particle_decoration.setTotalParticleSurfaceDensity(surface_density)

        avg_layer.addLayout(particle_decoration)

        roughness = ba.LayerRoughness(self.m_roughness, 0.3, 500.0*nm)

        multi_layer.addLayer(air_layer)
        multi_layer.addLayer(avg_layer)
        multi_layer.addLayerWithTopRoughness(substrate_layer, roughness)
        self.sample = multi_layer
        return self.sample
