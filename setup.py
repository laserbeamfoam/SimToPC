from setuptools import find_packages, setup


setup(
    name="simtopc",
    version="0.1.0",
    description="SimToPC: post-processing for LPBF simulations",
    packages=find_packages(include=["simtopc", "simtopc.*"]),
    package_data={"simtopc": ["resources/src/*.py"]},
    include_package_data=True,
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "pyyaml",
        "matplotlib",
        "joblib",
        "importlib-resources; python_version<'3.9'",
    ],
    entry_points={"console_scripts": ["simtopc=simtopc.cli:main"]},
)
