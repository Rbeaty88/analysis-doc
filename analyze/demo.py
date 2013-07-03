"""
"""
from . import analysis_base
import pylab as plt
import numpy as np

class Demo(analysis_base.AnalysisBase):

    def setup(self, **kw):
        self.plotfolder='demo'

    def plot_1(self):
        """Test making a simple plot, with caption
        This is the caption: a power law
        """
        fig, ax = plt.subplots( figsize=(4,4))
        x = np.linspace(0,10, 100)
        ax.plot(x, x**2, '-')
        return fig


    def text(self):
        """Some text
        Yes!
        """
    def all_plots(self):
        self.runfigures([self.plot_1,self.text,])