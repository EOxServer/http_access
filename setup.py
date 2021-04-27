from setuptools import setup, find_packages

# with open("README.md", "r") as fh:
#     long_description = fh.read()
long_description = ""

setup(
    name="http_access",
    version="0.0.1",
    author="",
    author_email="",
    description="http direct access django app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.eox.at/esa/prism/vs/-/tree/master/core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    zip_safe=False
)
