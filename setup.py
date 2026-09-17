from setuptools import setup, find_packages

setup(
    name="ParsMeet",
    version="2.1.0",
    description="Professional Python library for building CodeMeet bots.",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "httpx>=0.27.0",
        "websockets>=12.0",
        "requests>=2.20",
        "Pillow>=10.0.0"
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"]
    },
    entry_points={
        "console_scripts": [
            "parsmeet=ParsMeet.cli:main"
        ]
    },
    python_requires=">=3.8"
)