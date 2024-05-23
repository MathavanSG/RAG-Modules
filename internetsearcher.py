
import requests
import bs4
from bs4 import BeautifulSoup


from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from dotenv import load_dotenv
from langchain_utils import  get_vectorstore,get_text_chunks
from langchain_community.tools.tavily_search import TavilySearchResults


from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain import hub



load_dotenv()
# Function to scrape text from a webpage
def scrape_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text(separator=' ', strip=True)
            return page_text
        else:
            return f"Failed to retrieve the webpage: Status code {response.status_code}"
    except Exception as e:
        print(e)
        return f"Failed to retrieve the webpage: {e}"
    

# Function to summarize text
def summarize_text(texts, user_question):
    summarization_template = """Summarize the given {text} and answer it based on the given {user_question}highlight important points. Include all factual information, numbers, stats, etc. if available."""

    
    summarization_prompt = ChatPromptTemplate.from_template(summarization_template)
    summarization_chain = summarization_prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser()
    summarization_response = summarization_chain.invoke({"text": texts, "user_question": user_question})
    summary = summarization_response
    return summary


def handle_non_pdf_question(user_question):
    instructions = """You are an cyber now business analyst assistant"""
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=instructions)
    llm = ChatOpenAI(temperature=0)
    tavily_tool = TavilySearchResults()
    tools = [tavily_tool]
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )
    response=agent_executor.invoke({"input": user_question})
    final=response["output"]
    return final