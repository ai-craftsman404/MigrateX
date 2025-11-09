from setuptools import setup, find_packages

setup(
    name="migratex",
    version="0.0.1",
    description="Semi-automated migration assistant for migrating Semantic Kernel and AutoGen code to Microsoft Agent Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MigrateX Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "libcst>=1.1.0",
        "diff-match-patch>=20230430",
    ],
    entry_points={
        "console_scripts": [
            "migrate=migratex.cli.main:cli",
        ],
    },
)

