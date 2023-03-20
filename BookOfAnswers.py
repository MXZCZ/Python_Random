import random

class BookOfAnswers:
    def __init__(self):
        self.answers = [
            "Yes, definitely.",
            "No, absolutely not.",
            "Maybe, it depends.",
            "It's uncertain.",
            "Only time will tell.",
            "Ask again later.",
            "You must decide.",
            "Follow your instincts.",
            "It's a possibility.",
            "The answer lies within.",
            # Add more random answers as needed
        ]

    def ask_question(self, question):
        answer = random.choice(self.answers)
        return answer

def main():
    book_of_answers = BookOfAnswers()
    print("Welcome to the Book of Answers! Type 'quit' to exit.")
    while True:
        user_question = input("Please enter your question: ")
        if user_question.lower() == 'quit':
            break
        response = book_of_answers.ask_question(user_question)
        print(response)

if __name__ == "__main__":
    main()
