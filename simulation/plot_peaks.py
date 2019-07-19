"""
Test plotting of peaks
"""
from matplotlib import pyplot as plt
import bornagain as ba
from core.simulation_builder import SimulationBuilder
from core.meso_utils import load_setup

def plot_peaks(hist):
    peaks = ba.FindPeaks(hist, 3, "nomarkov", 1e-03)
    xpeaks = [peak[0] for peak in peaks]
    ypeaks = [peak[1] for peak in peaks]
    print(peaks)
    # print("xpeaks:", xpeaks)
    # print("ypeaks:", ypeaks)
    print("xpeaks=[", ', '.join('{:4.2f}'.format(k) for k in xpeaks), "]")
    print("ypeaks=[", ', '.join('{:4.2f}'.format(k) for k in ypeaks), "]")
    ba.plot_histogram(hist, cmap="jet", zmin=1e+02, zmax=1e+07)
    plt.plot(xpeaks, ypeaks, linestyle='None', marker='x', color='white', markersize=10)



if __name__ == '__main__':
    units = ba.AxesUnits.MM

    exp_config = load_setup("exp_config.json", "exp1")
    sample_config = load_setup("sample_config.json", "randommeso")
    builder = SimulationBuilder(exp_config, sample_config)
    builder.build_simulation()
    hist = builder.experimentalData().histogram2d(units)
    hist.save("single_peak.int")
    plot_peaks(hist)
    plt.show()

