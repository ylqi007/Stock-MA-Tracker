# Python Environment Setup for Stock-MA-Tracker

## Background

The project initially used the macOS built-in Python:

``` bash
which python3
# /usr/bin/python3
```

Attempts to run:

``` bash
python3.12 --version
```

returned:

``` text
zsh: command not found: python3.12
```

This indicated that only the system Python was installed and no
standalone Python version was available.

Additional checks confirmed:

-   `/usr/bin/python3` exists (system Python)
-   `python` command does not exist
-   `/usr/local/bin/python*` is empty
-   `/opt/homebrew/bin/python*` is empty

------------------------------------------------------------------------

## Homebrew Status

Verified Homebrew is already installed:

``` bash
brew --version
```

Output:

``` text
Homebrew 5.0.1
```

Therefore, installing Python through Homebrew is the recommended
approach.

------------------------------------------------------------------------

## Why Python 3.13?

We discussed using Python 3.12, 3.13, and 3.14.

### Recommendation

Use **Python 3.13** for this project.

Reasons:

-   New enough to receive active maintenance.
-   Excellent compatibility with common data libraries:
    -   pandas
    -   numpy
    -   matplotlib
    -   yfinance
-   Well supported by GitHub Actions.
-   Better balance between stability and modern features than 3.12 or
    the newest release.

For this project, stability and ecosystem compatibility are more
important than using the absolute latest Python release.

------------------------------------------------------------------------

## Installation

Install Python 3.13:

``` bash
brew install python@3.13
```

Verify:

``` bash
python3.13 --version
which python3.13
```

------------------------------------------------------------------------

## Create a Virtual Environment

Inside the repository:

``` bash
cd ~/Work/Finance/Stock-MA-Tracker

python3.13 -m venv .venv
source .venv/bin/activate
```

Verify:

``` bash
python --version
which python
pip --version
```

Expected:

``` text
Python 3.13.x
.../Stock-MA-Tracker/.venv/bin/python
```

------------------------------------------------------------------------

## Ignore the Virtual Environment

Add the virtual environment to `.gitignore`:

``` bash
echo ".venv/" >> .gitignore
```

Verify:

``` bash
git status
```

The `.venv` directory should not be committed to Git.

------------------------------------------------------------------------

## GitHub Actions Version

Use the same Python version in CI:

``` yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.13"
```

Keeping the local development environment and GitHub Actions on the same
Python version helps avoid version-specific issues.

------------------------------------------------------------------------

## Final Decision

-   Python version: **3.13**
-   Environment management: **venv**
-   Dependency management: **requirements.txt**
-   Local and GitHub Actions use the **same Python version**
-   Do **not** rely on the macOS system Python for project development

---

# Understanding and Managing Python Virtual Environments

## What Is a Virtual Environment?

A Python virtual environment is an isolated Python environment created specifically for one project.

For example, you may have two projects:

```text
Stock-MA-Tracker
Web-App
```

They may require different dependency versions:

```text
Stock-MA-Tracker:
pandas==2.3.0

Web-App:
pandas==2.1.4
```

If every dependency is installed into the same global Python environment, different projects can interfere with one another.

With virtual environments, each project has its own isolated dependency space:

```text
Stock-MA-Tracker/.venv/
Web-App/.venv/
```

The dependencies of one project do not affect the other.

---

## What Is Inside `.venv`?

Running:

```bash
python3.13 -m venv .venv
```

creates a directory similar to:

```text
.venv/
├── bin/
│   ├── python
│   ├── pip
│   └── activate
├── include/
├── lib/
└── pyvenv.cfg
```

The most important files are:

```text
.venv/bin/python
.venv/bin/pip
```

These are the Python interpreter and package installer used by this project.

A virtual environment is not a virtual machine. It does not create a separate operating system. It creates an isolated Python runtime and dependency directory associated with a specific Python installation.

---

# Why Use a Virtual Environment?

