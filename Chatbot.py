from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")

username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Debugging ke liye check karo ki API key load ho rahi hai ya nahi
print(f"Loaded API Key: {GroqAPIKey}")

if not GroqAPIKey:
    raise ValueError("API Key is missing! Check your .env file.")

Client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Set the initial message as system
SystemChatBot = [{"role": "system", "content": System}]

# Linux-compatible file path
file_path = os.path.join("data", "chatlog.json")

try:
    with open(file_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(file_path, "w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"Real-time Info: {current_date_time.strftime('%Y-%m-%d %H:%M:%S')}"

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    return "\n".join(line.strip() for line in lines if line.strip())

def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response"""
    
    try:
        with open(file_path, "r") as f:
            messages = load(f)

        # Correct role for User
        messages.append({"role": "user", "content": Query})  # User role set correctly
        
        # Combine System message with user query for completion
        messages_with_system = SystemChatBot + messages

        completion = Client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages_with_system,  # Send combined messages
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = ""
        
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        # Append assistant's response to messages
        messages.append({"role": "assistant", "content": Answer})  # Assistant role set correctly

        # Save the updated messages to the JSON file
        with open(file_path, "w") as f:
            dump(messages, f, indent=4)
            
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, something went wrong."


if __name__ == "__main__":
    print("Welcome to the Chatbot")
    print("Type 'exit' to end the conversation")
    
    while True:
        Query = input("You: ")
        
        if Query.lower() == "exit":
            break
        
        Answer = ChatBot(Query)
        print(f"Assistant: {Answer}")
        
        if "date" in Query or "time" in Query:
            print(RealtimeInformation())
            
    print("Goodbye!")
