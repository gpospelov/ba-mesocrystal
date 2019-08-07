"""
Simplified mesocrystal simulation for demo purposes
"""
import bornagain as ba
from bornagain import deg, nm, angstrom
import math
import periodictable as pt
import numpy as np

m_pixel_size = 4 * 41.74e-3  # mm


class MesoCrystalBuilder:
    """
    Meso crystal sample builder
    """
    def __init__(self, particle_material):
        self.m_lattice_length_a = 12.5*nm
        self.m_lattice_length_c = 31.1*nm
        self.m_nparticles = 10
        self.m_nanoparticle_radius = 5.02*nm
        self.m_sigma_nanoparticle_radius = 0.3*nm
        self.m_meso_height = 300*nm
        self.m_meso_radius = 500*nm
        self.particle_pos_sigma = 0.3*nm
        self.m_rotation_x = 0.0
        self.m_rotation_z = 0.0
        self.particle_material = particle_material
        pass

    @staticmethod
    def create_lattice(length_a, length_c):
        result = ba.Lattice.createHexagonalLattice(length_a, length_c)
        result.setSelectionRule(ba.SimpleSelectionRule(-1, 1, 1, 3))
        return result

    def create_basis(self, material, lattice, np_radius, np_sigma_radius, nparticles):
        scale_param = math.sqrt(math.log((np_sigma_radius/np_radius)**2 + 1.0))
        particle = ba.Particle(material, ba.FormFactorSphereLogNormalRadius(np_radius, scale_param, nparticles))

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
        ff_meso = ba.FormFactorCylinder(self.m_meso_radius, self.m_meso_height)

        lattice = self.create_lattice(self.m_lattice_length_a,
                                      self.m_lattice_length_c)

        basis = self.create_basis(self.particle_material, lattice,
                                  self.m_nanoparticle_radius,
                                  self.m_sigma_nanoparticle_radius,
                                  self.m_nparticles)

        npc = ba.Crystal(basis, lattice)
        dw_factor = self.particle_pos_sigma*self.particle_pos_sigma
        npc.setPositionVariance(dw_factor)
        result = ba.MesoCrystal(npc, ff_meso)

        if self.m_rotation_z != 0.0:
            rotZ = ba.RotationZ(self.m_rotation_z*deg)
            result.setRotation(rotZ)

        if self.m_rotation_x != 0.0:
            rotX = ba.RotationX(self.m_rotation_x*deg)
            result.rotate(rotX)

        return result


def get_air(wavelength):
    return ba.MaterialBySLD("air", 0.0, 0.0)


def get_si(wavelength):
    si = pt.formula("Si")
    dens = pt.Si.density
    rho, mu = pt.xray_sld(si, density=pt.Si.density, wavelength=wavelength / angstrom)
    return ba.MaterialBySLD("si", rho*1e-6, mu*1e-6)


def get_iron_oxide(wavelength):
    oxide = pt.formula("Fe2O3")
    dens = 5.24
    rho, mu = pt.xray_sld(oxide, density=dens, wavelength=wavelength / angstrom)
    return ba.MaterialBySLD("Fe203", rho*1e-6, mu*1e-6)


def create_detector():
    """
    Creates rectangular detector.
    """
    m_distance = 909.99  # mm
    m_nx = 1024
    m_ny = 1024
    m_center_x = 108.2
    m_center_y = 942.0
    width, height = m_nx * m_pixel_size, m_ny * m_pixel_size
    u0 = m_center_x * m_pixel_size
    v0 = (m_ny - m_center_y) * m_pixel_size
    detector = ba.RectangularDetector(m_nx, width, m_ny, height)
    detector.setPerpendicularToDirectBeam(m_distance, u0, v0)
    return detector


