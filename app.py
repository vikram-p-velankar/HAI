from flask import Flask, request, jsonify, render_template
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from flask_cors import CORS  # Add this import
import re
from email.message import EmailMessage
import smtplib

app = Flask(__name__)
CORS(app)

# Initialize global variables
vector_db = None
chain = None

def initialize_chain():
    global vector_db, chain
    
    # Load the existing Chroma database
    persist_directory = "chroma_db_combined_textbooks"
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
        collection_name="local-rag"
    )
    
    local_model = "llama2"
    llm = ChatOllama(model=local_model)
    
    retriever = MultiQueryRetriever.from_llm(
        retriever=vector_db.as_retriever(search_kwargs={"k": 2}),
        llm=llm
    )
    
    template = """
            Context:
{context}

Question:
{question}

Based on the context provided above, answer the question by identifying:
Disease: {{Explanation}}
Medication: {{Explanation}}
Severity: {{Low/High}}

    """

    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

@app.before_request
def setup():
    initialize_chain()

@app.route('/query', methods=['POST', 'GET'])
def query_document():
    global chain
    
    if not chain:
        return jsonify({"error": "Chain not initialized"}), 500
    
    data = request.json
    if 'question' not in data:
        return jsonify({"error": "No question provided"}), 400
    
    
    
    question = data['question']
    answer = chain.invoke(question)

    match = re.search(r'Severity:\s+(\w+)', answer)

    if match:
        severity = match.group(1)
        print("Severity:", severity)

        # Create the email message
        msg = EmailMessage()
        msg['From'] = "arunanshug2002@gmail.com"  # Replace with the sender's email
        msg['To'] = "2003011@ritindia.edu"  # Replace with the recipient's email

        if severity == 'High':
            msg['Subject'] = "High Severity Case - Immediate Attention Required"
            msg.set_content(f"Please review the attached high-profile documents for immediate action on the patient's condition. + {answer}")
            # Attach the high-profile documents or add more details here
        else:
            msg['Subject'] = "Low Severity Case"
            msg.set_content("Please find the attached low-profile documents for the patient's case.")
            # Attach the low-profile documents or add more details here

        # SMTP configuration (using Gmail as an example)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "arunanshug2002@gmail.com"  # Replace with your email
        sender_password = "tmor alpa owgg nkwp"  # Replace with your email password or app password

        # Sending the email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Encrypt the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")
    else:
        print("Severity not found")
    
    return jsonify({"answer": answer}), 200

if __name__ == '__main__':
    app.run(debug=True)
