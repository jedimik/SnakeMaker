# Welcome to SnakeMaker
> Welcome to SnakeMaker, a tool for creating reproducible and scalable workflows for bioinformatics analysis. SnakeMaker is a input interface system that allows you to create complete Snakemake workflows in a human-readable and easy-to-understand way. It is based on the Python programming language and is designed to be easy to use and flexible. With SnakeMaker, you can create complex workflows that can be run on a single machine or on a cluster of machines. SnakeMaker is designed to be easy to use and flexible, and it is a powerful tool for creating reproducible and scalable workflows for biomedical data analysis.
> Snakemaker is mostly aimed to create a replicable, reproducible, scallable workflow. Best practice will be to create at first script in shell, with notation of the input/shell commands/output files. Then create a workflow in SnakeMaker.

## Getting Started
### Installation
> To install SnakeMaker, you can should have thee following dependencies installed on your system:
- Python 3.11 or higher
- Optionally Anaconda or Miniconda for managing Python environments or other software dependencies.

> To install SnakeMaker, navigate to the Snakemaker folder and install all dependencies from requirements.txt. We reccomend using a virtual environment to manage dependencies.

1. Create virtual environment
2. Activate virtual environment
3. Install dependencies from requirements.txt
4. Edit configuration files. (for test runs just edit paths -> more in [Examples](#examples))
5. Run SnakeMaker

**Create virtual environment and install dependencies**
```bash
    # Create virtual environment
    python3 -m venv .venv
    # Activate virtual environment
    source .venv/bin/activate
    # Install dependencies
    pip install .
```

### Run demo version
> To run the demo version of SnakeMaker follow instructions in [Examples](#examples).