"""
New sample builder (2018).
Relies on json, have diffuse block.
"""
import numpy
import bornagain as ba
from bornagain import nm
from .create_mesocrystal_factory import create_mesocrystal_factory


class SampleBuilderVer1:
    """
    Meso crystal sample builder
    """
    def __init__(self, config):
        self.m_roughness = config["roughness"]
        self.m_surface_filling_ratio = config["surface_filling_ratio"]
        self.m_average_layer_thickness = config["average_layer_thickness"]
        self.m_meso_elevation = config["meso_elevation"]

        self.m_air_material = None
        self.m_substrate_material = None
        self.m_average_layer_material = None
        self.m_adapted_particle_material = None

        self.m_meso_factory = create_mesocrystal_factory(config)

    def init_materials(self):
        self.m_air_material = ba.HomogeneousMaterial("Air", 0.0, 0.0)
        self.m_substrate_material = ba.HomogeneousMaterial("Substrate", 7.57e-6, 1.73e-7)

        n_particle = complex(1.0-2.84e-5, 4.7e-7)
        avg_n_squared_meso = 0.7886*n_particle**2 + 0.2114
        n_avg = numpy.sqrt(self.m_surface_filling_ratio*avg_n_squared_meso + 1.0 - self.m_surface_filling_ratio)
        n_particle_adapted = numpy.sqrt(n_avg**2 + n_particle**2 - 1.0)

        self.m_adapted_particle_material = ba.HomogeneousMaterial("nanoparticle", n_particle_adapted)
        self.m_average_layer_material = ba.HomogeneousMaterial("AverageLayer", n_avg)

    def create_layout(self):
        """
        Creates particle layout and populates it with the collection of mesocrystals.
        """
        layout = ba.ParticleLayout()

        mesocrystals = self.m_meso_factory.build_mesocrystals(self.m_adapted_particle_material)
        for meso in mesocrystals:
            layout.addParticle(meso, 1.0, ba.kvector_t(0, 0, -self.m_average_layer_thickness+self.m_meso_elevation))

        layout.setTotalParticleSurfaceDensity(self.m_meso_factory.surface_density())

        return layout

    def create_diffuse_layout(self):
        layout = ba.ParticleLayout()
        radius = 5.0
        nparticles = 100
        sigma = 0.3 * radius
        gauss_distr = ba.DistributionGaussian(radius, sigma)

        particle = ba.Particle(self.m_adapted_particle_material, ba.FormFactorFullSphere(radius))

        sigma_factor = 2.0
        par_distr = ba.ParameterDistribution(
            "/Particle/FullSphere/Radius", gauss_distr, nparticles, sigma_factor)
        part_coll = ba.ParticleDistribution(particle, par_distr)
        layout.addParticle(part_coll, 1.0, ba.kvector_t(0, 0, -self.m_average_layer_thickness+self.m_meso_elevation))

        layout.setTotalParticleSurfaceDensity(0.005)
        return layout

    def build_sample(self, wavelength=None):
        """
        Constructs multilayer with collection of mesocrystals.
        """
        self.init_materials()

        multi_layer = ba.MultiLayer()
        air_layer = ba.Layer(self.m_air_material)

        avg_layer = ba.Layer(self.m_average_layer_material,
                             self.m_average_layer_thickness)


        layout = self.create_layout()

        avg_layer.addLayout(layout)
        avg_layer.addLayout(self.create_diffuse_layout())

        substrate_layer = ba.Layer(self.m_substrate_material)

        roughness = ba.LayerRoughness(self.m_roughness, 0.3, 500.0*nm)

        multi_layer.addLayer(air_layer)
        multi_layer.addLayer(avg_layer)
        multi_layer.addLayerWithTopRoughness(substrate_layer, roughness)

        return multi_layer

