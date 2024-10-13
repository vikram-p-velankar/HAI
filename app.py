from flask import Flask, request, jsonify
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from flask_cors import CORS  # Add this import


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
    
    return jsonify({"answer": answer}), 200

if __name__ == '__main__':
    app.run(debug=True)