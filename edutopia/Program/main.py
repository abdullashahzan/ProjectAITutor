import notesReader, aiModel

def main():
    print("Hello! How can I help you today? (Type 'attach notes' to attach notes, 'remove notes' to remove notes, and press Enter to exit)")
    doc = ""
    while True:
        user = input("\nYou: ")
        print("-"*50)
        if user == "":
            print("Goodbye! Have a nice day.")
            break
        elif user == "attach notes":
            doc = input("Please attach your notes. I can read pdf, ppt, pptx, jpeg, png, txt and everything that is text based.\n(Enter the file path): ")
            doc = notesReader.extract_text_from_file(doc)
            print("Notes attached successfully! Ask me anything.")
        elif user == "remove notes":
            doc = ""
            print("Notes removed successfully!")
        else:
            response = aiModel.ask_tutor(doc + " " + user)
            print("AI tutor: \n" + response[0].message.content)

def evaluator():
    while True:
        print("Welcome! How can I help you today?")
        print("1. Make a schedule")
        print("2. Evaluate")
        ask_user = input("Enter 1 or 2: ")
        if ask_user == "1":
            doc = input("Please attach a document that contains subjects, time period of the semester and course material. I can read pdf, ppt, pptx, jpeg, png, txt and everything that is text based.\n(Enter the file path): ")
            doc = notesReader.extract_text_from_file(doc)
            print(aiModel.make_schedule(doc))
        elif ask_user == "2":
            doc = input("Please attach all the notes on which the student should be evaluated on. I can read pdf, ppt, pptx, jpeg, png, txt and everything that is text based.\n(Enter the file paths seprated by '--'): ")
            doc = notesReader.extract_text_from_file(doc)
            print(aiModel.evaluate_student(doc))
        elif ask_user == "":
            break
        else:
            print("Invalid input")


ask_dev = input("What would you like to run 1) AI tutor or 2) AI Evaluator: ")
if ask_dev == "1":
        main()
elif ask_dev == "2":
    evaluator()
else:
    print("Invalid input")