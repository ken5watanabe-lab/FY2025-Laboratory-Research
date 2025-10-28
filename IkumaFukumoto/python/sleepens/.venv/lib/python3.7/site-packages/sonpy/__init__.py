from platform import system
from sys import maxsize

if system() == 'Windows':
    if maxsize > 2**32:
        import sonpy.amd64.sonpy as lib
    else:
        import sonpy.win32.sonpy as lib
elif system() == 'Darwin':
    import sonpy.darwin.sonpy as lib
elif system() == 'Linux':
    import sonpy.linux.sonpy as lib
