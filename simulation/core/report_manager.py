"""
Report generator for producing pdf files containing results of multiple
simulation runs.
"""
import os
import glob
import pylatex as pl
from pylatex.utils import NoEscape, bold, escape_latex
from pylatex import SmallText, FootnoteText, HugeText, Figure
from matplotlib import pyplot as plt
import json


def mono(s):
    return NoEscape(r'\texttt{' + s + '}')


def tiny(s):
    return NoEscape(r'\scriptsize{' + s + '}')


class ReportManager:
    def __init__(self, output_dir="../output", run_title="Experiment"):
        self.m_title = run_title
        self.m_run_prefix = "run"
        self.m_comment = "none"
        self.m_output_dir = output_dir
        self.m_output_index = 1

        geometry_options = {"margin": "0.5in"}
        self.m_doc = pl.Document("run-summary", document_options="landscape",
                                 geometry_options=geometry_options)

        self.prepare_output_dir()

    @staticmethod
    def make_dir(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def prepare_output_dir(self):
        self.make_dir(self.m_output_dir)
        files = glob.glob(self.m_output_dir+"/*")
        for f in files:
            os.remove(f)

    def output_png(self):
        """
        Returns file name to store pyplot figure.
        """
        return '{}/{}-{:03d}.png'.format(self.m_output_dir, self.m_run_prefix,
                                         self.m_output_index)

    def write_report(self, json_config=None, slide_title=None):
        """
        Append single page to PDF report (in memory).
        The page will contain a table with current list of parameters, and single
        image which is currently in pyplot.
        """
        doc = self.m_doc
        if slide_title:
            doc.append(slide_title)
        else:
            doc.append(self.m_title)

        doc.append(pl.VerticalSpace("2cm"))
        doc.append("\n")
        if json_config:
            self.create_json_minipage(json_config)
        self.create_figure_minipage()
        doc.append(pl.NewPage())
        self.m_output_index += 1

    def add_page(self, slide_title=None, json_config=None, mfig=None):
        self.m_doc.append(pl.NewPage())
        if slide_title:
            self.m_doc.append(slide_title)
        else:
            self.m_doc.append(self.m_title)
        if json_config:
            self.create_json_minipage(json_config)
        if mfig:
            with self.m_doc.create(pl.MiniPage(width=r"0.74\textwidth",
                                        height=r"0.25\textwidth",
                                        content_pos='t')) as page:
                with page.create(Figure(position='h!')) as plot:
                    plot.add_plot(width=NoEscape(r"0.99\textwidth"), dpi=300)

    def create_json_minipage(self, json_config):
        doc = self.m_doc
        with doc.create(pl.MiniPage(width=r"0.25\textwidth",
                                    height=r"0.25\textwidth",
                                    content_pos='t')) as page:
            str = json.dumps(json_config, sort_keys=False, indent=2, separators=(',', ': '))
            page.append(NoEscape(mono(tiny(escape_latex(str)))))

    def create_figure_minipage(self):
        """
        Create minipage with single figure which is currently in pyplot memory
        """
        doc = self.m_doc
        plt.savefig(self.output_png())
        with doc.create(pl.MiniPage(width=r"0.70\textwidth",
                                    height=r"0.25\textwidth",
                                    content_pos='t')) as page:
            page.append(pl.StandAloneGraphic(self.output_png(),
                image_options=NoEscape(r'width=0.90\textwidth')))
            doc.append("\n")

    def generate_pdf(self):
        """
        Write all pages in single pdf file.
        """
        filepath = os.path.join(self.m_output_dir, self.m_run_prefix+"-summary")
        self.m_doc.generate_pdf(clean_tex=False, filepath=filepath)

