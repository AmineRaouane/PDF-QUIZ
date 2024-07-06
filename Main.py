import requests
import streamlit as st
import os
import json
import time
from Processing_classes.Data_processor import Document_Processor
from Processing_classes.Chroma_creator import Chroma_collection_creator
from Processing_classes.Embedding import EmbeddingClient
from Processing_classes.Quiz_generator import QuizGenerator
import streamlit.components.v1 as components

st.set_page_config(
    page_title="My Streamlit App",
    page_icon=":rocket:",
    layout="wide"
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GOOGLE_APPLICATION_CREDENTIALS.json"

Flask_url = "http://localhost:5000/"

Scoring_system = {
    'Easy' : lambda time:1,
    'Medium' : lambda time:0.2 * (1+(30 - time) // 5),
    'Hard' : lambda time:1/(1+0.1*time**1.1)
}

mapping = {
    'A':0,
    'B':1,
    'C':2,
    'D':3,
    'E':4,
    }

def next_question(answer=None,Time=30):
    if answer:
        st.session_state['User_Answers'][st.session_state['i']] = (answer,Time)
    if st.session_state['i'] < len(st.session_state['questions']) - 1:
        st.session_state['i'] += 1
    else:
        st.session_state['i'] = -1
        
def Restart():
    st.session_state['Quiz_mode'] = False
    st.session_state['User_Answers'] = []
    st.session_state['i'] = 0
    st.session_state['questions'] = []
    st.session_state['n_questions'] = 4
    st.session_state['n_choices'] = 4
    st.session_state['topic_input'] = None
    st.session_state['Difficulty'] = 'Easy'

def Display_All_questions(Z):
    st.html('''
            <style>
                .e1f1d6gn2 div:nth-last-child(1) {
                    margin-top: auto;
                }
            
                .e1nzilvr4{
                    text-align: center;
                }

                .e1nzilvr4 p{
                    font-size: 20px;
                }
            </style>
            ''')
    for index in range(0,len(st.session_state['questions']),2):
        A,B = Z.columns(2)
        question1 ,question2 = st.session_state['questions'][index],st.session_state['questions'][index+1]
        with A.container(border=True):
            st.header(f"Question {index+1}")
            st.markdown(question1["question"])
            user_Answer = st.session_state['User_Answers'][index]
            if user_Answer == question2['answer']:
                st.success("Correct")
            else:
                st.error("Wrong Answer")
            st.radio("Your Answer was:",[f"{choice['key']}. {choice['value']}" for choice in question1["choices"]],index=mapping.get(user_Answer,None),disabled=True)
            with st.popover("See the Answer here",use_container_width=True):
                st.write(f"Correct answer: {question1['answer']}")
                st.html(f"<p class='Explanation'>Explanation: {question1['explanation']}</p>")
        with B.container(border=True):
            st.header(f"Question {index+2}")
            st.markdown(question2["question"])
            user_Answer = st.session_state['User_Answers'][index]
            if user_Answer == question2['answer']:
                st.success("Correct")
            else:
                st.error("Wrong Answer")
            st.radio("Your Answer was:",[f"{choice['key']}. {choice['value']}" for choice in question2["choices"]],index=mapping.get(user_Answer,None),disabled=True)
            with st.popover("See the Answer here",use_container_width=True):
                st.write(f"Correct answer: {question2['answer']}")
                st.html(f"<p class='Explanation'>Explanation: {question2['explanation']}</p>")

@st.experimental_fragment
def Radio_buttons(question):
    user_Answer = st.radio("Choose your Answer :",[f"{choice['key']}. {choice['value']}" for choice in question["choices"]],index=None)
    return user_Answer

def Display_question():
    st.session_state["Time"] = 0
    _,Z,_ = st.columns([1,7,1])
    if st.session_state['i'] + 1 :
        question_container = Z.container(border=True)
        i = st.session_state['i']
        question = st.session_state['questions'][i]
        Time_bar = question_container.progress(100, text="Embedding files...")
        question_container.title(f"Question {i+1}")
        question_container.html(f"<div class='Question'>{question['question']}</div>")
        with question_container:
            user_Answer = Radio_buttons(question)
            
        
        answer = user_Answer[0] if user_Answer else None

        question_container.button('Next',on_click=next_question,args=(answer,st.session_state["Time"])) # type: ignore

        for i in range(31) :
            st.session_state["Time"] += 1
            time.sleep(1)  # Wait for 1 second
            progress_value = 100 - ((i + 1) * (100 / 30))
            Time_bar.progress(int(progress_value)) 
            if i == 29:  # Trigger next_question at the end of countdown
                next_question()
                st.rerun()
    else:
        _,Z_middle,_ = Z.columns([1,3,1])
        Z_middle.write("Congratulations! You have finished the quiz.")
        score = 0
        for index,answer in enumerate(st.session_state['User_Answers']):
            if answer and answer[0] == st.session_state['questions'][index]['answer']:
                score += Scoring_system[st.session_state['Difficulty']](answer[1])
        Final_score = int(100*score/len(st.session_state['questions']))
        if Final_score >= 70 :
            Z_middle.success(f"Your score is {Final_score}% you have passed the quiz")
        elif Final_score >= 40 :
            Z_middle.warning(f"Your score is {Final_score}% you need some improvements")
        else:
            Z_middle.error(f"Your score is {Final_score}% you need to study more")
        
        Display_All_questions(Z)

        _,E,_ =  Z.columns([1,0.8,1],vertical_alignment='center')
        E.button("return to home page",on_click=Restart,use_container_width=True)

def handle_quizz_generation(topic_input,n_questions,n_choices,Difficulty,col):
    st.session_state['n_questions'] = n_questions
    st.session_state['n_choices'] = n_choices
    st.session_state['topic_input'] = topic_input
    st.session_state['Difficulty'] = Difficulty
    quiz_generator = QuizGenerator(topic_input, n_questions, chroma_creator,n_choices,Difficulty)
    if quiz_generator:
        response = quiz_generator.generate_question_with_vectorstore()
        try:
            response = json.loads(response)
            if response :
                col.toast("Quiz generated successfully",icon="✅",)
                time.sleep(2)
                st.session_state['questions'] = response
                st.session_state['User_Answers'] = [None for _ in range(n_questions)]
                st.session_state['Quiz_mode'] = True
                st.session_state['i'] = 0
        except:
            st.error("Error: Invalid JSON response.")
    else:
        st.error("No results found.")


st.html("<div class='title'>PDF Quizz</div>")
st.html("Styles/style.html")

if 'Quiz_mode' not in st.session_state:
    st.session_state.Quiz_mode=False
if 'User_Answers' not in st.session_state:
    st.session_state['User_Answers'] = []
    


if st.session_state['Quiz_mode']:
    Display_question()
else :
    _,A,_ =  st.columns([1,5,1],vertical_alignment='center')
    with A.form("form1"):
        uploaded_files = st.file_uploader("Insert your files here", type='pdf', accept_multiple_files=True, key="pdf_uploader")

        _,B,_ =  st.columns([1,0.8,1],vertical_alignment='center')
        Submit = B.form_submit_button("Submit",use_container_width=True)
        if Submit:
            if uploaded_files :
                files = [("files", (file.name, file.getvalue())) for file in uploaded_files]
                response = requests.post(f"{Flask_url}upload", files=files)
                if response.status_code == 200:
                    st.success("Files uploaded successfully and stored in the database.")
                else:
                    st.error("Failed to upload files.")
                st.session_state['uploaded_files'] = uploaded_files
                with st.status("Please wait while the data is being processed..."):
                    st.write("Processing")
                    processed_pages = Document_Processor(st.session_state['uploaded_files'])
                    st.write("Embedding")
                    chroma_creator = Chroma_collection_creator(EmbeddingClient())
                    st.write("storing")
                    chroma_creator.create_chroma_collection(processed_pages)
                st.session_state['chroma_creator'] = chroma_creator
                st.toast("Files uploaded successfully",icon="✅")
            else :
                    st.error("Please upload a file.")

    with A.form("form2"):
        topic_input = st.text_input(label='Topic for Generative Quiz', placeholder='Enter the topic of the document')
        col1,col2 = st.columns(2)
        n_questions = col1.number_input(label='Number of Questions',value=4,min_value=2,max_value=12,step=2)
        n_choices = col2.number_input(label='Number of Choices',value=4,min_value=2,max_value=5)
        Difficulty = st.selectbox(label='Difficulty',options=['Easy','Medium','Hard'])

        _,C,_ =  st.columns([1,0.8,1],vertical_alignment='center')
        Generate_Quiz = C.form_submit_button("Generate Quiz",use_container_width=True,on_click=handle_quizz_generation,args=(topic_input,n_questions,n_choices,Difficulty,A))

with st.sidebar:


    response = requests.get(f"{Flask_url}files")
    if response.status_code == 200:
        files_list = response.json()
        if files_list:
            # Create download buttons for each file
            for file in files_list:
                file_id = file['id']
                file_name = file['name']
                download_url = f"{Flask_url}download/{file_id}"
                file_data = requests.get(download_url).content
                st.download_button(label=f"Download {file_name}", 
                                   data=file_data, 
                                   file_name=file_name,
                                   use_container_width=True,
                                   key = file_id)
