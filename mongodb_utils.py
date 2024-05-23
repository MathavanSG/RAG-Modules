from pymongo import MongoClient
from pymongo.server_api import ServerApi
import datetime
import uuid


uri="mongodb+srv://aimathavan14:12345678cyberm@cluster0.kns3rzh.mongodb.net/"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["chat_app"]
messages_collection = db["messages"]
vector_collection=db["vectors"]

def create_new_session():
    """
    Generate a new unique session ID.
    """
    return str(uuid.uuid4())

def add_message(session_id,sender, user_id, username, message):
    """
    Adds a new chat message to the MongoDB database.

    Args:
        session_id (str): The session ID.
        user_id (str): The unique identifier of the user.
        username (str): The username of the user.
        role (str): The role of the sender ("human" or "ai").
        message (str): The content of the message.
    """
    message_data = {
        "session_id": session_id,
        "role": sender,  
        "user_id": user_id,
        "username": username,
        "content": message,
        "timestamp": datetime.datetime.now()
    }
    messages_collection.insert_one(message_data)


def get_messages(session_id):
    """
    Retrieves the latest chat messages from the MongoDB database.

    Args:
        session_id (str): The session ID.

    Returns:
        list: A list of dictionaries, where each dictionary represents a chat message.
    """
    messages = list(messages_collection.find({"session_id": session_id}).sort("timestamp", -1))
    return messages


