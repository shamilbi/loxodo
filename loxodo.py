#!/usr/bin/env python3

import sys
import platform

# On Windows CE, use the "ppygui" frontend.
if platform.system() == "Windows" and platform.release() == "CE":
    from src.frontends.ppygui import loxodo
    sys.exit()

# All other platforms use the Config module
from src.config import config, PY3

if PY3:
    unicode = str

# store base script name, taking special care if we're "frozen" using py2app or py2exe
if hasattr(sys, "frozen") and (sys.platform != 'darwin'):
    config.set_basescript(unicode(sys.executable, sys.getfilesystemencoding()))
elif PY3:
    config.set_basescript(__file__)
else:
    config.set_basescript(unicode(__file__, sys.getfilesystemencoding()))

# If cmdline arguments were given, use the "cmdline" frontend.
if len(sys.argv) > 1:
    from src.frontends.cmdline import loxodo
    sys.exit()

# In all other cases, use the "wx" frontend.
try:
    import wx
    assert wx.__version__.startswith('4.0.')
except AssertionError as e:
    print('Found incompatible wxPython, the wxWidgets Python bindings: %s' % wx.__version__, file=sys.stderr)
    print('Falling back to cmdline frontend.', file=sys.stderr)
    print('', file=sys.stderr)
    from src.frontends.cmdline import loxodo
    sys.exit()
except ImportError as e:
    print('Could not find wxPython, the wxWidgets Python bindings: %s' % e, file=sys.stderr)
    print('Falling back to cmdline frontend.', file=sys.stderr)
    print('', file=sys.stderr)
    from src.frontends.cmdline import loxodo
    sys.exit()

from src.frontends.wx import loxodo

