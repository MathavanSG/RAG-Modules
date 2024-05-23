from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.schema.output_parser import StrOutputParser

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from langchain.docstore.document import Document



uri="mongodb+srv://aimathavan14:12345678cyberm@cluster0.kns3rzh.mongodb.net/"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["chat_app"]
messages_collection = db["messages"]
vector_collection=db["vectors"]

ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    '''documents = [Document(page_content=chunk) for chunk in text_chunks]
    vectorstore = MongoDBAtlasVectorSearch.from_documents(
        documents=documents,
        embedding=embeddings,
        collection=vector_collection,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
    )'''
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation(vectorstore):
    llm = ChatOpenAI()
    retriever = vectorstore.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    llm = ChatOpenAI()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Your name is Cybersnow bot,Your role is a  Research Business Analyst,Answer the user's questions based on the below context with a quantitative data which is numerical  with respect to the business context only if available if not do not makeup :\n\n{context}"),
        MessagesPlaceholder(variable_name='chat_history'),
        ("user", "{input}")
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def grader(user_input, response):
    # LLM with function call
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

    # Prompt
    system = """You are assessing the relevance of responses to a user question. 

    If the response directly answers the user's question with factual information or relevant content without including phrases such as 'I don't know', 'I don't have real-time information', 'I do not have specific data available', 'I apologize for the confusion', 'I am sorry', or 'I won't be able to provide', then mark it as relevant.

    Give a binary score 'yes' or 'no' to indicate whether the response is relevant to the question."""
    grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved response: \n\n {response} \n\n User question: {question}"),
        ("system", "Is the response relevant to the user's question? (yes/no)"),
    ]
)



    retrieval_grader = grade_prompt | llm | StrOutputParser()
    result = retrieval_grader.invoke({"question": user_input, "response":response})
    return result

# Function to split text into chunks
def get_text_chunks(cleaned_texts_with_images):
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        separator=' \n ',
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(cleaned_texts_with_images)
    #print(chunks)
    return chunks