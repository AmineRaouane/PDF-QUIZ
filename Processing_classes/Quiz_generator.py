from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
import os
from Processing_classes.Prompt import Initial_Prompt

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None,n_choices=3,Difficulty='Easy'):
        self.topic = topic if topic else "General Knowledge"
        self.vectorstore = vectorstore
        self.llm = None

        initial_prompt = Initial_Prompt.replace("num_questions", str(num_questions))
        initial_prompt = initial_prompt.replace("n_choices", str(n_choices))
        initial_prompt = initial_prompt.replace("Difficulty", Difficulty)
        self.system_template = initial_prompt

    def init_llm(self,temperature=0.3,max_output_tokens=1000):
        self.llm = VertexAI(
            model_name='gemini-pro',
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )


    def generate_question_with_vectorstore(self):
        
        self.init_llm()

        if not self.vectorstore:
            raise ValueError("Vectorstore is empty.")
        
        retriever = self.vectorstore.db.as_retriever()

        prompt = PromptTemplate.from_template(self.system_template)

        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )

        chain = setup_and_retrieval | prompt | self.llm #type:ignore
        response = chain.invoke(self.topic)

        return response
    