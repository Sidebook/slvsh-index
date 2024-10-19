from setuptools import setup, find_packages
print(find_packages())

setup(
    name="slvsh_tr",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python",
        "pytesseract",
        "pydantic",
        "tqdm"
    ],
    author="Ryu Wakimoto",
    description="SLVSH Trick Recognizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires='>=3.7',
)
