PY_FILES= find . -type f -not -path '*/\.*' | grep -i '.*[.]py$$' 2> /dev/null


entr_warn:
	@echo "----------------------------------------------------------"
	@echo "     ! File watching functionality non-operational !      "
	@echo ""
	@echo "Install entr(1) to automatically run tasks on file change."
	@echo "See http://entrproject.org/"
	@echo "----------------------------------------------------------"

isort:
	isort `${PY_FILES}`

black:
	black `${PY_FILES}` --skip-string-normalization

test:
	py.test $(test)

watch_test:
	if command -v entr > /dev/null; then ${PY_FILES} | entr -c $(MAKE) test; else $(MAKE) test entr_warn; fi

vulture:
	vulture unihan_etl

watch_vulture:
	if command -v entr > /dev/null; then ${PY_FILES} | entr -c $(MAKE) vulture; else $(MAKE) vulture entr_warn; fi

build_docs:
	cd doc && $(MAKE) html

watch_docs:
	cd doc && $(MAKE) watch_docs

flake8:
	flake8 unihan_etl tests

watch_flake8:
	if command -v entr > /dev/null; then ${PY_FILES} | entr -c $(MAKE) flake8; else $(MAKE) flake8 entr_warn; fi
