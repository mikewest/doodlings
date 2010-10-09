#!/usr/bin/env python
# encoding: utf-8;

from __future__ import with_statement

import os, sys, re, numpy
from lib.png import Writer
from optparse import OptionParser

class Placeholder( object ):
    FOREGROUND = 255
    BACKGROUND = 0
    def __init__( self, settings ):
        self.width  = settings.width
        self.height = settings.height
        self.out    = settings.out
        self.border = settings.border
        self.colors = self.generateColors( settings.background, settings.foreground )

    def generateColors( self, start, end ):
        colors  = []
        steps   = 256.0
        start   = ( int( start[0:2], 16 ),  int( start[2:4], 16 ),  int( start[4:6], 16 ) )
        end     = ( int( end[0:2], 16 ),    int( end[2:4], 16 ),    int( end[4:6], 16 ) )
        step    = ( (end[0]-start[0])/steps, (end[1]-start[1])/steps, (end[2]-start[2])/steps )
        for rgb in range( 0, int( steps ) ):
            colors.append( (
                int( step[0]*rgb + start[0]),
                int( step[1]*rgb + start[1]),
                int( step[2]*rgb + start[2])))

        return colors

    def write( self ):
        slope       = ( 1.0 * self.width ) / self.height 
        intslope    = int( slope )
        colorstep   = int( 255 / slope )
        pixels      = numpy.zeros( ( self.height, self.width ), dtype=int )
        borderWidth = range( 1, self.width - 1 )

        print "Slope: %d, Colorstep: %d" % ( slope, colorstep )

        for y in range( 0, self.height ):
            point       = slope * y
            reflection  = self.width - point
            if self.border and ( y == 0 or y == self.height - 1 ):
                print "Writing the border for y = %d" % y 
                for x in borderWidth:
                    pixels[ y, x ] = Placeholder.BACKGROUND
            elif self.border and ( y == 1 or y == self.height - 2 ):
                print "Writing the border for y = %d" % y 
                for x in borderWidth:
                    pixels[ y, x ] = Placeholder.FOREGROUND
            else:
                for x in range( -intslope, intslope ):
                    color = int( colorstep * ( slope - x )  ) )
                    if ( x + point > 0 ):
                        print "Putting %d into (%d,%d - %d)" % ( color, y, x, point )
                        pixels[ y, x + point ] = 1
                    if ( x + reflection < self.width ):
                        pixels[ y, x + reflection ] = 1
                if self.border:
                    pixels[ y, 1 ]              = Placeholder.FOREGROUND
                    pixels[ y, self.width - 2 ] = Placeholder.FOREGROUND
        
        import pprint
        pprint.pprint( pixels )

        with open( self.out, 'wb' ) as f:
            w = Writer( self.width, self.height, background=self.colors[0], palette=self.colors, bitdepth=8 )
            w.write( f, pixels )

def main(argv=None):
    if argv is None:
        argv = sys.argv

    default_root = os.path.dirname(os.path.abspath(__file__))

    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 0.1")
    parser.add_option(  "--verbose",
                        action="store_true", dest="verbose_mode", default=False,
                        help="Verbose mode")
    
    parser.add_option(  "-o", "--output",
                        action="store",
                        dest="out", 
                        default=os.path.join(default_root, 'png.png'),
                        help="Output file")

    parser.add_option(  "--background",
                        action="store",
                        dest="background",
                        default="000000",
                        metavar="RRGGBB",
                        help="Background color in hex (`RRGGBB`) format")

    parser.add_option(  "--foreground",
                        action="store",
                        dest="foreground",
                        default="FFFFFF",
                        metavar="RRGGBB",
                        help="Foreground color in hex (`RRGGBB`) format")

    parser.add_option(  "--width",
                        action="store",
                        dest="width",
                        type="int",
                        default=100,
                        help="Width of placeholder")

    parser.add_option(  "--height",
                        action="store",
                        dest="height",
                        type="int",
                        default=100,
                        help="Height of placeholder")
    
    parser.add_option(  "--no-border",
                        action="store_false",
                        dest="border",
                        default=True,
                        help="Suppress rendering of border around the placeholder image.")
    
    (options, args) = parser.parse_args()

    p = Placeholder( options )
    p.write()

if __name__ == "__main__":
    import cProfile
    cProfile.run('main()', 'mainprof')
