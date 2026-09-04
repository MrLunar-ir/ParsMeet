from setuptools import setup, find_packages

setup(
    name="ParsMeet",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "websockets>=12.0",
        "requests>=2.20",
        "Pillow>=10.0.0"
    ],
    python_requires=">=3.8"
)