## 1. Prevent Dependency Conflicts

Different projects may require different versions of the same library.

For example:

```text
Project A requires yfinance 0.2.x
Project B requires a newer yfinance version
```

Installing both into one global environment can cause one project to break when the package is upgraded.

With separate environments:

```text
Project-A/.venv → its own dependencies
Project-B/.venv → its own dependencies
```

Each project can use the versions it needs.

---

## 2. Avoid Modifying the macOS System Python

The current system Python is located at:

```text
/usr/bin/python3
```

This Python installation is managed by macOS or the Apple Command Line Tools.

Avoid commands such as:

```bash
sudo pip install pandas
```

Installing packages into the system Python can cause:

- permission problems
- dependency conflicts
- unexpected changes to system tools
- difficulty determining which Python installation is being used

Inside a virtual environment, packages can be installed without `sudo`:

```bash
python -m pip install pandas
```

The package is installed only inside the project's `.venv`.

---

## 3. Keep Local Development and GitHub Actions Consistent

Locally, the project can use:

```text
Python 3.13
pandas
yfinance
matplotlib
```

GitHub Actions can use the same Python version:

```yaml
- name: Set up Python
  uses: actions/setup-python@v6
  with:
    python-version: "3.13"
```

Dependencies are then installed from a dependency file:

```bash
python -m pip install -r requirements.txt
```

This reduces the chance of encountering:

> It works locally, but fails in GitHub Actions.

---

## 4. Make the Environment Reproducible

The virtual environment itself should not be committed to Git.

Instead, commit dependency declarations such as:

```text
requirements.txt
pyproject.toml
```

Another developer or GitHub Actions can recreate the environment with:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The virtual environment is disposable. The dependency definition is the source of truth.

---

# Creating a Virtual Environment

Enter the repository:

```bash
cd ~/Work/Finance/Stock-MA-Tracker
```

Create the environment:

```bash
python3.13 -m venv .venv
```

Command breakdown:

```text
python3.13
```

Uses Python 3.13 to create the environment.

```text
-m venv
```

Runs Python's built-in `venv` module.

```text
.venv
```

Specifies the environment directory name.

`.venv` is a common convention and is automatically recognized by many editors and Python tools.

---

# Activating the Virtual Environment

On macOS and Linux:

```bash
source .venv/bin/activate
```

After activation, the terminal usually changes to:

```text
(.venv) ➜ Stock-MA-Tracker git:(main)
```

Verify the interpreter:

```bash
which python
python --version
```

Expected output:

```text
.../Stock-MA-Tracker/.venv/bin/python
Python 3.13.x
```

Verify pip:

```bash
which pip
python -m pip --version
```

The output should point to a path inside:

```text
Stock-MA-Tracker/.venv/
```

---

## What Does Activation Actually Do?

Activation temporarily modifies the current terminal's `PATH`.

It places:

```text
.venv/bin
```

before other executable locations.

Therefore, when you run:

```bash
python
```

the shell finds:

```text
.venv/bin/python
```

before the system Python.

Activation affects only the current terminal session.

---

# Deactivating the Virtual Environment

Run:

```bash
deactivate
```

The `(.venv)` prefix disappears.

The terminal then returns to the Python configuration outside the virtual environment.

---

# Do You Need to Activate It Every Time?

Yes.

Activation only applies to the current terminal session.

After opening a new terminal, run:

```bash
cd ~/Work/Finance/Stock-MA-Tracker
source .venv/bin/activate
```

VS Code can also be configured to automatically use the project's virtual environment.

---

# Installing Dependencies

After activating the virtual environment, install packages with:

```bash
python -m pip install pandas
```

For this project:

```bash
python -m pip install pandas yfinance matplotlib
```

Using:

```bash
python -m pip
```

is preferred over using `pip` directly because it makes it explicit that pip belongs to the currently selected Python interpreter.

List installed packages:

```bash
python -m pip list
```

Inspect a package:

