"""
Base class for skymodel analysis

"""

import os, sys, pickle, glob, zipfile, time
import numpy as np
import pylab as plt
from mpl_toolkits.axes_grid import axes_grid, axes_size, Divider, make_axes_locatable

from . import _html
from . _html import HTMLindex


class FloatFormat(): #simple formatting functor for to_html!
    def __init__(self, n): self.fmt = '%%.%df' % n
    def __call__(self, x): return self.fmt % x
    
def html_table( df, heading={}, href=True, **kw):
    """ utility to reformat a pandas-generated html table
    df : a DataFrame
    heading : dict
        keys are column names
        items - comma-delimited string, first field the title to use instead of the column name, rest an explanation
    href : bool
         if True, replace index names with link to sedrec
    """
    t = df.to_html(**kw)
    t = t.replace('<td><strong>', '<td class="index"><strong>') #what pandas generates for index column
    for h, item in heading.items():
        try:
            newhead,title=item.split(',',1)
        except: 
            print '***fail to parse html_table data:',item
            continue
        t = t.replace('>'+h+'<', ' title="%s">%s<'% (title, newhead if newhead!='' else h))
    if href:
       for n in df.index:
           fn = 'sedfig/' + n.replace(' ','_').replace('+','p') + '_sed.png'
           if not os.path.exists(fn): continue
           t = t.replace('>'+n+'<', '><a href="../../%s">%s<' %(fn,n))
    return t
    
    
class OutputTee(object):
    """ capture a copy of stdout to a local string
    """
    def __init__(self):
        self.logstream = '' 
        self.stdout = sys.stdout
        sys.stdout = self
    def write(self, stuff):
        self.logstream += stuff
        self.stdout.write(stuff)
    def close(self):
        sys.stdout =self.stdout
    def flush(self):
        pass
    def set_parent(self, parent):
        self.stdout.set_parent(parent) #needed??
       
       
