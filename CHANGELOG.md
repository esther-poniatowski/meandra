# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Rename the option `--config`/`-c` of `run` to `--inputs`/`-i`, since the
  command-line conventions reserve `--config` for the configuration file of a
  tool; the former name is retired without an alias.
- Give `--version` the short form `-v`, retire `-V`, and remove the short form
  `-v` of `--verbose`.
- Exit with status 2 on a usage error (a malformed `--param`, a class without
  `@pipeline`, an unknown graph format) and with status 1 on a problem found
  by a validation or a run.
- Make `validate --pipeline` fail with status 1 on missing inputs, instead of
  printing a warning.

### Fixed

- Print the version on `meandra --version` without a command, instead of
  failing with "Missing command".

### Added

- Initial project structure and core workflow orchestration framework.
