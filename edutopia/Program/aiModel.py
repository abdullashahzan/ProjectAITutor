import os

from groq import Groq

# Keep it highly secure (DO NOT SHARE IT WITH ANYONE!)
client = Groq(
    api_key="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",
)

def ask_tutor(content):
    AI = "You are an AI tutor that is focused on helping students by explaining them their notes or making them short quizzes based on their notes. You are friendly and use simple language. You will do whatever the user asks you to do."
    info = {"role": "user", 
            "content": AI + " From here on all of this will be user input: " + content}
    chat_completion = client.chat.completions.create(
        messages=[info],
        model="mixtral-8x7b-32768",
    )
    return chat_completion.choices
    #return chat_completion.choices[0].message.content

def make_schedule(content):
    AI = "You are an AI scheduler that is focused on helping students by making schedules based on their subjects so that he does not face any pressure or has to attend too many quizzez in one day. You are friendly and use simple language. You will do whatever the user asks you to do."
    info = {"role": "user", 
            "content": AI + " From here on all of this will be user input: " + content}
    chat_completion = client.chat.completions.create(
        messages=[info],
        model="mixtral-8x7b-32768",
    )
    return chat_completion.choices[0].message.content
    #return chat_completion.choices[0].message.content

def evaluate_student(content):
    AI = "You are an AI evaluater that evaluates student based on how they perform. Your job is to make quizzez or exams related to student's notes that they will solve and you will have to evaluate based on that. You are very creative. Come up with new ideas that are unique to evaluate students and then ask the user these questions that you came up with."
    AI2 = "You are an AI evaluater that evaluates student based on how they perform. Your job is to make quizzez or exams related to student's notes that they will solve and you will have to evaluate based on that. You are very creative. Come up with new ideas that are unique to evaluate student."
    info = {"role": "user", 
            "content": AI2 + " From here on all of this will be user input: " + content}
    chat_completion = client.chat.completions.create(
        messages=[info],
        model="mixtral-8x7b-32768",
    )
    return chat_completion.choices[0].message.content
    #return chat_completion.choices[0].message.content


