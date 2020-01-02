import os.path
import sys

if not sys.argv[1:]:
    print('No input file given.')
    sys.exit()

from loader import get_code
from var import get_input, call_error, initialise_path, run

fname = ' '.join(sys.argv[1:])
if not os.path.isfile(fname):
    call_error("The path: '" + str(fname) + "' could not be found.", error_type='ioerr')

fname = os.path.abspath(fname)
dirname = os.path.dirname(fname)
initialise_path(dirname)
code = get_code(fname)
if isinstance(code, Exception):
    call_error("The path: '" + str(fname) + "' could not be accessed, "
        'perhaps caused by a permission error or something similar.', error_type='ioerr')

try:
    run(code, fname, raw=True)
except (KeyboardInterrupt, EOFError):
    call_error('KeyboardInterrupt called.', error_type='ioerr')
except Exception as e:
    call_error('', error_type='fatal')
