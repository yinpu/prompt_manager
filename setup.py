from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prompt-manager",
    version="0.1.0",
    author="作者名",
    author_email="your.email@example.com",
    description="一个用于管理和版本控制提示（prompts）的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/prompt_manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)