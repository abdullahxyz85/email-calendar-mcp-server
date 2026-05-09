#!/usr/bin/env python
"""Setup script for Email & Calendar MCP Server"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="email-calendar-mcp-server",
    version="1.0.0",
    author="Your Name",
    author_email="your-email@example.com",
    description="Email and Calendar Manager MCP Server for Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/email-calendar-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "google-auth>=2.28.0",
        "google-auth-httplib2>=0.2.0",
        "google-auth-oauthlib>=1.2.0",
        "google-api-python-client>=2.108.0",
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
        "cryptography>=42.0.0",
        "pydantic>=2.8.1",
        "pydantic-settings>=2.0.0",
        "structlog>=24.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.1.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "email-calendar-mcp=email_calendar_mcp.main:main",
        ],
    },
)
