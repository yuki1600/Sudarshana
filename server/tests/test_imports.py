"""Every import in core_logic/ and server/ resolves, the ones inside functions too: those run only when their
path does, so a name lost when code moves between modules would otherwise surface as an error in the app."""
import ast
import importlib
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestImports(unittest.TestCase):
    def test_every_import_resolves(self):
        bad = []
        for top in ("core_logic", "server"):
            for d, _, files in os.walk(os.path.join(ROOT, top)):
                if "tests" in os.path.relpath(d, ROOT).split(os.sep):
                    continue
                for f in (f for f in files if f.endswith(".py")):
                    path = os.path.join(d, f)
                    mod = os.path.relpath(path, ROOT)[:-3].replace(os.sep, ".")
                    pkg = mod[: -len(".__init__")] if f == "__init__.py" else mod.rsplit(".", 1)[0]
                    with open(path, encoding="utf-8") as fh:
                        tree = ast.parse(fh.read(), path)
                    for node in ast.walk(tree):
                        where = "%s:%d" % (os.path.relpath(path, ROOT), getattr(node, "lineno", 0))
                        try:
                            if isinstance(node, ast.Import):
                                for a in node.names:
                                    importlib.import_module(a.name)
                            elif isinstance(node, ast.ImportFrom):
                                base = node.module or ""
                                if node.level:
                                    parts = pkg.split(".")
                                    base = ".".join(parts[: len(parts) - node.level + 1] + ([node.module] if node.module else []))
                                m = importlib.import_module(base)
                                for a in node.names:
                                    if a.name != "*" and not hasattr(m, a.name):
                                        try:
                                            importlib.import_module(base + "." + a.name)   # a submodule
                                        except ImportError:
                                            bad.append("%s: %s has no %s" % (where, base, a.name))
                        except ImportError as e:
                            bad.append("%s: %s" % (where, e))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
