"""
Creates ready to run simulation.
"""
import time
import bornagain as ba
from bornagain import deg, nm, angstrom
from .detector_builder import DetectorBuilder
from .create_sample_builder import create_sample_builder


class SimulationBuilder:
    def __init__(self, exp_config, sample_config):
        self.m_beam_intensity = exp_config["beam_intensity"]
        self.m_beam_wavelength = exp_config["beam_wavelength"]*nm
        self.m_inclination_angle = exp_config["inclination_angle"]
        self.m_integration = exp_config["integration"]
        self.m_resolution_sigma_factor = exp_config["det_sigma_factor"]
        self.m_time_spend = 0
        self.m_sample_builder = create_sample_builder(sample_config)
        self.m_experimental_data = None
        self.m_detector_builder = DetectorBuilder(exp_config)

    def detector_resolution_sigma(self):
        return self.m_detector_builder.pixel_size()*self.m_resolution_sigma_factor

    def build_simulation(self):
        result = ba.GISASSimulation()
        result.setTerminalProgressMonitor()
        result.getOptions().setMonteCarloIntegration(self.m_integration, 50)

        result.setDetector(self.m_detector_builder.create_detector())
        result.setBeamParameters(self.m_beam_wavelength, self.m_inclination_angle*deg, 0.0)
        result.setBeamIntensity(self.m_beam_intensity)
        result.setSample(self.m_sample_builder.build_sample(self.m_beam_wavelength))
        result.setRegionOfInterest(30.0, 21.0, 65.0, 58.0)  # basic
        # result.setRegionOfInterest(30.0, 21.0, 50.0, 43.0)  # smaller
        # result.setRegionOfInterest(41.0, 26.0, 47.0, 34.0)  # singlepeak
        result.getOptions().setUseAvgMaterials(True)
        # result.setBackground(ba.PoissonNoiseBackground())
        result.setBackground(ba.ConstantBackground(200.0))

        result.setDetectorResolutionFunction(ba.ResolutionFunction2DGaussian(self.detector_resolution_sigma(), self.detector_resolution_sigma()*1.7))

        self.m_detector_builder.apply_masks(result)

        # wavelength_distr = ba.DistributionLogNormal(self.m_beam_wavelength, self.m_beam_wavelength/50)
        # result.addParameterDistribution("*/Beam/Wavelength", wavelength_distr, 10)
        #
        # alpha_distr = ba.DistributionGaussian(self.m_inclination_angle*deg, self.m_inclination_angle*deg/20.)
        # result.addParameterDistribution("*/Beam/InclinationAngle", alpha_distr, 10)

        data = ba.IHistogram.createFrom("../data/004_230_P144_im_full.int.gz").array()
        self.m_experimental_data = ba.ConvertData(result, data)

        return result

    def run_simulation(self):
        simulation = self.build_simulation()
        start = time.time()
        print("Starting")
        simulation.runSimulation()
        self.m_time_spend = time.time() - start
        print("\nDone in {:0} sec".format(self.m_time_spend))
        return simulation.result()

    def experimentalData(self):
        """
        Returns experimental data in same units as simulated data.
        """
        return self.m_experimental_data
