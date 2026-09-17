# Release Notes

## 0.1.0 (unreleased)

### 🍰 Features

* Add `--format` to all subcommands to select TOML or JSON output, replacing
  `info --json`. [#5](https://github.com/mcflugen/landlab-cli/pull/5)
* Add the initial `landlab-cli` command with help and version output.
  [#1](https://github.com/mcflugen/landlab-cli/issues/1)
* Add the `landlab-cli` console entry point.
  [#1](https://github.com/mcflugen/landlab-cli/issues/1)
* Add `info`, `components`, `fields`, `grids`, and `catalog` subcommands for
  inspecting an installed Landlab package and generating metadata catalogs.
  [#2](https://github.com/mcflugen/landlab-cli/issues/2)
* Allow `components --using` and `--providing`, and `fields --used-by` and
  `--provided-by`, to be combined. Results must match both filters (AND).
  Each option can be repeated to match any of its supplied values (OR).
  [#4](https://github.com/mcflugen/landlab-cli/issues/4)
* Add `run` subcommand for running a Landlab model.
  [#6](https://github.com/mcflugen/landlab-cli/issues/6)

### 🧪 Tests

* Add tests for command-line parsing and module execution.
  [#1](https://github.com/mcflugen/landlab-cli/issues/1)

### 🧰 Misc

* Add packaging metadata.
  [#1](https://github.com/mcflugen/landlab-cli/issues/1)
* Add Nox sessions for linting, testing, coverage, building, and testing built distributions.
  [#1](https://github.com/mcflugen/landlab-cli/issues/1)
* Add pre-commit configuration.
  [#1](https://github.com/mcflugen/landlab-cli/issues/1)
