# SnakeMaker parser
> Requires python>=3.12

## With standard pip virtualvenv
> 1. Create virtualenv and Activate it 
> 2. install with : 'pip install -e .'
> 3. Look for all <path> in the config files and replace them with the correct path, also in demo_functions path for the shell function
> 3. Run with : 'python SnakeMaker/snakemaker.py'

## With UV 
> 1. Install uv from this [link](https://docs.astral.sh/uv)
> 2. Run ```uv venv``` from default Snakemaker folder to create a virtual environment
> 3. Activate virtualenvironment
> 4. Run ```uv pip install -e .```
> 5. Run with 'python SnakeMaker/snakemaker.py' 

## To run documentation locally:
> 1. Install mkdocs with 'pip install mkdocs' (should be installed in the virtualenv after running 'pip install .')
> 2. Run 'mkdocs serve' in the docs directory.
> 3. Open the browser and go to 'http://localhost:8000'