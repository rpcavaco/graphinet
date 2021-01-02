
import setuptools

LONG_DESCRIPTION = "Graphinet is a Python 3 library to manipulate generic directed network graphs"

setuptools.setup(
    name="graphinet", 
    version="0.0.1",
    author="Rui Pedro Cavaco Barrosa",
    author_email="rpcavaco@gmail.com",
    description="Network graph manipulation",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/rpcavaco/graphinet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
