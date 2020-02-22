import os
import re
import shutil
import sys

sys.path.insert(0, os.path.abspath('src'))

from var import __version__


def success(tip):
    print('SUCCESS - ' + str(tip))


def error(info):
    print('\n' + info)
    print('CANCELLED AND REVERSED.')
    print('ABORTED.\n')
    exit()


def remove_pycache_info(filename):
    return re.sub('\.cpython-[0-9]+', '', filename)


if os.path.isdir('dist/mdcl-' + str(__version__)):
    error('AN EXPORT OF VERSION ' + str(__version__) + ' ALREADY EXISTS.')
elif os.path.isdir('dist/__init__'):
    shutil.rmtree('dist/__init__')
    success('AN INCOMPLETE EXPORT WAS FOUND BUT SAFELY DELETED.')
elif os.path.isfile('dist/mdcl-' + str(__version__)):
    error('THERE IS A FILE IN THE WAY OF PATH '
        'dist/mdcl-' + str(__version__) + ' WHICH MUST BE REMOVED.')
elif os.path.isfile('dist/__init__'):
    error('THERE IS A FILE IN THE WAY OF PATH '
        'dist/__init__ WHICH MUST BE REMOVED.')

os.system('pyinstaller src/__init__.py')
success('SOURCE HAS BEEN BUILT')

os.remove('dist/__init__/__init__.exe.manifest')
success('REMOVED MANIFEST')

shutil.rmtree('build')
success('REMOVED TEMP BUILD FOLDER')

os.remove('__init__.spec')
success('REMOVED TEMP SPEC FILE')

os.rename('dist/__init__/__init__.exe', 'dist/__init__/mdcl.exe')
success('RENAMED MAIN EXECUTABLE')

if not os.path.isfile('src/startup.mdcl'):
    error('src/startup.mdcl STARTUP FILE NOT FOUND.')
shutil.copy2('src/startup.mdcl', 'dist/__init__/startup.mdcl')
success('COPIED STARTUP FILE (startup.mdcl)')

if not os.path.isdir('src/builtins'):
    error('src/builtins PATH NOT FOUND.')
shutil.copytree('src/builtins', 'dist/__init__/builtins')
success('COPIED BUILTINS')

if not os.path.isdir('src/__pycache__'):
    error('src/__pycache__ PATH NOT FOUND.')
for a in os.listdir('src/__pycache__'):
    if '__init__' in a:
        continue
    shutil.copy2('src/__pycache__/' + a, 'dist/__init__/' + a)
    os.rename('dist/__init__/' + a, remove_pycache_info('dist/__init__/' + a))
success('COPIED AND RENAMED MAIN SOURCE FILES')

try:
    os.rename('dist/__init__', 'dist/mdcl-' + str(__version__))
    success('EXPORT FOLDER RENAMED')
except FileExistsError:
    shutil.rmtree('dist/__init__')
    error('AN EXPORT OF VERSION ' + str(__version__) + ' ALREADY EXISTS.')

print('\nSUCCESS.')
print('Version ' + str(__version__) + ' has been exported and is waiting in '
    '/dist/mdcl-' + str(__version__) + '/\n')
