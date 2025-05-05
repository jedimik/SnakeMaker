from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="SnakeMaker",  # Replace with your project's name
    version="0.1.0",  # Start with an initial version
    author="Your Name",
    author_email="your_email@example.com",
    description="A brief description of your project",
    # Link to your project's repository
    packages=find_packages(),  # Automatically find packages within your project
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Or choose another appropriate license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",  # Specify the minimum Python version required
)
