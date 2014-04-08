from . import BaseLoader

class MakejankLoader(BaseLoader):

    tag = 'makejank'

    def dependencies(self, env, filename, kwargs):
        return env.render_template(filename, get_deps=True)

    def load(self, env, filename, kwargs):
        return env.render_template(filename)
