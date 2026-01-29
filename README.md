*DRAFT*

This is a set of scripts to control, run, and analize the CE-QUAL-W2 model.

We have ported CE-QUAL-W2 to Linux under the name of CE-QUAL-W2

Preprocessor.py takes in a directory of Qual-W2 model files and intializes the
process for model runs

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
