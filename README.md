# PDF Outline Extractor

This project is a fully containerized, offline application that extracts a structured outline (Title, H1, H2, H3 headings) from PDF documents. It is designed as an automated backend tool that reads PDFs from a specified input directory and writes structured JSON files to an output directory, adhering to strict performance and resource constraints.

## My Approach

The solution is built around a **dynamic heuristic engine** rather than a large, pre-trained machine learning model. This design ensures full compliance with the competition's size and performance constraints while maintaining high accuracy on a wide range of documents. The logic is entirely self-contained and does not hardcode any file-specific rules, adapting to each PDF individually.

The process for each PDF is as follows:

1.  **Dynamic Style Analysis**: The application first performs a complete pass over the PDF to profile its unique typographic styles (font size, font name, and weight). It counts the frequency of each style to understand the document's inherent structure.

2.  **Hierarchy Inference**: The engine assumes the most frequently used style is the main body text. It then identifies potential headings by finding styles that are either larger than the body text or have a bold font weight. These candidates are sorted by size to dynamically map them to semantic levels: the largest style becomes the `Title`, the next largest `H1`, then `H2`, and so on.

3.  **Hybrid Content Extraction**: With the style map established, the application performs a second pass to extract content. A line of text is identified as a heading if it meets one of two criteria:
    *   It matches one of the identified heading styles from the previous step.
    *   It matches a pre-defined regular expression for common heading patterns (e.g., `1.1. Introduction`, `A. Background`) and is not styled as body text. This hybrid approach allows the tool to correctly identify headings even in documents with less consistent styling.

## Models or Libraries Used

No machine learning models are used in this project. The entire solution is algorithmic.

-   **PyMuPDF (fitz)**: This is the sole library dependency. It is a high-performance Python library for PDF parsing, chosen for its exceptional speed and its ability to extract rich metadata about text, including the font size, name, and weight, which are crucial inputs for the heuristic engine.

## How to Build and Run Your Solution

The application is designed to be built and run using Docker, as specified in the hackathon requirements.

### Prerequisites

-   Docker must be installed and running on your system.

### Build the Docker Image

Navigate to the project's root directory (where the `Dockerfile` is located) and execute the following command. This will build the Docker image and tag it as `pdf-extractor`.

```bash
docker build --platform linux/amd64 -t pdf-extractor:latest .