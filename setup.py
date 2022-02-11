from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="http_access",
    version="0.1.3",
    author="Nikola Jankovic",
    author_email="nikola.jankovic@eox.at",
    description="http direct access django app",
    long_description_content_type="text/markdown",
    url="https://github.com/EOxServer/http_access",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    zip_safe=False,
)
