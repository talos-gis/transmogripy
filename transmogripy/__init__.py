__pacakge_name__ = 'transmogripy'
__author__ = 'Ben Avrahami'
__author_email__ = 'avrahami.ben@gmail.com'
__maintainer__ = 'Idan Miara'
__maintainer_email__ = 'idan@miara.com'
__version__ = '1.2.0'
__license__ = 'MIT'
__url__ = 'https://github.com/talos-gis/transmogripy'
__description__ = 'tool to convert short pascal scripts to python'

from .convert import convert, ResultBehaviour
from .__util import TransmogripyWarning, FatalTransmogripyWarning

# todo ceil/floor