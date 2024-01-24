import string
import pickle
import re
from pathlib import Path

import tensorflow as tf
import numpy as np


strip_chars = string.punctuation
strip_chars = strip_chars.replace("[", "")
strip_chars = strip_chars.replace("]", "")

 
def custom_standardization(input_string):
    lowercase = tf.strings.lower(input_string)
    return tf.strings.regex_replace(
        lowercase, f"[{re.escape(strip_chars)}]", "")
    
    
max_tokens = 25_000
sequence_length = 30


embed_dim = 128
dense_dim = 4 * embed_dim
num_heads = 8
encoder_layers = 4
decoder_layers = 4


def load_text_vectorization(path, standardize=None):
    from_disk = pickle.load(open(path, "rb"))
    new_v = tf.keras.layers.TextVectorization.from_config(from_disk['config'])
    if standardize:
        new_v._standardize = standardize
    new_v.adapt(tf.data.Dataset.from_tensor_slices(["xyz"]))
    new_v.set_weights(from_disk['weights'])
    return new_v




class Translator:
    
    def __init__(self, model_dir):
        model_dir = Path(model_dir)
        self.source_vectorization = load_text_vectorization(str(model_dir / 'source_vec.pkl'))
        self.target_vectorization = load_text_vectorization(str(model_dir / 'target_vec.pkl'), custom_standardization)
        self.transformer = tf.keras.models.load_model(str(model_dir / 'full_model'))
    
    def __call__(self, pl_text):
        output = self.decode_sequence(pl_text)
        if output.startswith('[start]'):
            output = output[7:]
        if output.endswith('[end]'):
            output = output[:-5]
        return output.strip()
        


    def decode_sequence(self, input_sentence):
        target_vocab = self.target_vectorization.get_vocabulary()
        target_index_lookup = dict(zip(range(len(target_vocab)), target_vocab))
        max_decoded_sentence_length = 30
        
        tokenized_input_sentence = self.source_vectorization([input_sentence])
        decoded_sentence = "[start]"
        for i in range(max_decoded_sentence_length):
            tokenized_target_sentence = self.target_vectorization(
                [decoded_sentence])[:, :-1]
            predictions = self.transformer(
                {'source': tokenized_input_sentence, 'target': tokenized_target_sentence})
            sampled_token_index = np.argmax(predictions[0, i, :])
            sampled_token = target_index_lookup[sampled_token_index]
            decoded_sentence += " " + sampled_token
            if sampled_token == "[end]":
                break
        return decoded_sentence
