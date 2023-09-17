import json
import sqlite3
from rest_framework.decorators import api_view
from .classLoad import loadAI
from rest_framework.response import Response
from rest_framework import status


cnnLoc = './cnnsvmPortal/AImodels/cnn_model_proper.h5'
svmLoc = './cnnsvmPortal/AImodels/svm_model_proper.pkl'
tokenizerloc = './cnnsvmPortal/AImodels/tokenizer_proper.pkl'

aiLogic = loadAI.cnnSVM(cnnLoc, svmLoc, tokenizerloc)

# Sample json input
# {
#     "text": ["This is the text you want to analyze.",
# 	"you are stupid", "YOU ARE A NIGGER"
# 	]
# }

@api_view(['POST','GET'])
def aiInference(request):
    if request.method == 'POST':
        try:
            data = request.data['text']
            judgement = aiLogic.performJudgement(data)
            return Response({'verdict': judgement}, status=status.HTTP_200_OK)
        except:
            return Response({'error': "Wrong format JSON"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        return Response({'message': "Enter Data"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def chat_filter(request):
    if request.method == 'POST':
        try:
            input_text = request.data['text']
            sentences = input_text.splitlines()  # Split input into sentences
            total_word_count = 0
            banned_word_count = 0

            # Define the path to your SQLite database or text file containing the words
            db_path = './cnnsvmPortal/bannedWords/wordsSql.db'  # Replace with the actual path

            # Open the SQLite database connection or text file
            if db_path.endswith('.db'):
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
            else:
                with open(db_path, 'r') as file:
                    word_list = [line.strip() for line in file]

            for sentence in sentences:
                words_in_sentence = sentence.split()  # Split the sentence into words
                total_word_count += len(words_in_sentence)

                # Check if any word in the sentence is in the database or text file
                if db_path.endswith('.db'):
                    # Assuming you have a table named 'word_list' with a 'word' column in your SQLite database
                    cursor.execute("SELECT word FROM word_list")
                    words_in_db = [row[0] for row in cursor.fetchall()]
                    banned_word_count += sum(1 for word in words_in_sentence if word in words_in_db)
                else:
                    banned_word_count += sum(1 for word in words_in_sentence if word in word_list)

            if db_path.endswith('.db'):
                connection.close()  # Close the SQLite database connection if opened

            # Calculate the ratio of banned words to total words
            if total_word_count == 0:
                ratio = 0.0  # Avoid division by zero
            else:
                ratio = banned_word_count / total_word_count

            return Response({'ratio': f"{ratio}"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': "error"}, status=status.HTTP_400_BAD_REQUEST)