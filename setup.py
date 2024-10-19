from setuptools import setup, find_packages

setup(
    name="fuzz",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dotmap>=1.3.30"
    ],
    python_requires='>=3.6',
    description="A package for generating fuzzing test suites using temporal logic constraints",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.jpl.nasa.gov/lars/fuzzing"
)


