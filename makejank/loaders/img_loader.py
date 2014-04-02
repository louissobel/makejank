import mimetypes
mimetypes.init()
import base64
import textwrap

from . import BaseLoader

DEFAULT_MIMETYPE = "application/octet-stream"
DATA_URI_TEMPLATE = "data:%s;base64,%s"
IMG_TEMPLATE = '<img src="%s" />'

PRODUCT_NAME_TEMPLATE = "%s:base64_img_tag"

class ImgLoader(BaseLoader):

    tag = 'img'

    def product(self, env, filename, kwargs):
        return PRODUCT_NAME_TEMPLATE % filename

    def dependencies(self, env, filename, kwargs):
        return set([env.resolve_path(filename)])

    def load(self, env, filename, kwargs):
        # Guess mime of filename.
        mime, _ = mimetypes.guess_type(filename)
        if mime is None:
            mime = DEFAULT_MIMETYPE

        pathname = env.resolve_path(filename)
        try:
            with open(pathname, 'rb') as f:
                data = f.read()
        except IOError as e:
            raise ValueError("Error reading file %s: %s" % (pathname, e.strerror))

        b64data = base64.b64encode(data)
        data_uri = DATA_URI_TEMPLATE % (mime, b64data)
        wrapped_data_uri = textwrap.fill(data_uri, 1024)
        img = IMG_TEMPLATE % wrapped_data_uri

        return img