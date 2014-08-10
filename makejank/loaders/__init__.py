from base_loader import BaseLoader
from loader_wrapping_loader import LoaderWrappingLoader

from file_loader import FileLoader
from yaml_loader import YamlLoader
from css_loader import CSSLoader
from js_loader import JSLoader
from img_loader import ImgLoader
from makejank_loader import MakejankLoader
from shell_loader import ShellLoader


class WrapLoader(object):
    """
    Namespace for loader finder
    """
    def __init__(self, loader):
        self.loader = loader

makejank_file       = WrapLoader(FileLoader)
makejank_yaml       = WrapLoader(YamlLoader)
makejank_css        = WrapLoader(CSSLoader)
makejank_js         = WrapLoader(JSLoader)
makejank_img        = WrapLoader(ImgLoader)
makejank_makejank   = WrapLoader(MakejankLoader)
makejank_shell      = WrapLoader(ShellLoader)
