
import setuptools

LONG_DESCRIPTION = "Netmesh is a Python 3 library to ...."

setuptools.setup(
    name="netmesh", # Replace with your own username
    version="0.0.1",
    author="Rui Pedro Cavaco Barrosa",
    author_email="rpcavaco@gmail.com",
    description="------- blá blá .....",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
