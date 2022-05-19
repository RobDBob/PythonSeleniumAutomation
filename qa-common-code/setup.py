import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

setuptools.setup(
    name="wm-automation-common",
    version="0.2.19",
    author="Framework Test Infrastructure",
    author_email="robert.deringer@company.com",
    description="QA Core Framework libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.prod.company.com/scm/qaf/qa-common-code.git",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)