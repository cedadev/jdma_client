# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = jdma_client
SOURCEDIR     = .
BUILDDIR      = _build
GH_PAGES_SOURCES = jdma_client Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

publish:
	git checkout gh-pages
	rm -rf build _sources _static
	git checkout master $(GH_PAGES_SOURCES)
	git reset HEAD
	make html
	mv -fv build/html/* ./
#	rm -rf $(GH_PAGES_SOURCES) build
	# git add -A
	# git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
	# git push origin gh-pages
	# git checkout master

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
