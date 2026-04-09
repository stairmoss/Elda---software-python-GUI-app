### ELDA: Localized AI Caregiving System

Welcome to the ELDA project. We have developed this system keeping in mind the heavy responsibility of Alzheimer's caregiving. Basically, it is a localized AI system running in the background only. It directly assists the patient using simple voice and chat interfaces, while simultaneously providing a proper dashboard for caregivers and doctors to monitor the situation without any tension.

### System Architecture

The system architecture is designed to be very simple for the patient. They do not need to learn any complex user interface; they can interact naturally through voice or text. At the backend, the ELDA AI brain is doing the heavy lifting. It is powered by Qwen 2.5 3B running locally via Ollama, which handles memory management, detects emotions, and constantly checks for patient risks.

For the family and caregivers, the system provides daily guides and immediate risk alerts so they can manage their daily work peacefully. The concerned doctors can also access long-term trend updations to adjust the care plans accordingly during regular medical checkups.

### Technology Stack

We are utilizing Python 3.10 and above for the core programming. For the AI and logic part, we have integrated Ollama with the Qwen2.5-3B model, Sentence-Transformers for RAG, and FAISS for memory retrieval.

The backend routing is handled by FastAPI and SQLAlchemy, and the desktop application is built using PySide6. For voice processing, Vosk and Coqui TTS are doing the needful. Everything is stored locally in an Async SQLite database because it is very lightweight and fast. Kindly refer to the elda folder in the repository for the exact file arrangements.

### Setup and Installation

Kindly follow these steps sequentially to start the application on your local system.

First, you have to install Ollama on your machine. Once it is installed, open your terminal and pull the required model by running the below command:

ollama pull qwen2.5:3b


Next, kindly clone the project repository to your local machine and navigate into the folder:

git clone https://github.com/stairmoss/Elda---software-python-GUI-app.git

cd Elda---software-python-GUI-app


After that, kindly make sure you have Python installed. It is highly recommended to create and activate a virtual environment so it does not disturb your other system packages. You can do the needful by executing:

python -m venv venv

# If you are using Windows, run this:
venv\Scripts\activate

# If you are using Mac or Linux, run this:
source venv/bin/activate


Once the virtual environment is activated, install all the required Python dependencies:

pip install -r requirements.txt


Once the installations are completed, everything is set. You just need to run the main file to start the system:

python run_elda.py
