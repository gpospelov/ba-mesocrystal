"""
Simplified mesocrystal simulation for demo purposes
"""
import bornagain as ba
from bornagain import deg, nm, angstrom
import math
import periodictable as pt

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
        self.m_meso_height = 200*nm
        self.m_meso_radius = 1000*nm
        self.m_sigma_lattice_length_a = 0.1*nm
        self.m_sigma_meso_height = 20*nm
        self.m_sigma_meso_radius = 20*nm
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
        ff_cyl = ba.FormFactorCylinder(self.m_meso_radius, self.m_meso_height)

        ff_meso = ba.FormFactorDecoratorDebyeWaller(ff_cyl, self.m_sigma_meso_height**2/2.0,
                                                    self.m_sigma_meso_radius**2/2.0)

        lattice = self.create_lattice(self.m_lattice_length_a,
                                      self.m_lattice_length_c)

        basis = self.create_basis(self.particle_material, lattice,
                                  self.m_nanoparticle_radius,
                                  self.m_sigma_nanoparticle_radius,
                                  self.m_nparticles)

        npc = ba.Crystal(basis, lattice)
        dw_factor = self.m_sigma_lattice_length_a*self.m_sigma_lattice_length_a/6.0
        npc.setDWFactor(dw_factor)
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


def create_layout(particle_material, average_layer_thickness):
    layout = ba.ParticleLayout()

    builder = MesoCrystalBuilder(particle_material)
    meso = builder.create_meso()
    meso_elevation = 50*nm
    layout.addParticle(meso, 1.0, ba.kvector_t(0, 0, -average_layer_thickness + meso_elevation))
    layout.setTotalParticleSurfaceDensity(1e-7)

    return layout
    pass


def create_sample(wavelength):
    m_air_material = get_air(wavelength)
    m_substrate_material = get_si(wavelength)
    m_particle_material = get_iron_oxide(wavelength)

    multi_layer = ba.MultiLayer()

    air_layer = ba.Layer(m_air_material)
    m_average_layer_thickness=1000
    avg_layer = ba.Layer(m_air_material, 1000*nm)
    layout = create_layout(m_particle_material, m_average_layer_thickness)
    avg_layer.addLayout(layout)
    substrate_layer = ba.Layer(m_substrate_material)
    roughness = ba.LayerRoughness(10.0, 0.3, 500.0 * nm)

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

    simulation = ba.GISASSimulation()
    simulation.setTerminalProgressMonitor()
    simulation.setDetector(create_detector())
    simulation.setBeamParameters(m_beam_wavelength, m_inclination_angle, 0.0)
    simulation.setBeamIntensity(m_beam_intensity)
    simulation.setRegionOfInterest(30.0, 21.0, 65.0, 58.0)
    simulation.getOptions().setUseAvgMaterials(True)
    simulation.setBackground(ba.ConstantBackground(200.0))
    simulation.setDetectorResolutionFunction(ba.ResolutionFunction2DGaussian(m_pixel_size, m_pixel_size))
    simulation.setSample(create_sample(m_beam_wavelength))
    return simulation


def run_simulation():
    simulation = create_simulation()
    simulation.runSimulation()
    return simulation.result()


if __name__ == '__main__':
    result = run_simulation()
    ba.plot_simulation_result(result, cmap='jet', aspect='auto')
