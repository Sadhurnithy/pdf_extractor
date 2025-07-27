# Pdf Extractor

**🏆 Adobe "Connecting the Dots" Hackathon (Round 1A) Submission**

A high-performance, ML-powered system that extracts structured outlines (Title, H1, H2, H3) from PDF documents and outputs a clean, hierarchical JSON file. Built to run fully offline in a Dockerized environment while complying with strict performance and resource constraints.

---
## 📌 Table of Contents
- [Overview](#overview)
- [Architecture: ML-Powered Pipeline](#%EF%B8%8F-architecture-ml-powered-pipeline)
- [Models & Libraries Used](#-models--libraries-used)
- [Build & Run Instructions](#-build--run-instructions)
- [Local Testing Guide](#-local-testing-guide)
- [Bonus: Multilingual Support](#-bonus-multilingual-support)
- [Acknowledgements](#-acknowledgements)

---

## 🔍 Overview

This project intelligently parses PDF documents and extracts their logical structure using machine learning, rather than relying solely on font heuristics. It is built with:

- A lightweight LightGBM classification model.
- Fast PDF parsing via PyMuPDF.
- Offline compatibility with no internet access.
- A Docker container for seamless deployment and testing.

---

## ⚙️ Architecture: ML-Powered Pipeline

The system is implemented as a **three-stage pipeline**:

### 🔹 Stage 1: High-Speed PDF Parsing & Feature Engineering
Uses `PyMuPDF (Fitz)` to extract structured features for each text block:
- **Font Features**: Size, family, bold/italic flags.
- **Positional Features**: X-position (for center alignment), whitespace above/below.
- **Statistical Features**: Font size relative to page median.
- **Content Features**: Word count, ALL CAPS flag, numbered list pattern detection.

### 🔹 Stage 2: Heading Classification via LightGBM
- Lightweight, CPU-efficient LightGBM model classifies blocks as:
  `Title`, `H1`, `H2`, `H3`, or `Body`.

### 🔹 Stage 3: Hierarchical Assembly & JSON Output
- Body blocks are discarded.
- Remaining headings are sorted and hierarchically assembled.
- Output saved as a clean, nested JSON.

---

## 📚 Models & Libraries Used

### Machine Learning
- `LightGBM`: Pre-trained classifier for heading detection (`lgbm_header_classifier.txt` < 5MB).

### Core Libraries
- `PyMuPDF`: Ultra-fast PDF parsing and text block metadata extraction.
- `scikit-learn`: Feature preprocessing.

---

## 🐳 Build & Run Instructions

### 1. Build Docker Image
```bash
docker build --platform linux/amd64 -t pdf_extractor:latest .
```
### 2. Run the Docker Container
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf_extractor:latest
```
- Place your .pdf files inside input/
- The container will generate corresponding .json files in output/

## 🧪 Local Testing Guide
### 1. Clone the Repo

```bash
git clone [your-repo-url]
cd [project-directory]
```
### 2. Create Input/Output Folders

```bash
mkdir input output
```
### 3. Add PDF for Testing
- Place sample.pdf inside the input/ directory.

### 4. Build Image
```bash
docker build --platform linux/amd64 -t pdf_extractor:latest .
```
### 5. Run Container

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf_extractor:latest
```
### 6. Check Result
- See output/sample.json for the extracted outline.

---

## 🌍 Bonus: Multilingual Support
This system generalizes across multiple languages and scripts (including non-Latin, such as Japanese) because it relies on structural and layout-based features rather than language-dependent NLP.

---

## 🙏 Acknowledgements
This project was built as part of Adobe's "Connecting the Dots" Challenge (Round 1A).
