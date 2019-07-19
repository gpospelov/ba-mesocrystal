"""
Collection of builders to generate particle layouts generating diffuse scattering.
"""
import bornagain as ba
from .meso_utils import random_gate
import numpy.random as npr


class DiffuseBuilder:
    """
    Base class to generate particle layouts for diffuse scattering.
    """
    def __init__(self, config=None):
        self.m_config = config
        pass

    def create_layout(self, particle_material):
        return None


class RandomSizeParticles(DiffuseBuilder):
    """
    Creates particle layout with
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.m_average_layer_thickness = config["average_layer_thickness"]
        self.m_meso_elevation = config["meso_elevation"]

    def create_layout(self, particle_material):
        layout = ba.ParticleLayout()
        radius = 5.02
        nparticles = 100
        sigma = 0.3
        gauss_distr = ba.DistributionGaussian(radius, sigma)
        # scale_param = math.sqrt(math.log((sigma / radius) ** 2 + 1.0))
        # gauss_distr = ba.DistributionLogNormal(radius, scale_param)

        particle = ba.Particle(particle_material, ba.FormFactorFullSphere(radius))

        sigma_factor = 2.0
        par_distr = ba.ParameterDistribution(
            "/Particle/FullSphere/Radius", gauss_distr, nparticles, sigma_factor)
        part_coll = ba.ParticleDistribution(particle, par_distr)
        layout.addParticle(part_coll, 1.0, ba.kvector_t(0, 0, -self.m_average_layer_thickness))

        for i in range(0, 100):
            radius = npr.normal(5.0, 0.3)
            if radius < 4.0 or radius > 6.0:
                pass
            particle = ba.Particle(particle_material, ba.FormFactorFullSphere(radius))
            zbot = -self.m_average_layer_thickness
            pos = random_gate(zbot, zbot+50)
            layout.addParticle(particle, 0.05, ba.kvector_t(0, 0, pos))

        layout.setTotalParticleSurfaceDensity(0.002)
        return layout
