'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

import os.path
import sys

fname = []
options = []
for a in sys.argv[1:]:
    if a.startswith('-'):
        options += [a]
    else:
        fname += [a]

if not fname and not options:
    print('No input file given.')
    sys.exit()
if fname:
    fname = fname[0]

from loader import get_code
from var import get_input, call_error, initialise_path, run, __version__

if options:
    if '-v' in options:
        del options[options.index('-v')]
        print('MDCL ' + __version__)
        sys.exit()
    if '--version' in options:
        del options[options.index('--version')]
        print('MDCL ' + __version__)
        sys.exit()
if options:
    print('Command line option ' + options[0] + ' is not recognised.')
    sys.exit()

if not os.path.isfile(fname):
    call_error("The path: '" + str(fname) + "' could not be found.", 'ioerr')

fname = os.path.abspath(fname)
dirname = os.path.dirname(fname)
initialise_path(dirname)
code = get_code(fname)
if isinstance(code, Exception):
    call_error("The path: '" + str(fname) + "' could not be accessed, "
        'perhaps caused by a permission error or something similar.', 'ioerr')

try:
    run(code, fname, raw=True)
except (KeyboardInterrupt, EOFError):
    call_error('', 'keyboardinterrupt')
except RecursionError:
    call_error('RecursionError, too many calls back and forth.', 'recursion')
except Exception as e:
    call_error('', 'fatal')
