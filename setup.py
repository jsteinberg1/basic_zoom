import setuptools

setuptools.setup(
    name="basic_zoom",
    version="0.0.7",
    author="Justin Steinberg",
    author_email="jsteinberg@gmail.com",
    install_requires=["requests", "PyJWT", "requests_oauthlib", "rich"],
    description="REST api client for Zoom",
    long_description="REST api client for Zoom",
    long_description_content_type="text/markdown",
    url="https://github.com/jsteinberg1/basic_zoom",
    packages=["basic_zoom"],
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.8",
)
