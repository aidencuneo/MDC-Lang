import os
import sys

import loader
import var

if not sys.argv[1:]:
    print('No input file given.')
    try:
        prompt = var.get_input('Type a file path to run a file, or press enter to quit: ')
    except (KeyboardInterrupt, EOFError):
        prompt = False
    if not prompt:
        sys.exit()
    print(end='\n')
    code = loader.get_code(prompt)

fname = ' '.join(sys.argv[1:])
if not os.path.isfile(fname):
    var.call_error("The path: '" + str(fname) + "' could not be found.", error_type='ioerr')

fname = os.path.abspath(fname)
dirname = os.path.dirname(fname)
var.initialise_path(dirname)
code = loader.get_code(fname)
if isinstance(code, Exception):
    var.call_error("The path: '" + str(fname) + "' could not be accessed, "
        'perhaps caused by a permission error or something similar.', error_type='ioerr')

var.run(code, fname, raw=True)
