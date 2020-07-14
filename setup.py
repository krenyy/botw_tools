from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="botw_tools",
    version="0.2.0",
    author="kreny",
    author_email="kronerm9@gmail.com",
    description="A collection of tools for modding Breath of the Wild",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krenyy/botw_tools",
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aamp = botw_tools.aamp:main",
            "byml = botw_tools.byml:main",
            "sarc = botw_tools.sarc:main",
            "yaz0 = botw_tools.yaz0:main",
            "actorinfo = botw_tools.actorinfo:main",
        ]
    },
)
