import bornagain as ba
from matplotlib import pyplot as plt
from core.simulation_builder import SimulationBuilder
from core.meso_utils import load_setup
import json
import matplotlib.gridspec as gridspec


def plot_simulation(result):
    fig = plt.figure(figsize=(12, 8))
    ba.plot_colormap(result, zmin=100, zmax=1e+07, units=ba.AxesUnits.QSPACE, cmap="jet")
    fig.tight_layout()
    return fig


def plot_colormap(data, zmin=1e+03, zmax=1e+07, units=ba.AxesUnits.MM, zlabel="", cmap="jet", aspect="auto"):
    ba.plot_colormap(data, zmin=zmin, zmax=zmax, units=units, zlabel=zlabel, cmap=cmap, aspect=aspect)


def plot_vertical_slices(data, xpeaks):
    for x in xpeaks:
        plt.plot([x, x], [data.histogram2d().getYmin(), data.histogram2d().getYmax()],
             color='gray', linestyle='-', linewidth=1)


def plot_alongx(exp_data, sim_result, units=ba.AxesUnits.MM):
    fig = plt.figure(figsize=(16, 14))
    gs1 = gridspec.GridSpec(1, 2)
    gs1.update(left=0.05, right=1.0, bottom=0.525, top=0.95, wspace=0.05)

    plt.subplot(gs1[0])
    plot_colormap(exp_data)

    plt.subplot(gs1[1])
    plot_colormap(sim_result)

    gs2 = gridspec.GridSpec(1, 1)
    gs2.update(left=0.05, right=0.95, bottom=0.05, top=0.455, wspace=0.05)
    ax = plt.subplot(gs2[0])
    exp_proj = exp_data.histogram2d(units).projectionX()
    plt.semilogy(exp_proj.getBinCenters(), exp_proj.getBinValues()+1, label=r'$\phi=0.0^{\circ}$')

    sim_proj = sim_result.histogram2d(units).projectionX()
    plt.semilogy(sim_proj.getBinCenters(), sim_proj.getBinValues()+1, label=r'$\phi=0.0^{\circ}$')

    plt.ylim(1e+03, 1e+09)

    ax.legend(['experiment', 'simulation'], facecolor='w')

    return fig


def plot_alongy(exp_data, sim_result, units=ba.AxesUnits.MM):
    xpeaks = [32.95, 43.8, 47.8, 57.5, 62.9]
    fig = plt.figure(figsize=(16, 14))
    gs1 = gridspec.GridSpec(1, 2)
    gs1.update(left=0.05, right=1.0, bottom=0.525, top=0.95, wspace=0.05)

    plt.subplot(gs1[0])
    plot_colormap(exp_data)
    plot_vertical_slices(exp_data, xpeaks)

    plt.subplot(gs1[1])
    plot_colormap(sim_result)
    plot_vertical_slices(sim_result, xpeaks)

    gs2 = gridspec.GridSpec(2, 3)
    gs2.update(left=0.05, right=0.95, bottom=0.05, top=0.455, wspace=0.1)

    for index, x in enumerate(xpeaks):
        ax = plt.subplot(gs2[index])
        xmin = x - 0.25
        xmax = x + 0.25
        exp_proj = exp_data.histogram2d(units).projectionY(xmin, xmax)
        plt.semilogy(exp_proj.getBinCenters(), exp_proj.getBinValues()+1, label=r'$\phi=0.0^{\circ}$')

        sim_proj = sim_result.histogram2d(units).projectionY(xmin, xmax)
        plt.semilogy(sim_proj.getBinCenters(), sim_proj.getBinValues()+1, label=r'$\phi=0.0^{\circ}$')
        plt.ylim(1e+03, 1e+07)

    return fig


def write_real_data_to_report(builder, report):
    plot_simulation(builder.experimentalData())
    report.write_report(slide_title="004_230_P144_im_full")


def run_single(exp_config, sample_config, report=None):
    builder = SimulationBuilder(exp_config, sample_config)
    print(json.dumps(sample_config, sort_keys=True, indent=2, separators=(',', ': ')))
    result = builder.run_simulation()
    figs = []
    # figs.append(plot_simulation(result))
    # figs.append(plot_alongx(builder.experimentalData(), result))
    figs.append(plot_alongy(builder.experimentalData(), result))

    if report:
        report.write_report(sample_config)
        for fig in figs:
            #report.add_page(json_config=config, mfig=figs)
            plt.close(fig)
    else:
        plt.show()


def main():
    exp_config = load_setup("exp_config.json", "exp1")
    sample_config = load_setup("sample_config.json", "rotmeso")

    run_single(exp_config, sample_config)
    print("Terminated successfully")


if __name__ == '__main__':
    main()


