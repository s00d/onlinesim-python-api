# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-10
### Added
- API domain replacement capability through `base_url` parameter in `API` class constructor
- `base_url` parameter allows using alternative domains for API endpoints
- Comprehensive test coverage for custom domain functionality
- New test file `tests/test_custom_domain.py` with unit tests for API domain replacement

### Changed
- Updated pydantic dependency to support both v1 and v2 (>=1.10.0,<3.0.0)
- Enhanced test infrastructure with pytest, pytest-cov, and pytest-mock
- Migrated from setup.py to modern pyproject.toml configuration
- Replaced legacy setuptools with modern build system
- Updated GitHub Actions workflow to use modern actions and PyPI API tokens
- Centralized version management in pyproject.toml, removed _version.py


## [2.0.1] - 2022-02-06
### Added
- refactoring, thanks to [RTHeLL](https://github.com/RTHeLL)

## [1.0.5] - 2019-09-21
### Added
- add ban

## [1.0.5] - 2019-09-21
### Added
- full message

## [1.0.1] - 2019-08-06
### Added
- multiple driver

## [1.0.1] - 2019-08-06
### Changed
- remove async

## [1.0.0] - 2019-08-05
### Added
- Project





