from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prompt-manager",
    version="0.1.0",
    author="yinpu",
    author_email="yinpu.mail@gmail.com",
    description="一个用于管理和版本控制提示（prompts）的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yinpu/prompt_manager.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)