"""
Run consecutive simulations to scan sample parameter influence.
"""
from core.report_manager import ReportManager
from core.meso_utils import load_setup
import numpy as np
from run_simulation import run_single
import os


def scan_rotation_z(exp_config, sample_config, report_manager):
    report_manager.m_title = "Single meso, rotation_z"
    # values = np.linspace(-5.0, 5.0, 51)
    # values = np.linspace(17.7-5.0, 17.7+5.0, 51)
    # values = np.linspace(28.5-5.0, 28.5+5.0, 51)
    # values = np.linspace(39.75-5.0, 39.75+5.0, 51)
    values = np.linspace(57.5-5.0, 57.5+5.0, 3)
    for value in values:
        sample_config["rotation_z"] = value
        run_single(exp_config, sample_config, report_manager)


def scan_tilt(exp_config, sample_config, report_manager):
    report_manager.m_title = "Single meso, lattice_length_a"
    for value in np.linspace(-0.5, 0.5, 11):
        sample_config["rotation_x"] = value
        run_single(exp_config, sample_config, report_manager)


def scan_lattice_length_a(exp_config, sample_config, report_manager):
    report_manager.m_title = "Single meso, lattice_length_a"
    for value in np.linspace(12.0, 13.0, 11):
        sample_config["lattice_length_a"] = value
        run_single(exp_config, sample_config, report_manager)


def scan_lattice_length_c(exp_config, sample_config, report_manager):
    report_manager.m_title = "Single meso, lattice_length_a"
    for value in np.linspace(29.0, 33.0, 20):
        sample_config["lattice_length_c"] = value
        run_single(exp_config, sample_config, report_manager)


def scan_particle_pos_sigma(exp_config, sample_config, report_manager):
    report_manager.m_title = "Single meso, particle_pos_sigma"
    for value in np.linspace(0.0, 2.0, 21):
        sample_config["particle_pos_sigma"] = value
        run_single(exp_config, sample_config, report_manager)


def scan_meso_count(exp_config, sample_config, report_manager):
    report_manager.m_title = "Random meso, scan on meso_count. Stability of rndm()."
    values = [100, 100, 200, 200, 500, 500, 1000, 1000]
    for value in values:
        sample_config["RandomMesoFactory"]["meso_count"] = value
        run_single(exp_config, sample_config, report_manager)


def scan_tilt_span(exp_config, sample_config, report_manager):
    report_manager.m_title = "RandomMeso, tilt_dtheta random span"
    for value in np.linspace(0.0, 5.0, 11):
        sample_config["RandomMesoFactory"]["tilt_dtheta"] = value
        run_single(exp_config, sample_config, report_manager)


def meso_size_scan(exp_config, sample_config, report_manager):
    report_manager.m_title = "RandomMeso, growing meso"
    height0, radius0 = 50.0, 100.0
    factor = (1, 2, 4, 6, 10, 20)
    for value in factor:
        height = height0*value
        radius = radius0*value
        volume_factor = 200.0*200.0*200.0/(radius*radius*height)
        print("xxx", height, radius, volume_factor)
        sample_config["meso_height"] = height
        sample_config["meso_radius"] = radius
        sample_config["RandomMesoFactory"]["layout_weight"] = 2e-2*2/value
        run_single(exp_config, sample_config, report_manager)


def scan_roughness(exp_config, sample_config, report_manager):
    report_manager.m_title = "RandomMeso, roughness scan"
    values = [0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0]
    for value in values:
        sample_config["roughness"] = value
        run_single(exp_config, sample_config, report_manager)


def single_shot(exp_config, sample_config, report_manager):
    report_manager.m_title = "TwoMeso factory"
    run_single(exp_config, sample_config, report_manager)


def run_scan(exp_config, sample_config, report_manager):
    # scan_rotation_z(exp_config, sample_config, report_manager)
    # scan_tilt(exp_config, sample_config, report_manager)
    # scan_lattice_length_a(exp_config, sample_config, report_manager)
    # scan_lattice_length_c(exp_config, sample_config, report_manager)
    # scan_particle_pos_sigma(exp_config, sample_config, report_manager)
    # scan_meso_count(exp_config, sample_config, report_manager)
    # scan_tilt_span(exp_config, sample_config, report_manager)
    # meso_size_scan(exp_config, sample_config, report_manager)
    # scan_roughness(exp_config, sample_config, report_manager)
    single_shot(exp_config, sample_config, report_manager)


def main():
    output = os.path.abspath(os.path.join(os.path.split(__file__)[0], "../output"))
    report_manager = ReportManager(output)

    exp_config = load_setup("exp_config.json", "exp1")
    sample_config = load_setup("sample_config.json", "rotmeso")

    run_scan(exp_config, sample_config, report_manager)

    report_manager.generate_pdf()
    print("Terminated successfully")


if __name__ == '__main__':
    main()

