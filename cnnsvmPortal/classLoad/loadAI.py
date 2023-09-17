import numpy as np
import joblib
from keras.models import load_model
from keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences

class cnnSVM:
    def __init__(self, cnnLoc, svmLoc, tokenLoc):
        self.cnnLoc = cnnLoc
        self.svmLoc = svmLoc
        self.tokenLoc = tokenLoc

    def performJudgement(self, text_input):

        loaded_cnn_model = load_model(self.cnnLoc)
        loaded_svm_model = joblib.load(self.svmLoc)
        tokenizer = joblib.load(self.tokenLoc)

        X_test = text_input
        max_sequence_length = 200

        X_test_sequences = tokenizer.texts_to_sequences(X_test)
        X_test_padded = pad_sequences(X_test_sequences, maxlen=max_sequence_length)


        loaded_cnn_model = Sequential(loaded_cnn_model.layers[:-1])
        X_test_cnn_features = loaded_cnn_model.predict(X_test_padded)

        y_pred = loaded_svm_model.predict(X_test_cnn_features)

        loaded_cnn_model = None
        loaded_svm_model = None
        tokenizer = None

        return y_pred