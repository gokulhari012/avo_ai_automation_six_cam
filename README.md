# Carbon Brushes Quality Check Automation

## Overview

Welcome to the **Carbon Brush Automation Project**, an industrial consultancy initiative aimed at streamlining and enhancing the manufacturing and quality assurance processes of carbon brushes. This project leverages advanced image processing and machine learning techniques to automate the inspection and classification of carbon brushes, ensuring high-quality standards and reducing manual labor.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Dataset Collection Tool](#dataset-collection-tool)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Functionality](#functionality)
- [Merging Datasets](#merging-datasets)
- [Future Enhancements](#future-enhancements)
- [Contact](#contact)

## Project Overview

Carbon brushes are critical components in electric motors and generators, facilitating the transfer of electrical current between stationary and moving parts. Ensuring the quality and consistency of carbon brushes is paramount for the reliability and efficiency of electrical machinery.

This project aims to automate the quality inspection process of carbon brushes by:

- **Automating Data Collection:** Utilizing computer vision to capture high-quality images of carbon brushes.
- **Data Management:** Organizing and managing collected datasets for training machine learning models.
- **Quality Assurance:** Implementing algorithms to detect defects and inconsistencies in carbon brushes.
- **Efficiency Improvement:** Reducing manual inspection time and minimizing human error.

## Features

- **Live Video Feed:** Real-time monitoring of carbon brushes during the manufacturing process.
- **Recording Functionality:** Capture and save frames of carbon brushes for dataset creation.
- **Snapshot Capture:** Take individual snapshots of carbon brushes for detailed analysis.
- **Dataset Management:** Organize captured images into structured datasets for machine learning applications.
- **Merge Datasets:** Consolidate multiple datasets and snapshots into a unified common dataset for comprehensive analysis.

## Dataset Collection Tool

The dataset collection tool is a Python-based application built using Pygame and OpenCV. It facilitates the automated capture and organization of carbon brush images, forming the foundation for subsequent machine learning and quality assurance tasks.

### Prerequisites

Before setting up the dataset collection tool, ensure you have the following installed on your system:

- **Python 3.6 or higher**
- **Pip** (Python package installer)
- **OpenCV:** For image processing.
- **Pygame:** For the graphical user interface.

### Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Clastocarnate/avo_automation.git
    cd avo_automation
    ```

2. **Create a Virtual Environment (Optional but Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    *If `requirements.txt` is not provided, you can install dependencies manually:*

    ```bash
    pip install pygame opencv-python
    ```

### Usage

1. **Connect the Camera:**

    Ensure that a compatible camera is connected to your system. The default camera index is set to `0`. If you have multiple cameras, you might need to adjust the `camera_index` variable in the script.

2. **Run the Dataset Collection Tool:**

    ```bash
    python dataset_collection.py
    ```

3. **Interface Overview:**

    - **Live Feed:** Displays the real-time video feed from the camera.
    - **Record Button:**
      - **Start Recording:** Click to begin saving frames to a new `dataset_n` folder.
      - **Stop Recording:** Click again to stop saving frames.
    - **Snap Button:**
      - **Capture Snapshot:** Click to save the current frame as a snapshot in the `snapshots` folder.
    - **Merge Button:**
      - **Merge Datasets:** Click to consolidate all images from existing datasets and snapshots into a single `common_dataset` folder.

### Functionality

The dataset collection tool offers the following functionalities:

- **Live Video Display:** Continuously displays the live feed from the connected camera, allowing real-time monitoring of carbon brushes.

- **Recording Frames:**
  - **Start Recording:** Initiates the saving of consecutive frames into a uniquely numbered `dataset_n` folder (e.g., `dataset_1`, `dataset_2`, etc.).
  - **Stop Recording:** Halts the frame-saving process.
  
- **Snapshot Capture:**
  - Captures a single frame and saves it in the `snapshots` folder for detailed inspection or specific analysis.

- **Merging Datasets:**
  - Consolidates all images from `dataset_n` folders and the `snapshots` folder into a unified `common_dataset` folder, facilitating comprehensive data analysis and machine learning model training.

## Merging Datasets

The **Merge** functionality is pivotal for aggregating data from various sources into a single repository. This is especially useful for training comprehensive machine learning models.

### How It Works

1. **Click the Merge Button:**
    - Initiates the merging process, copying all images from existing `dataset_n` folders and the `snapshots` folder into the `common_dataset` folder.

2. **File Naming Convention:**
    - **Snapshots:** Prefixed with `snapshot_` to differentiate from dataset frames.
    - **Dataset Frames:** Prefixed with the respective dataset folder name (e.g., `dataset_1_frame_1631023450.jpg`).

3. **Result:**
    - All images are available in `common_dataset/` for unified access and processing.

### Benefits

- **Centralization:** Simplifies data management by having all relevant images in one location.
- **Conflict Avoidance:** Prefixed filenames prevent overwriting and maintain traceability of sources.
- **Ease of Access:** Facilitates seamless integration with machine learning pipelines and data analysis tools.

## Future Enhancements

To further elevate the capabilities of the Carbon Brush Automation Project, consider implementing the following features:

- **Automated Defect Detection:**
  - Integrate machine learning models to automatically identify and classify defects in carbon brushes.
  
- **User Authentication:**
  - Implement user roles and permissions to secure data and control access to functionalities.
  
- **Data Visualization:**
  - Develop dashboards to visualize data metrics, recording statistics, and defect analysis.
  
- **Remote Access:**
  - Enable remote monitoring and control of the dataset collection tool via a web interface or mobile application.
  
- **Advanced Data Management:**
  - Incorporate database systems for more efficient data storage and retrieval, especially for large-scale datasets.

## Contact

For any inquiries or support, please contact:

- **Name:** Ayush Upadhyay
- **Email:** [ayush2005au@gmail.com](mailto:ayush2005au@gmail.com)
- **LinkedIn:** [https://www.linkedin.com/in/ayush-upadhyay-b92629272/](https://www.linkedin.com/in/ayush-upadhyay-b92629272/)

---

Thank you for your interest in the **Carbon Brush Quality Check Automation Project**. We are committed to advancing industrial processes through innovative technological solutions.
