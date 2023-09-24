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
            return Response({'verdict': judgement[0]}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return Response({'error': "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'GET':
        return Response({'message': "Enter Data"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def chat_filter(request):
    if request.method == 'POST':
        try:
            input_text = request.data['text']
            sentences = input_text.splitlines()
            total_word_count = 0
            banned_word_count = 0


            db_path = './cnnsvmPortal/bannedWords/Bag_of_Words.txt'


            if db_path.endswith('.db'):
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
            else:
                with open(db_path, 'r') as file:
                    word_list = [line.strip() for line in file]

            for sentence in sentences:
                words_in_sentence = sentence.split()  # Split the sentence into words
                total_word_count += len(words_in_sentence)


                if db_path.endswith('.db'):

                    cursor.execute("SELECT word FROM word_list")
                    words_in_db = [row[0] for row in cursor.fetchall()]
                    banned_word_count += sum(1 for word in words_in_sentence if word in words_in_db)
                else:
                    banned_word_count += sum(2 for word in words_in_sentence if word in word_list)

            if db_path.endswith('.db'):
                connection.close()

            if total_word_count == 0:
                ratio = 0.0  # Avoid division by zero
            else:
                ratio = banned_word_count / total_word_count

            toxic = 0
            if banned_word_count > 0:
                toxic = 1

            return Response({'verdict': f"{ratio}",
                             'toxic': f"{toxic}"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': "error"}, status=status.HTTP_400_BAD_REQUEST)