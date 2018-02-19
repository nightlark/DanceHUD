"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['DanceHUD.py']
DATA_FILES = [
    ('', ['font', 'icons'])
              ]

INCLUDES = ['sdl2',
            'sdl2.ext',
            'sdl2.sdlimage',
            'sdl2.sdlttf']

FRAMEWORKS = ['/Library/Frameworks/SDL2.framework',
              '/Library/Frameworks/SDL2_image.framework',
              '/Library/Frameworks/SDL2_ttf.framework']

OPTIONS = {
    'argv_emulation': True,
    'frameworks': FRAMEWORKS,
    'includes': INCLUDES
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
