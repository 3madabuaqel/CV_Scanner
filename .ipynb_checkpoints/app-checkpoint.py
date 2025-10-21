from flask import Flask, request, render_template
import pickle

app = Flask(__name__)


rf_classifier_categorization = pickle.load(open('models/rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open('models/tfidf_vectorizer_categorization.pkl', 'rb'))


@app.route('/')
def resume():
    return render_template('resume.html')


@app.route('/pred', methods=['POST'])
def perd():
    if 'resume' in request.files:
        file - request.files['resume']
        filename = file.filename
    
        if filename.endswith('.pdf'):
            pass
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return render_template('resume.html', message='Invalid file format, please upload a .pdf or .txt file')

# main
if __name__ == '__main__':
    app.run(debug=True)