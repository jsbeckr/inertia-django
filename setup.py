import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inertia-django",
    version="0.1.1",
    author="Jens Becker",
    author_email="jensbecker@gmail.com",
    description="The Django adapter for Inertia.js.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsbeckr/inertia-django",
    packages=setuptools.find_packages(),
    keywords='django inertia template',
    classifiers=[
        "Framework :: Django",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.2'
)