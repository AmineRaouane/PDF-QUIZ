Initial_Prompt = '''
You are a subject matter expert on the topic: {topic}
            
Follow the instructions to create num_questions quiz questions:
1. Generate num_questions unique Difficulty questions based on the topic provided and context as a list of key "questions"
2. For each question, provide n_choices multiple choice answers as a list of key-value pairs "choices"
3. Provide the correct answer for each question from the list of answers as key "answer"
4. Provide an explanation for each question as to why the answer is correct as key "explanation"
            
You must respond as a JSON list that can be decoded by the json.loads method, structured as follows:
[
    {{
        "question": "<question>",
        "choices": [
            {{"key": "A", "value": "<choice>"}},
            {{"key": "B", "value": "<choice>"}},
            ...
        ],
        "answer": "<answer key from choices list>",
        "explanation": "<explanation as to why the answer is correct>"
    }},
    ...
]
            
Context: {context}
'''
