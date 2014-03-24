import mimetypes
mimetypes.init()
import base64
import textwrap

DEFAULT_MIMETYPE = "application/octet-stream"
DATA_URI_TEMPLATE = "data:%s;base64,%s"
IMG_TEMPLATE = '<img src="%s" />'

PRODUCT_NAME_TEMPLATE = "%s:base64_img_tag"

class ImgLoader(object):

    tag = 'img'

    def dependency_graph(self, env, args):
        filename = args[0]
        product = PRODUCT_NAME_TEMPLATE % filename
        deps = [env.resolve_path(filename)]
        return product, deps

    def load(self, env, args):
        filename = args[0]

        # Guess mime of filename.
        mime, _ = mimetypes.guess_type(filename)
        if mime is None:
            mime = DEFAULT_MIMETYPE

        try:
            with open(env.resolve_path(filename), 'rb') as f:
                data = f.read()
        except IOError:
            # TODO: WHAT DO WE DO
            raise ValueError

        b64data = base64.b64encode(data)
        data_uri = DATA_URI_TEMPLATE % (mime, b64data)
        wrapped_data_uri = textwrap.fill(data_uri, 1024)
        img = IMG_TEMPLATE % wrapped_data_uri

        return img