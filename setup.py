from setuptools import setup, find_packages

# The text of the README file
with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()

# The text of the requirements file
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="lemon-pm",
    version="1.0.0",
    description="A simple, command-line package manager for Windows devices.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jules the AI",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={"console_scripts": ["lemon=lemon_pm.main:main"]},
)
