import os
from dotenv import load_dotenv
from mongodb_utils import add_message, get_messages, create_new_session
from langchain_utils import get_vectorstore, get_conversation, get_conversational_rag_chain, grader,get_text_chunks
from internetsearcher import handle_non_pdf_question
from reportgenerator import generate_summary
def main():
    load_dotenv()
    new_session_id = create_new_session()
    #user details:
    user_id=14
    user_name="Mathavan"
    # Vector store should be initialized with the pdf content
    vectorstore = None
    text = "ssns company has a revenue of 153 crores"
    chunk=get_text_chunks(text)
    vectorstore = get_vectorstore(chunk)

    def get_response(user_input):
        retriever_chain = get_conversation(vectorstore)
        conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
        chat_history = get_messages(new_session_id)
        response = conversation_rag_chain.invoke({
                "chat_history": chat_history,
                "input": user_input
            })
        grade = grader(user_input, response)
        print(grade)
        if grade.lower() == "no":
            print('2')
            response = handle_non_pdf_question(user_input)
            return response
        return response['answer']

    # Main loop to handle user input and generate responses
    print("###################################################")
    print("Welcome to Cybersnow Analyst bot")
    print("###################################################")
    while True:
        user_input = input("User: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = get_response(user_input)
        print(f"AI: {response}")
        add_message(new_session_id,"human",user_id,user_name,user_input)
        add_message(new_session_id,"ai",user_id,user_name,user_input)

        if user_input.lower()=="report":
            text_data=get_messages(new_session_id)
            report=generate_summary(text_data)
            print(report)
        

if __name__ == "__main__":
    main()
