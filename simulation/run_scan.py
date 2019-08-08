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


def single_shot(exp_config, sample_config, report_manager):
    report_manager.m_title = "Rotated factory"
    run_single(exp_config, sample_config, report_manager)


def run_scan(exp_config, sample_config, report_manager):
    # scan_rotation_z(exp_config, sample_config, report_manager)
    # scan_tilt(exp_config, sample_config, report_manager)
    # scan_lattice_length_a(exp_config, sample_config, report_manager)
    # scan_lattice_length_c(exp_config, sample_config, report_manager)
    # scan_particle_pos_sigma(exp_config, sample_config, report_manager)
    scan_meso_count(exp_config, sample_config, report_manager)
    # single_shot(exp_config, sample_config, report_manager)


def main():
    output = os.path.abspath(os.path.join(os.path.split(__file__)[0], "../output"))
    report_manager = ReportManager(output)

    exp_config = load_setup("exp_config.json", "exp1")
    sample_config = load_setup("sample_config.json", "randommeso")

    run_scan(exp_config, sample_config, report_manager)

    report_manager.generate_pdf()
    print("Terminated successfully")


if __name__ == '__main__':
    main()

