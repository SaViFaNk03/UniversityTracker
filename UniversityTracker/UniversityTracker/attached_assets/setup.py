from setuptools import setup, find_packages

setup(
    name="university-career-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
        "matplotlib",
    ],
    package_data={
        "": ["assets/*"],
    },
    entry_points={
        "console_scripts": [
            "university-career-manager=main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Un'applicazione per la gestione della carriera universitaria",
    keywords="university, career, management, grades, exams",
    url="https://github.com/yourusername/university-career-manager",
    classifiers=[
        "Development Status :: A completa app desktop per Windows",
        "Intended Audience :: Studenti universitari",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)