from setuptools import setup, find_packages

setup(
    name="ParsMeet",
    version="1.3.1",
    packages=find_packages(),
    install_requires=["httpx>=0.27.0", "websockets>=12.0"],
)