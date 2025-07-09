"""
Setup configuration for HireScope
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hirescope",
    version="1.0.0",
    author="GSD at Work LLC",
    author_email="contact@gsdat.work",
    description="AI-powered candidate analysis for Greenhouse ATS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/culstrup/hirescope",
    project_urls={
        "Bug Tracker": "https://github.com/culstrup/hirescope/issues",
        "Documentation": "https://github.com/culstrup/hirescope/wiki",
        "Source Code": "https://github.com/culstrup/hirescope",
        "Company": "https://gsdat.work",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Human Resources",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hirescope=hirescope.cli:main",
        ],
    },
    keywords="recruiting hiring greenhouse ats ai openai candidate analysis hr",
    include_package_data=True,
    zip_safe=False,
)