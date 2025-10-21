from flask import Flask, request, render_template 
import pickle
from PyPDF2 import PdfReader
import re
from requirement import skills_list, education_keywords

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

# load models
rf_classifier_categorization = pickle.load(open('models/rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open('models/tfidf_vectorizer_categorization.pkl', 'rb'))

rf_classifier_job_recommendation = pickle.load(open('models/rf_classifier_job_recommendation.pkl', 'rb'))
tfidf_vectorizer_job_recommendation = pickle.load(open('models/tfidf_vectorizer_job_recommendation.pkl', 'rb'))

# pdf to text
def pdf_to_text(file):
    reader = PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# clean resume text
def cleanResume(txt):
    cleanText = re.sub(r'http\S+\s', ' ', txt)  # Match URLs
    cleanText = re.sub(r'RT|cc', ' ', cleanText)  # Remove 'RT' and 'cc'
    cleanText = re.sub(r'#\S+\s', ' ', cleanText)  # Remove hashtags
    cleanText = re.sub(r'@\S+', '  ', cleanText)  # Remove mentions
    cleanText = re.sub(r'[!"#$%&\'()*+,-./:;<=>?@\[\]^_`{|}~]', ' ', cleanText)  # Remove punctuation
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)  # Remove non-ASCII characters
    cleanText = re.sub(r'\s+', ' ', cleanText)  # Normalize whitespace
    return cleanText

# predict category name
def predict_category(resume_text):
    resume_text= cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_categorization.transform([resume_text])
    predicted_category = rf_classifier_categorization.predict(resume_tfidf)[0]
    return predicted_category

# predict job recommendation 
def job_recommendation(resume_text):
    resume_text= cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
    recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
    return recommended_job

# -----------------------------------------------------------------------------------------------

# resume extraction functions
def extract_contact_number_from_resume(text):
    contact_number = None
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()
        return contact_number
    return 'Contact number not found'

def extract_email_from_resume(text):
    email = None
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    match = re.search(pattern, text)
    if match:
        email = match.group()
        return email
    return 'Email not found'


def extract_skills_from_resume(text):
    skills = []
    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)

    return skills


def extract_education_from_resume(text):
    education = []
    for keyword in education_keywords:
        pattern = r"\b{}\b".format(re.escape(keyword))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            education.append(keyword)

    return education



def extract_name_from_resume(text):
    # Regex for matching first and last names (two words, capitalized)
    name_pattern = r"^[A-Z][a-zA-Z'-]+(?: [A-Z][a-zA-Z'-]+)*$"
    
    # Split text into lines and check each line
    for line in text.split("\n"):
        line = line.strip()
        if re.match(name_pattern, line):
            return line
        elif re.search('Name:', line):
            name = line.split(':')
            return name[1].strip()
    return "Name not found"


@app.route('/')
def resume():
    return render_template('resume.html')



@app.route('/pred', methods=['POST'])
def perd():
    if 'resume' in request.files:
        file = request.files['resume']
        filename = file.filename
    
        if filename.endswith('.pdf'):
            text = pdf_to_text(file)
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return render_template('resume.html', message='Invalid file format, please upload a .pdf or .txt file')


        predicted_category = predict_category(text)
        recommended_job = job_recommendation(text)
        phone_number = extract_contact_number_from_resume(text) 
        email = extract_email_from_resume(text)
        extracted_skills = extract_skills_from_resume(text)
        
        extracted_education = extract_education_from_resume(text)
        name = extract_name_from_resume(text)
        

        
        return render_template('resume.html', predicted_category = predicted_category, recommended_job = recommended_job
                               , phone_number = phone_number, email = email, extracted_skills = extracted_skills
                               , extracted_education = extracted_education, name = name)
    else:
        return render_template('resume.html', message='please upload resume')






    
if __name__ == '__main__':
    app.run(debug=True)