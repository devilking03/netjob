import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "netjob",
    version = "1.0.0",
    author = "Narayan Bandodker",
    author_email = "narayanband1356@gmail.com",
    description = "Package to parallelize workloads across a network of processors",
    packages = setuptools.find_packages(),
    long_description = long_description,
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
