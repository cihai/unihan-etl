(releasing)=

# Releasing

## Version policy

unihan-etl follows [semantic versioning](https://semver.org/). Until 1.0, minor
releases may include breaking API changes.

## Release checklist

1. Update `CHANGES` with new entries under the next version heading.
2. Bump the version in `pyproject.toml`.
3. Commit: `git commit -m "chore: release vX.Y.Z"`.
4. Tag: `git tag vX.Y.Z`.
5. Push: `git push --follow-tags`.
6. CI publishes to PyPI automatically on tagged pushes.
