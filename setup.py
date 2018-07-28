from setuptools import setup, find_packages

exec(open("triopg/_version.py", encoding="utf-8").read())

LONG_DESC = open("README.rst", encoding="utf-8").read()

setup(
    name="triopg",
    version=__version__,
    description="PostgreSQL client for Trio based on asyncpg",
    url="https://github.com/python-trio/triopg",
    long_description=LONG_DESC,
    author="Emmanuel Leblond",
    author_email="emmanuel.leblond@gmail.com",
    license="MIT -or- Apache License 2.0",
    packages=find_packages(),
    install_requires=[
        "trio",
        "trio-asyncio",
        "asyncpg",
    ],
    keywords=["async", "trio", "sql", "postgresql", "asyncpg"],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Trio",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: SQL",
    ],
)
