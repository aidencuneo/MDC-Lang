'''

MDCL created by Aiden Blishen Cuneo.
First Commit was at: 1/1/2020.

'''

import os.path
import signal
import sys
sys.setrecursionlimit(4995)

fname = []
options = []
for a in sys.argv[1:]:
    if a.startswith('-'):
        options += [a]
    else:
        fname += [a]

from loader import get_code
from var import MDCLError, MDCLExit, sig_c, get_input, call_error, initialise_path, start, _debug_mode, __version__

if options:
    if '-v' in options:
        del options[options.index('-v')]
        print('MDCL ' + __version__)
        sys.exit()
    if '-version' in options:
        del options[options.index('-version')]
        print('MDCL ' + __version__)
        sys.exit()
    if '-r' in options:
        del options[options.index('-r')]
        code = ' '.join(fname)
        src_path = sys.path[0] if _debug_mode else os.path.dirname(sys.path[0])
        initialise_path(src_path, os.getcwd())
        try:
            start(code)
        except MDCLExit:
            pass
        sys.exit()
elif not fname and not options:
    import platform
    pt = platform.system()
    if pt == 'Darwin':
        pt = 'Mac OS X'
    print('MDCL', __version__, 'on', pt, platform.release())
    while True:
        i = get_input('\n--> ')
        if i:
            try:
                start(i, exit_on_exc=False)
            except SystemExit:
                pass
            except MDCLExit:
                sys.exit()
    sys.exit()

if options:
    print('Command line option ' + options[0] + ' is not recognised.')
    sys.exit()

if fname:
    fname = fname[0]

if not os.path.isfile(fname):
    call_error("The path: '" + str(fname) + "' could not be found.", 'ioerr')

fname = os.path.abspath(fname)
dirname = os.path.dirname(fname)
src_path = sys.path[0] if _debug_mode else os.path.dirname(sys.path[0])
initialise_path(src_path, dirname)
code = get_code(fname)
if isinstance(code, Exception):
    call_error("The path: '" + str(fname) + "' could not be accessed, "
        'perhaps caused by a permission error or something similar.', 'ioerr')

start(code, fname)
