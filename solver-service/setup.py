from setuptools import setup, find_packages

setup(
    name="solver-service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "ortools>=9.4.1874",
        "pydantic>=1.8.2",
        "python-dotenv>=0.19.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "python-multipart>=0.0.5",
        "openai>=0.27.0"
    ],
) 