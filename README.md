# ELDA: AI Caregiving System

Welcome to the **ELDA** project. We have developed this system keeping in mind the heavy responsibility of Alzheimer's caregiving. Essentially, it is a localized AI system running in the background, assisting the patient through simple voice and chat interfaces while providing a comprehensive dashboard for caregivers and doctors to monitor the situation seamlessly.

---

## System Architecture

The system architecture is designed for maximum simplicity for the patient. Users interact naturally through voice or text without needing to learn complex interfaces. 

* **The Brain:** Powered by **Qwen 2.5 3B** running locally via **Ollama**. It handles memory management, emotion detection, and risk assessment.
* **For Caregivers:** Provides daily guides and immediate risk alerts to allow for peaceful daily management.
* **For Doctors:** Offers access to long-term trend updates to adjust care plans during medical checkups.

---

## Technology Stack

We utilize **Python 3.10+** for core programming, integrated with the following stack:

| Component | Technology |
| :--- | :--- |
| **LLM Engine** | Ollama (Qwen2.5-3B) |
| **Vector DB / RAG** | Sentence-Transformers & FAISS |
| **Backend** | FastAPI & SQLAlchemy |
| **GUI Framework** | PySide6 |
| **Voice / TTS** | Vosk & Coqui TTS |
| **Database** | Async SQLite |

> [!NOTE]
> Please refer to the `elda` folder in the repository for specific file arrangements.

---

## Setup and Installation

Follow these steps sequentially to start the application on your local system.

### 1. Install Ollama & Pull Model
First, install [Ollama](https://ollama.com/) on your machine. Once installed, pull the required model:

```bash
ollama pull qwen2.5:3b
```
2. Clone the Repository
Clone the project to your local machine and navigate into the directory:
```
git clone [https://github.com/stairmoss/Elda---software-python-GUI-app.git](https://github.com/stairmoss/Elda---software-python-GUI-app.git)
cd Elda---software-python-GUI-app
```
3. Environment Setup
Create and activate a virtual environment to keep your system packages clean:

On Windows:
```
python -m venv venv
venv\Scripts\activate
```
On Mac or Linux: 
```
python -m venv venv
source venv/bin/activate
```
4. Install Dependencies
With the virtual environment active, install the required packages:
```
pip install -r requirements.txt
```
5. Launch the System
Run the main file to start ELDA:
```
python start.py
```
