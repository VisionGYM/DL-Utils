from setuptools import find_packages, setup


def read_requirements(path):
    with open(path) as f:
        modules = f.read().splitlines()

    return modules


setup(
    name="dlutils",
    version="0.0.1",
    author="10cho",
    author_email="myeddie77@gmail.com",
    url="https://github.com/eddie94/dl-utils",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
)