class AnalysisBase(object):
    """ basic class to handle data for diagnostics, collect code to make plots
    """
    def __init__(self, skymodel_dir='.', **kwargs):
        """ skymodel_dir: string
            points to a directory containing a config.txt file, and perhaps other files
            
            Creates a folder 'plots' if it does not exist, 
        """
        self.skymodel_dir = os.path.expandvars(skymodel_dir)
        if skymodel_dir != '.': os.chdir(self.skymodel_dir)
        self.skymodel = os.path.split(os.getcwd())[-1]
        self.setup(**kwargs)
        if not os.path.exists('plots'):
            os.mkdir('plots')
            print 'created folder "plots"'
        if hasattr(self, 'plotfolder'):
            self.plotfolder = os.path.join('plots', self.plotfolder)
            if not os.path.exists(self.plotfolder): os.makedirs(self.plotfolder)
        else:
            raise Exception('Subclass of AnalysisBase did not create a "plotfolder" variable')
            
        #create needed folder
        if not os.path.exists('needed'):
            os.mkdir('needed')
            print 'created folder "needed"'

    def setup(self, **kwargs):
        assert False, 'Base class not implemented'
        
    def startlog(self):
        """Start a log stream: all output is also directed to a string variable"""
        self.outtee= OutputTee()
        
    def stoplog(self): 
        """Stop the log, return the string"""
        try:   
            self.outtee.close()
            return self.outtee.logstream
        except:
            print 'Did not start the log?'
            return 'No log stream'

    def describe(self):
        return 'no description'
 
    def subplot_array( self, hsize, vsize=(1.0,), figsize=(10,10)):
        """ Use the axes_divider module to make a single row of plots
        hsize : list of floats
            horizontal spacing: alternates Scaled for plot, Fixed for between plots
        vsize : list of floats
            vertical spacing
            
        ref:   http://matplotlib.org/mpl_toolkits/axes_grid/users/axes_divider.html
        """
        nx = (len(hsize)+1)/2
        ny = (len(vsize)+1)/2
        fig, axx = plt.subplots(ny,nx,squeeze=False, figsize=figsize) # just to make the axes, will move them
        sizer = lambda x,i: axes_size.Scaled(x) if i%2==0 else axes_size.Fixed(x)
        horiz = [ sizer(h,i) for i,h in enumerate(hsize) ]
        vert  = [ sizer(v,i) for i,v in enumerate(vsize) ]
        divider = Divider(fig, (0.1, 0.1, 0.8, 0.8), horiz, vert, aspect=False)
        for i,ax in enumerate(axx.flatten()):
            iy = i//nx; ix = i%nx
            ax.set_axes_locator(divider.new_locator(nx=2*ix, ny=2*iy))
        return fig, axx
        
    def savefigure(self, name, func=None, title=None, caption=None, section='', **kwargs):
        """ save a figure.
        name : string
            If name is the name of a function in the class, optionally define 
                the title as the first line, the caption the following lines
        func : executable function, or None
            if not None, run the func, use it to get docs
            If func creates a figure, it must return it
        Note that the docstring may have %(xxx)s, which will be replaced by attribute xxx.
        """
        if func is not None:
            fname = func.__name__
            try:
                fig=func(**kwargs)
            except Exception, msg:
                print '*** Failed to run function %s: "%s"' % (fname, msg)
                return '<h3>%s %s</h3> Failed to run function %s: "%s"' % (section, title, fname, msg)
        else: fname = name
        if hasattr(self, fname):
            try:
                doclines = ((eval('self.%s' % fname).__doc__%self.__dict__).split('\n'))
                doclines.append('')
                if caption is None:   caption = '\n<p>'+'\n'.join(doclines[1:])+'</p>\n'
                if title is None:     title = doclines[0]
            except Exception, msg:
                print '*** docstring processing problem: %s' % msg
        localfile = '%s_%s.png'%(name, self.skymodel.replace('/','_'))
        savefile = os.path.join(self.plotfolder,localfile)
        if title is None: title = name.replace('_', ' ')
        htmldoc=None
        if fig is not None:
            fig.text(0.02, 0.02, self.skymodel, fontsize=8)
            savefig_kw=dict(dpi=60, bbox_inches='tight', bbox_extra_artists=fig.texts, pad_inches=0.5) 
            plt.savefig(savefile, **savefig_kw)
            print 'saved plot to %s' % savefile
            htmldoc = '<h3>%s %s</h3> <img src="%s" />\n <br> %s '% (section, title, localfile, caption if caption is not None else '')
        elif caption is not None:
            htmldoc = '<h3>%s %s</h3>\n <br>  %s' % (section, title, caption )
        if htmldoc is not None:
            open(savefile.replace('.png','.html'),'w').write(htmldoc )
        print 'saved html doc to %s' % os.path.join(os.getcwd(),savefile.replace('.png','.html'))
        return htmldoc

    def runfigures(self, functions, names=None,  **kwargs):
        """ 
        run the functions, create a web page containing them

        functions: list of bound functions 
        names: optional set of names to use instad of function names
        
        Expect to be called from all_plots, get a summary from its docstring if present, or the class docstring
        """
        if names is None:
            names=[None]*len(functions)
        title = self.skymodel +'-'+self.__class__.__name__
        htmldoc = '<head>'+ _html.style + '\n <title>%s</title>\n' % title
        htmldoc +=' <script>document.title="%s"</script>\n</head>\n' % title # this to override SLAC Decorator
        htmldoc +='<body><h2>%(header)s</h2>'
 
        docstring = self.all_plots.__doc__
        if docstring is None: docstring = self.__doc__
        if docstring is not None: htmldoc+=docstring
        section = 0
        for function, name in zip(functions,names):
            section +=1
            fname = name if name is not None else function.__name__
            fig = self.savefigure(fname, function, section='%d.'%section, **kwargs)
            if fig is not None:
                htmldoc+='\n'+ fig
        htmldoc+= '\n<hr>\nPage generated %4d-%02d-%02d %02d:%02d:%02d on %s by %s'\
                % (tuple(time.localtime()[:6])+
                 (os.environ.get('HOSTNAME',os.environ.get('COMPUTERNAME','?')),
                  os.environ.get('USER',os.environ.get('USERNAME','?'))))
        htmldoc+='\n</body>'
        t = os.getcwd().split(os.path.sep)[-3:]
        m = '<a href="../plot_index.html?skipDecoration">%s</a>' % t[-1] # model name has uplink
        r = '<a href="../../../analysis-doc?skipDecoration">%s</a>' % t[-2] # to group of models 
        self.header='/'.join([r, m, os.path.split(self.plotfolder)[-1]])
        text= htmldoc
        try:
            text = htmldoc%self.__dict__
        except KeyError, msg:
            print '*** failed filling %s:%s' % (title, msg)
        except TypeError:
            pass # ignore if % in text
        open(os.path.join(self.plotfolder,'index.html'), 'w').write(text)
        print 'saved html doc to %s' %os.path.join(self.plotfolder,'index.html')