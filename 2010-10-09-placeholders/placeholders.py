#!/usr/bin/env python
# encoding: utf-8;

from __future__ import with_statement

import os, sys, re, numpy
from lib.png import Writer
from optparse import OptionParser, OptionValueError

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
        steps   = Placeholder.FOREGROUND * 1.0
        start   = ( int( start[0:2], 16 ),  int( start[2:4], 16 ),  int( start[4:6], 16 ) )
        end     = ( int( end[0:2], 16 ),    int( end[2:4], 16 ),    int( end[4:6], 16 ) )
        step    = ( (end[0]-start[0])/steps, (end[1]-start[1])/steps, (end[2]-start[2])/steps )
        for rgb in range( 0, int( steps ) ):
            colors.append( (
                int( step[0]*rgb + start[0]),
                int( step[1]*rgb + start[1]),
                int( step[2]*rgb + start[2])))
        return colors

    def getColor( self, opacity ):
        return int( 255 * opacity )

    def write( self ):
        slope       = ( 1.0 * self.height ) / self.width
        pixels      = numpy.zeros( ( self.height, self.width ), dtype=int )

        #
        # Something similar to http://en.wikipedia.org/wiki/Xiaolin_Wu's_line_algorithm
        # but special cased, since I know the lines are mirrored thrice.
        #
        actualY = 0
        for leftX in range( 0, ( self.width / 2 ) + 1 ):
            # Precalculating.  Math!
            frac        = actualY - int( actualY ) 
            topColor    = self.getColor( 1 - frac )
            bottomColor = self.getColor( frac )
            topY        = int( actualY )
            bottomY     = self.height - topY - 1
            rightX      = self.width - leftX - 1

            # Actual Line (top-left)
            pixels[ topY,       leftX ]   = topColor
            pixels[ topY + 1,   leftX ]   = bottomColor

            # Horizontal Flip (top-right)
            pixels[ topY,       rightX ]  = topColor
            pixels[ topY + 1,   rightX ]  = bottomColor

            # Vertical Flip (bottom-left)
            pixels[ bottomY,     leftX ]  = topColor
            pixels[ bottomY - 1, leftX ]  = bottomColor

            # 180-degree Rotation
            pixels[ bottomY,     rightX ] = topColor
            pixels[ bottomY - 1, rightX ] = bottomColor
            
            # Increment `actualY`
            actualY += slope
            
            # Worry about the border (avoids another loop)
            if self.border:
                pixels[ 0,                leftX  ] = Placeholder.BACKGROUND
                pixels[ self.height - 1,  leftX  ] = Placeholder.BACKGROUND
                pixels[ 0,                rightX ] = Placeholder.BACKGROUND
                pixels[ self.height - 1,  rightX ] = Placeholder.BACKGROUND
                if leftX > 1:
                    pixels[ 1,                leftX  ] = Placeholder.FOREGROUND
                    pixels[ self.height - 2,  leftX  ] = Placeholder.FOREGROUND
                    pixels[ 1,                rightX ] = Placeholder.FOREGROUND
                    pixels[ self.height - 2,  rightX ] = Placeholder.FOREGROUND
                if leftX == 1:
                    for y in range( 1, self.height - 1 ):
                        pixels[ y,  leftX  ] = Placeholder.FOREGROUND
                        pixels[ y,  rightX ] = Placeholder.FOREGROUND

        with open( self.out, 'wb' ) as f:
            w = Writer( self.width, self.height, background=self.colors[0], palette=self.colors, bitdepth=8 )
            w.write( f, pixels )

def is_valid_hex( option, opt_str, value, parser ):
    try:
        r,g,b = ( int( value[0:2], 16 ),  int( value[2:4], 16 ),  int( value[4:6], 16 ) )
        if len(value) == 6 and min( r, g, b ) >= 0 and max( r, g, b ) <= 255:
            setattr(parser.values, option.dest, value )
            return
    except:
        pass
    raise OptionValueError(
            """
    `%s` expects a hex value in `RRGGBB` format (`000000` for black, and `FFFFFF` white).
    You entered `%s`""" % (opt_str, value))

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
                        action="callback",
                        type="string",
                        dest="background",
                        default="000000",
                        metavar="RRGGBB",
                        callback=is_valid_hex,
                        help="Background color in hex (`RRGGBB`) format")

    parser.add_option(  "--foreground",
                        action="callback",
                        type="string",
                        dest="foreground",
                        default="FFFFFF",
                        metavar="RRGGBB",
                        callback=is_valid_hex,
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
                        type=None,
                        default=True,
                        help="Suppress rendering of border around the placeholder image.")
    
    (options, args) = parser.parse_args()

    p = Placeholder( options )
    p.write()

if __name__ == "__main__":
    sys.exit( main() )
