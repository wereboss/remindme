from setuptools import setup, find_packages

setup(
    name="remindme-pwa",
    version="0.2.0",
    description="Lightweight Python PWA Notes & Reminders Service",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Coder Agent",
    author_email="coder@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "remindme=app.__main__:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
