import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prettyphi",
    version="0.1",
    author="Renzo Comolatti & Matteo Grasso",
    author_email="renzo.com@gmail.com",
    description="A library to visualize IIT-4.0 cause-effect structures from PyPhi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renzocom/prettyphi",
    packages=setuptools.find_packages(include=['prettyphi']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
    ],
)