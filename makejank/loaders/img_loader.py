import mimetypes
mimetypes.init()
import base64
import textwrap

from . import FileLoader, LoaderWrappingLoader

DEFAULT_MIMETYPE = "application/octet-stream"
DATA_URI_TEMPLATE = "data:%s;base64,%s"
IMG_TEMPLATE = '<img src="%s" />'

class ImgLoader(LoaderWrappingLoader):

    tag = 'img'
    WRAPPED_LOADER = FileLoader()
    DIFFERENT_FOR_PRODUCTION = False

    def wrap_result(self, env, filename, kwargs, result):
        # Guess mime of filename.
        mime, _ = mimetypes.guess_type(filename)
        if mime is None:
            env.logger.debug(
                "Unable to determine mimetype for %s. Using %s",
                filename,
                DEFAULT_MIMETYPE,
            )
            mime = DEFAULT_MIMETYPE

        b64data = base64.b64encode(result)
        data_uri = DATA_URI_TEMPLATE % (mime, b64data)
        wrapped_data_uri = textwrap.fill(data_uri, 1024)
        img = IMG_TEMPLATE % wrapped_data_uri

        return img