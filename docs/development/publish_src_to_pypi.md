# How to Publish a Source Distribution (.tar.gz) to PyPI

This guide documents how I published a source distribution (`.tar.gz`) for version `4.0.3` of [PyPubSub](https://github.com/schollii/pypubsub) to [PyPI](https://pypi.org/project/PyPubSub/4.0.3/#files).

## Steps

### 1. Clone the repo and checkout the release tag

```bash
git clone git@github.com:schollii/pypubsub.git
cd pypubsub/
git checkout v4.0.3
````

### 2. Ensure Python, pip, and venv are set up

```bash
python3 --version
sudo apt install python3-pip
sudo apt install python3.10-venv  # Or appropriate version
```

### 3. Install `build` and generate the `.tar.gz`

```bash
pip3 install build
python3 -m build --sdist
```

This creates the file:

```
dist/pypubsub-4.0.3.tar.gz
```

### 4. Install `twine` and ensure your PATH is correct

```bash
pip install twine
export PATH=$HOME/.local/bin:$PATH
```

You may add that `PATH` line to your `.bashrc` or `.zshrc` if needed.

### 5. Upload the `.tar.gz` to PyPI

```bash
twine upload dist/pypubsub-4.0.3.tar.gz
```

It will prompt for your PyPI username and password (or use an API token if configured).

### 6. Confirm upload

Go to:
[https://pypi.org/project/PyPubSub/4.0.3/#files](https://pypi.org/project/PyPubSub/4.0.3/#files)
You should now see the `.tar.gz` listed alongside the `.whl`.

---

## Notes

* If you run into issues with `twine`, check that `~/.pypirc` is correctly set up or use `--repository-url`.

