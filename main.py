import json
from difflib import get_close_matches
import sqlite3

#database script to create a new database
conn = sqlite3.connect(":memory:")
#conn = sqlite3.connect("coursesDB.db")
#"coursesDB.db" creates a seperate database file whereas
#":memory:" creates a database everytime the program is run
c = conn.cursor()
#creating a new table
c.execute('''CREATE TABLE courses
          (name TEXT,  type TEXT)''')
#inserting values into the table
courses = [
    ("Software Engineering", "BEng (Hons)"),
    ("Data Science", "BSc (Hons)"),
    ("Computer Science", "BSc (Hons)"),
    ("Robotics with Artificial Intelligence", "MSc"),
    ("Data Analytics", "MSc"),
    ("Cyber Security", "MSc"),
]
c.executemany('INSERT INTO courses VALUES (?, ?)', courses)
conn.commit
#displaying the relevant data in the database
c.execute('SELECT * FROM courses')
displayCourseInfo = c.fetchall()

#defining a function to load the knowledge base for the chat bot
def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

#defining a function to save the dictionary to the knowledge base (saving/learning new information)
def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

#defining a function to find the best match from the dictionary for the user's question
def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None
    
#defining a function to get/reply with the answer for each question
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
        
#"questions" defined here are essentially "intents", which are the
#goals that the user has when they're sending a message to the chatbot

#creating the main script      
def chat_bot():
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')

    #defining an infinite loop that will constantly run and process user input until the user types "quit"
    while True:
        user_input: str = input('You: ')

        if user_input.lower() == 'quit':
            break
        
        #defining the best match
        best_match: str | None = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

        #obtaining information from the database
        if user_input.lower() == 'what are the available courses?':
            print(displayCourseInfo)

        #finding the best match for the user's input from the knowledge base
        elif best_match:
            answer: str = get_answer_for_question(best_match, knowledge_base)
            print(f'Bot: {answer}')
        #if the best match cannot be found, the bot will request the user to teach it
        else:
            print('Bot: I don\'t know the answer. Can you please teach me?')
            new_answer: str = input('Type the answer or "skip" to skip: ')

            #the bot will add the new response into the knowledge base and save it, learning new information
            if new_answer.lower() != 'skip':
                knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                save_knowledge_base('knowledge_base.json', knowledge_base)
                print('Bot: Thank you! I learned a new response!')

#running the chat bot
if __name__ == '__main__':
    chat_bot()
