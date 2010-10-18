#!/usr/bin/env python
# encoding: utf-8;

#
# Import the with statement from The Future (!) to ensure compatability
# with Python 2.5.
#
from __future__ import with_statement

import os
import sys
import optparse
from markdown import markdown

from pygments import lex
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.utils import ClassNotFound

PYGOCCO_VERSION = 0.1

for l in  pygments.lex( '"""\nomg\n"""\n\n# omg?\n\ndef omg:\n    omg() # wtf', pygments.lexers.get_lexer_for_filename( "omg.py" ) ):
    ...     pprint.pprint( l )

# Helper Functions
# ----------------

# Replicate `mkdir -p` functionality
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

#
# Generate documentation for a source file by reading it in, splitting it
# into comment/code sections, highlighting them for the appropriate
# language, and merging them into an HTML template.
#
def generate_documentation( filename, options ):
    with open( filename, "rb" ) as f:
        sections = parse_sections( filanem=filename, text=f.read(), language=options.language )

# In order to parse sections, we'll need a lexer to tokenize the text.
def generate_lexer( filename, text, language ):
    #
    # If `language` is specified, use it to generate a lexer
    #
    lexer = None
    if language is not None:
        try:
            lexer = get_lexer_by_name( language )
        except pygments.util.ClassNotFound:
            sys.stderr.write( "ERROR: The specified language `%s` doesn't exist as a Pygments lexer.  Falling back to hueristics." % language )

    #
    # Determine which lexer best fits the file.  First, check whether the
    # filename clearly identifies a language (via Pygments'
    # `get_lexer_for_filename`):
    #
    if lexer is None: 
        try:
            lexer = get_lexer_for_filename( filename )
    #
    # If the filename doesn't help (because it's an extensionless shell
    # script, for instance), run `pygments.lexers.guess_lexer` to brute
    # force a lexer.
    #
        except pygments.util.ClassNotFound:
            try:
                lexer = guess_lexer( text )
            except pygments.util.ClassNotFound:
                sys.stderr.write( "ERROR: Could not find an appropriate lexer for `%s`.  Please use the `-l` flag to force a language selection." )
    # Throw the lexer back over the wall...
    return lexer


#
# With the ability to tokenize text, we'll move on to splitting the text
# into sections.  Given a filename, text, and an optional language, we'll
# first generate a lexer, and then split text into an array of dictionaries
# in the form:
#
#     [
#         {
#             "docs_text":  ...,
#             "docs_html":  ...,
#             "code_text":  ...,
#             "code_html":  ...,
#             "num":        ...
#         },
#         ...
#     ]
#
# 
#
def parse_sections( filename, text, language=None ):
    lexer = generate_lexer( filename=filename, text=text, language=language )

    if lexer:
        tokens = lex( text, lexer )

#
# Define a `main` function that we'll call when the file is executed.  Here,
# we'll use `OptionParser` to deal with the difficulty of extracting useful
# information from `argv`.
#
def main():
    #
    # Define the `OptionParser` object
    #
    # *   `-o`, `--output`: Defines the directory into which output files
    #     will be rendered.  _Defaults to `[CWD]/docs`_.
    #
    parser = optparse.OptionParser( usage="Usage: %prog [options] [source files]",
                                    version="%%prog %s" % PYGOCCO_VERSION )
    
    parser.add_option(   "-o", "--output",
                        action="store",
                        dest="output_root",
                        default=os.path.join( os.getcwd(), "docs" ),
                        metavar="DIR",
                        help="Directory into which rendered documentation " +
                             "ought be written (defaults to a `docs` " +
                             "subdirectory within the current working " +
                             "directory)" )

    opts, sources = parser.parse_args()

    #
    # If no source files were specified, throw an error and exit (handled
    # entirely by `OptionParser`
    #
    if not sources:
        parser.error( "Please provide source files to be parsed" )
    #
    # Else, we've got something to work with, so ensure that the output
    # directory exists, and then loop through the provided list of source
    # files, running each in turn through `generate_documentation`
    #
    else: 
        mkdir_p( opts.output_root )
        for f in sources:
            generate_documentation( f, opts ) 

if __name__ == "__main__":
    sys.exit( main() )
