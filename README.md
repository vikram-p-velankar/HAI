# HAI
Healthcare AI Model
Utilizes Capabilities of Llama2 LLM and Langchain with RAG for summarization of the possiblity of Disease a patient has depending on his current symptoms.

1. app.py is for flask server that serves as a backend for our telemedicine kiosk
2. index.html serves as main web app page for the application
3. STMP utilized for sending mail to the patient with probable medication and severity with the disease that the user is infected with.

Requirements:-
1. Ollama
2. llama2
3. nomic-embed-text
4. ``flask, langchain, langchain_community, flask_cors, email, smtplib, chromadb``

How to Use:-
1. Install Ollama
2. ``ollama run llama2``
3. Exit the llama2 model and the pull nomic-embed-text using ``ollama pull nomic-embed-text``
4. Once done with the download rerun ``ollama run llama2``
5. Navigate to the HAI folder ``cd ~/PATH/HAI-main``
6. install all the requirements from requirements.txt
7. run application using following command ``python app.py``
8. Once server starts Open ``index.html`` from the directory on web Browser.
9. Select any prompt from ``prompt.txt`` or any similar to context of provided prompts.
10. Wait for model to work and you get all the information for disease a patient has.


# PROJECT WAS PART OF HACKDEARBORN-3 at UofM-DEARBORN
Team Members:
1. Vikram Velankar
2. Neha Basugade
3. Sai Arunanshu Govindarajula
4. Alex Boccaccio
