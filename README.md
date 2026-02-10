# pyqualw2

`pyqualw2` is a Python toolkit for configuring, running, and analyzing output
for the [CE-QUAL-W2 water quality and hydrodynamic simulation
engine](https://www.ce.pdx.edu/w2/).

> [!WARNING]
> `pyqualw2` is under construction. Not all features are implemented.

## Background

CE-QUAL-W2 is a hydrodynamic and water quality simulation engine that can model
rivers, estuaries, lakes, reservoirs, and river basin systems. It's a widely
used and incredibly useful tool, but it requires great care and niche expertise
to configure and use it for modeling real world systems. Some pain points
include

- **Configuration**: Configuring a CE-QUAL-W2 simulation requires manipulating
  values in a large CSV configuration file by hand, making it both error-prone
  and difficult to understand what each configuration value does.
- **Simulation**: The CE-QUAL-W2 binary expects simulation inputs and outputs
  to exist on certain places on disk. Furthermore, running the engine modifies
  those input files, making it impossible to know what the original
  configuration was for a given simulation.
- **Post-processing**: Cleaning up after a simulation, carrying out
  post-processing on results, and generating data visualizations remains a
  tedious manual task.

`pyqualw2` aims to introduce tooling at each step of the process to ease the
burden of configuring, running, and generating insights from CE-QUAL-W2 output.

## Installation

To install `pyqualw2`, simply

```bash
pip install pyqualw2
```

On Linux, you'll need [Wine](https://www.winehq.org/) installed for the
CE-QUAL-W2 binary to be run, since it is compiled targeting Windows.

## Usage

> [!WARNING]
> The Python bindings are still under construction.

`pyqualw2` provides Python bindings for CE-QUAL-W2, allowing simulations to be
configured, run, and analyzed from inside Python.

> [!WARNING]
> The CLI is still under construction.

`pyqualw2` also provides a CLI so that simulations can be done from the command
line.

## Development

To set up your development environment, install the `dev` optional dependency
group:

```bash
pip install -e '.[dev]'
```

This will install the package along with some other developer tooling.

### Pre-commit hooks

This project uses pre-commit hooks to ensure code quality. To get started,
ensure [`prek`](https://github.com/j178/prek) is installed (it's one of the
dependencies included in the optional `dev` dependency group). Then run

```bash
prek install
```

to install the pre-commit hooks. Read more about pre-commit hooks on the [`prek`
github page](https://github.com/j178/prek).
