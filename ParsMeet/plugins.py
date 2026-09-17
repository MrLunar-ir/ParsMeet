import os
import importlib.util

class Plugin:
    name = "base"
    version = "1.0.0"
    author = ""

    def setup(self, bot):
        pass

    def teardown(self, bot):
        pass

class PluginManager:
    def __init__(self, bot):
        self.bot = bot
        self.plugins = {}

    def register(self, plugin):
        if plugin.name in self.plugins:
            return False
        plugin.setup(self.bot)
        self.plugins[plugin.name] = plugin
        return True

    def unregister(self, name):
        if name in self.plugins:
            self.plugins[name].teardown(self.bot)
            del self.plugins[name]
            return True
        return False

    def load_from_file(self, path):
        if not os.path.exists(path):
            return False
        spec = importlib.util.spec_from_file_location("plugin_module", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, Plugin) and obj is not Plugin:
                self.register(obj())
        return True

    def load_from_folder(self, folder):
        if not os.path.isdir(folder):
            return 0
        count = 0
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not filename.startswith("_"):
                if self.load_from_file(os.path.join(folder, filename)):
                    count += 1
        return count

    def list_plugins(self):
        return list(self.plugins.keys())