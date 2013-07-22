# -*- coding: utf-8 -*-
"""
Manage the Web page generation
$Header:$
"""
import os, glob
import pandas as pd



class HTMLindex():
    """ Manage the web browser pages
    """
    #Attempted to use %(needed_files)s under href for below, however if it is in style= then it does not grab from the function __init__ below.
    style="""
<script type="text/javascript" src="needed/simpletreemenu.js">

/***********************************************
* Simple Tree Menu- © Dynamic Drive DHTML code library (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit Dynamic Drive at http://www.dynamicdrive.com/ for full source code
***********************************************/

</script>

<link rel="stylesheet" type="text/css" href="needed\simpletree.css" /> 

</head>
<body>

"""
#title is required for to define the document - used in search engines etc.

#<script> function load(){ parent.content.location.href='%(model_summary)s';} </script>
    #</head>
    #<body onload="load()">
    menu_header="""<!DOCTYPE html>
<html> 
<head> 
<title>%(model)s index</title> %(style)s 
    
<h2><a href="%(upper_link)s">%(upper)s</a>%(model)s</h2> 

<a href="javascript:ddtreemenu.flatten('treemenu1', 'expand')">Expand All</a> | <a href="javascript:ddtreemenu.flatten('treemenu1', 'contract')">Contract All</a>

<ul id="treemenu1" class="treeview">



"""
 

    def __init__(self, folder='plots/*'):
        self.style = HTMLindex.style
    
        w= glob.glob(folder)
        if len(w)==0: 
            print 'Did not find any plot folders under %s' % folder
        z = dict( zip(w, [glob.glob(a+'/*.htm*') for a in w] ) )
        w = os.getcwd().split(os.path.sep)
        self.upper = w[-2]+'/'
        self.upper_link = '../'#This updates the link (analysis-doc) in the main webbrowser.
        self.model = w[-1] #'/'.join(w[-2:])
        self.model_summary='plots/config/index.html'
        self.needed_files='needed'
        s= HTMLindex.menu_header % self.__dict__
       
        
        def parse_item(x): ##This functions make all the hyperlinks under plots\config, and plots\demo respectively.
            head, tail =os.path.split(x)
            name = os.path.splitext(tail)[0]
            n = name.find('_uw')
            #note the special qualifier for use with the SLAC decorator
            
                    
            if x==v[len(v)-1]:
                return '<li><a href="%s">%s</a></li></ul></li>' % (x,name[:n])
            else:
                return '<li><a href="%s">%s</a></li>' % (x,name[:n])
 

        for k in sorted(z.keys()):
            v = z[k]
            if len(v)==0: continue
            index = '%s/index.html'% k
            if index in v:
                v.remove(index)
                #s += '\n<h4><a href="%s?skipDecoration" target="content">%s</a></h4>'% 'hi',k[6:] #Why does this never get called?
            else:
                s += '<li><a href="javascript:void 0" onclick="TreeMenu.toggle(this)">%s</a><ul>'% k[6:]
            
            s += '\n\t' + '\n\t'.join(map(parse_item, v))  
            #pass
        self.ul = s + '\n <script type="text/javascript">  ddtreemenu.createTree("treemenu1", true) / ddtreemenu.createTree("treemenu2", false) </script> </body>' # s + '</p>\n</body>'
        self.make_config_link()
        print s
    def _repr_html_(self):    
        return self.ul
    
    def make_config_link(self):
        html = """<head>%s</head><body><h2><a href="../../plot_index.html">%s</a> - configuration and analysis history files!!</h2>
        """ %( self.style,self.model) 
        for filename in ('config.txt', 'dataset.txt', 'converge.txt', 'summary_log.txt'):
            if not os.path.exists(filename): continue
            html += '<h4>%s</h4>\n<pre>%s</pre>' % (filename, open(filename).read())
        html += '\n</body>'
        if not os.path.exists('plots/config'): os.makedirs('plots/config') #plots/config
        open('plots/config/index.html','w').write(html)
        print 'wrote plots/config/index.html'
        
    def create_menu(self, filename='plot_index.html'):
        ###summary = open(filename, 'w')
        open(filename, 'w').write(self.ul)
        print 'wrote menu %s' % os.path.join(os.getcwd(),filename)
        # make separate menu for the Decorator browser
        t = self.ul.replace('plots/', '')
        open('plots/index.html', 'w').write(t)
        print 'wrote menu %s' %os.path.join(os.getcwd(), 'plots/index.html')