def create_mesocrystal_layout(particle_material, average_layer_thickness):
    """
    Createss layout with mesocrystal collection.
    """
    m_meso_elevation = 50*nm
    m_surface_density = 1e-7

    layout = ba.ParticleLayout()

    # generating rotated mesocrystals
    mesocrystals = list()
    for phi in np.linspace(-5.0, 65.0, 141):
        builder = MesoCrystalBuilder(particle_material)
        builder.m_rotation_z = phi
        mesocrystals.append(builder.create_meso())

    for meso in mesocrystals:
        layout.addParticle(meso, 1.0, ba.kvector_t(0, 0, -average_layer_thickness + m_meso_elevation))

    layout.setTotalParticleSurfaceDensity(m_surface_density)

    return layout
    pass


def create_diffuse_layout(particle_material, average_layer_thickness):
    """
    Createss layout with mesocrystal collection.
    """

    m_radius = 5.02
    m_nparticles = 100
    m_sigma = 0.5
    m_diffuse_surface_density = 1e-2

    layout = ba.ParticleLayout()

    distr = ba.DistributionGaussian(m_radius, m_sigma)
    # scale_param = math.sqrt(math.log((m_sigma / m_radius) ** 2 + 1.0))
    # distr = ba.DistributionLogNormal(m_radius, scale_param)
    particle = ba.Particle(particle_material, ba.FormFactorFullSphere(m_radius))

    sigma_factor = 3.0
    par_distr = ba.ParameterDistribution(
        "/Particle/FullSphere/Radius", distr, m_nparticles, sigma_factor)
    part_coll = ba.ParticleDistribution(particle, par_distr)
    layout.addParticle(part_coll, 1.0, ba.kvector_t(0, 0, -average_layer_thickness+10))

    layout.setTotalParticleSurfaceDensity(m_diffuse_surface_density)

    return layout


def create_sample(wavelength):
    """
    Creates multilayer.
    """
    m_air_material = get_air(wavelength)
    m_substrate_material = get_si(wavelength)
    m_particle_material = get_iron_oxide(wavelength)
    m_average_layer_thickness = 1000*nm
    m_roughness = 1.0*nm

    multi_layer = ba.MultiLayer()

    air_layer = ba.Layer(m_air_material)
    avg_layer = ba.Layer(m_air_material, m_average_layer_thickness)
    meso_layout = create_mesocrystal_layout(m_particle_material, m_average_layer_thickness)
    avg_layer.addLayout(meso_layout)
    diffuse_layout = create_diffuse_layout(m_particle_material, m_average_layer_thickness)
    avg_layer.addLayout(diffuse_layout)

    substrate_layer = ba.Layer(m_substrate_material)
    roughness = ba.LayerRoughness(m_roughness, 0.3, 500.0 * nm)

    multi_layer.addLayer(air_layer)
    multi_layer.addLayer(avg_layer)
    multi_layer.addLayerWithTopRoughness(substrate_layer, roughness)

    return multi_layer


def create_simulation():
    """
    Creates GISAS simulation.
    """
    m_inclination_angle = 0.4 * deg
    m_beam_wavelength = 0.177 * nm
    m_beam_intensity = 6.1e+12
    m_constant_background = 200.0

    print("Starting")
    simulation = ba.GISASSimulation()
    simulation.setTerminalProgressMonitor()
    simulation.setDetector(create_detector())
    simulation.setBeamParameters(m_beam_wavelength, m_inclination_angle, 0.0)
    simulation.setBeamIntensity(m_beam_intensity)
    simulation.setRegionOfInterest(30.0, 21.0, 65.0, 58.0)
    simulation.getOptions().setUseAvgMaterials(True)
    simulation.setBackground(ba.ConstantBackground(m_constant_background))
    simulation.setDetectorResolutionFunction(ba.ResolutionFunction2DGaussian(m_pixel_size*1.5, m_pixel_size*2.0))
    simulation.setSample(create_sample(m_beam_wavelength))
    return simulation


def run_simulation():
    simulation = create_simulation()
    simulation.runSimulation()
    return simulation.result()


if __name__ == '__main__':
    result = run_simulation()
    print("Completed successfully")
    ba.plot_simulation_result(result, intensity_min=1e+04, intensity_max=1e+08, cmap='jet', aspect='auto')
