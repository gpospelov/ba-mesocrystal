"""
Sample builder (August, 2019).
Can work with arbitrary number of particle layouts.
"""
import bornagain as ba
from bornagain import nm, angstrom
from .create_layout_factory import create_layout_factory
from periodictable.xsf import xray_energy, xray_sld_from_atoms, xray_sld
from periodictable.xsf import index_of_refraction, mirror_reflectivity
import periodictable as pt


class SampleBuilderVer3:
    """
    Meso crystal sample builder
    """
    def __init__(self, config):
        self.m_roughness = config["roughness"]
        self.m_average_layer_thickness = config["average_layer_thickness"]

        self.m_air_material = None
        self.m_substrate_material = None
        self.m_particle_material = None

        self.m_layouts = list()
        for layout_name in config["layouts"]:
            self.m_layouts.append(create_layout_factory(layout_name, config))

    def get_air(self, wavelength):
        return ba.MaterialBySLD("air", 0.0, 0.0)

    def get_si(self, wavelength):
        si = pt.formula("Si")
        dens = pt.Si.density
        rho, mu = pt.xray_sld(si, density=pt.Si.density, wavelength=wavelength / angstrom)
        rho *= 1e-6
        mu *= 1e-6
        print("MaterialLibrary > wavelength:{0} formula:{1} density:{2} rho:{3} mu:{4}".format(wavelength, si,
                                                                                               dens, rho, mu))
        return ba.MaterialBySLD("si", rho, mu)

    def get_iron_oxide(self, wavelength):
        oxide = pt.formula("Fe2O3")
        dens = 5.24
        rho, mu = pt.xray_sld(oxide, density=dens, wavelength=wavelength / angstrom)
        rho *= 1e-6
        mu *= 1e-6
        print("MaterialLibrary > wavelength:{0} formula:{1} density:{2} rho:{3} mu:{4}".format(wavelength, oxide,
                                                                                               dens, rho, mu))
        return ba.MaterialBySLD("Fe203", rho, mu)

    def init_materials(self, wavelength):
        self.m_air_material = self.get_air(wavelength)
        self.m_substrate_material = self.get_si(wavelength)
        self.m_particle_material = self.get_iron_oxide(wavelength)

    def build_sample(self, wavelength=None):
        """
        Constructs multilayer with collection of mesocrystals.
        """
        self.init_materials(wavelength)

        multi_layer = ba.MultiLayer()
        air_layer = ba.Layer(self.m_air_material)
        avg_layer = ba.Layer(self.m_air_material, self.m_average_layer_thickness)
        substrate_layer = ba.Layer(self.m_substrate_material)

        for layout_factory in self.m_layouts:
            avg_layer.addLayout(layout_factory.create_layout(self.m_particle_material))

        roughness = ba.LayerRoughness(self.m_roughness, 0.3, 500.0*nm)
        multi_layer.addLayer(air_layer)
        multi_layer.addLayer(avg_layer)
        multi_layer.addLayerWithTopRoughness(substrate_layer, roughness)

        return multi_layer