```bash
python -m pip show pandas
```

Remove a package:

```bash
python -m pip uninstall pandas
```

---

# Recording Dependencies

## Using `requirements.txt`

One approach is:

```bash
python -m pip freeze > requirements.txt
```

This produces exact versions for all installed packages, including transitive dependencies.

Example:

```text
matplotlib==3.10.3
numpy==2.3.1
pandas==2.3.0
yfinance==0.2.65
```

Install them later with:

```bash
python -m pip install -r requirements.txt
```

For the first version of Stock-MA-Tracker, it may be simpler to maintain only the project's direct dependencies manually:

```text
pandas
yfinance
matplotlib
```

Later, exact versions can be pinned when the project needs stronger reproducibility.

---

# Why `.venv` Must Not Be Committed

The `.venv` directory:

- contains many files
- may use significant disk space
- includes machine-specific paths
- depends on the operating system and CPU architecture
- can be recreated from dependency definitions

A virtual environment created on an Apple Silicon Mac should not be reused directly on a Linux GitHub Actions runner.

Add this to `.gitignore`:

```gitignore
.venv/
```

Recommended Python-related entries:

```gitignore
.venv/
__pycache__/
*.pyc
.DS_Store
```

Verify:

```bash
git status
```

The `.venv` directory should not appear as files to commit.

---

# Daily Virtual Environment Workflow

## Start Development

```bash
cd ~/Work/Finance/Stock-MA-Tracker
source .venv/bin/activate
```

Confirm the environment:

```bash
python --version
which python
python -m pip --version
```

Install project dependencies if necessary:

```bash
python -m pip install -r requirements.txt
```

Run the project:

```bash
python tracker.py
```

## Finish Development

```bash
deactivate
```

---

# Managing the Virtual Environment

## Do Not Edit `.venv` Manually

Do not manually modify files inside:

```text
.venv/lib
.venv/bin
```

Use pip commands instead:

```bash
python -m pip install <package>
python -m pip uninstall <package>
```

---

## Rebuilding a Broken Environment

A virtual environment is disposable.

If it becomes corrupted or inconsistent:

```bash
deactivate
rm -rf .venv
```

Recreate it:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The important files to preserve are:

```text
source code
requirements.txt
pyproject.toml
```

The `.venv` directory itself does not need to be preserved.

---

## Upgrading the Python Version

Suppose the project later moves from Python 3.13 to Python 3.14.

Do not continue using the old environment.

Recreate it:

```bash
deactivate
rm -rf .venv

python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Virtual environments are closely tied to the Python version that created them.

---

# Verifying the Correct Environment

Before running the project, use:

```bash
python --version
which python
python -m pip --version
```

Expected results should point inside the repository:

```text
Python 3.13.x
/Users/<username>/Work/Finance/Stock-MA-Tracker/.venv/bin/python
pip ... from .../Stock-MA-Tracker/.venv/lib/python3.13/site-packages
```

If the interpreter points to:

```text
/usr/bin/python3
```

the project virtual environment is not active.

---

# Configuring VS Code

Open the project in VS Code.

Press:

```text
Command + Shift + P
```

Search for:

```text
Python: Select Interpreter
```

Select:

```text
./.venv/bin/python
```

VS Code will then use the virtual environment for:

- running Python files
- debugging
- autocomplete
- linting
- integrated terminals
- package discovery

---

# Recommended Project Structure

```text
Stock-MA-Tracker/
├── .venv/                # Local only; never commit
├── .github/
│   └── workflows/
├── data/
├── src/
├── tests/
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# Recommended Environment Standard

For the first version of Stock-MA-Tracker:

```text
Python version: Python 3.13
Virtual environment directory: .venv
Package installation: python -m pip
Dependency file: requirements.txt
CI environment: GitHub Actions with Python 3.13
```

The core principle is:

> `.venv` is a disposable local runtime environment. `requirements.txt` or `pyproject.toml` is the formal description used to recreate it.

