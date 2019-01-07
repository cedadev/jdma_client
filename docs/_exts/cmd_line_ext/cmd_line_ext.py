# functions to remove the function signature to documentation of command line
# client from within the docstring

from sphinx.ext import autodoc
from sphinx.pycode import ModuleAnalyzer, PycodeError

class cmdlineDocumenterMixin(object):
    """
    Mixin for cmdline documentation to override the generate method in the
    and the cmdlineFunctionDocumenter - which is inherited from
    autodoc.functionDocumenter - which is, in turn, inherited from autodoc.Documenter
    """
    def generate(self, more_content=None, real_modname=None, check_module=False, all_members=False):
        # parse the name and the objects
        if not self.parse_name():
            return

        if not self.import_object():
            return

        self.real_modname = real_modname or self.get_real_modname()

        if self.real_modname == 'jdma':
            try:
                self.analyzer = ModuleAnalyzer.for_module(self.real_modname)
                self.analyzer.find_attr_docs()
            except PycodeError as err:
                self.env.app.debug('[autodoc] module analyzer failed: %s', err)
                self.analyzer = None
                if hasattr(self.module, '__file__') and self.module.__file__:
                    self.directive.filename_set.add(self.module.__file__)
            else:
                self.directive.filename_set.add(self.analyzer.srcname)

            if check_module:
                if not self.check_module():
                    return

            sourcename = self.get_sourcename()

            # add all content (from docstrings, attribute docs etc.)
            self.add_content(more_content)
            #
            self.indent += self.content_indent + "   "
            #
            # document members, if possible
            self.document_members(all_members)
        else:
            autodoc.Documenter.generate(self, more_content, real_modname, check_module, all_members)

    def process_doc(self, docstrings):
        return autodoc.Documenter.process_doc(self, docstrings)

class cmdlineFunctionDocumenter(cmdlineDocumenterMixin, autodoc.FunctionDocumenter):
    pass

def setup(app):
    autodoc.add_documenter(cmdlineFunctionDocumenter)
