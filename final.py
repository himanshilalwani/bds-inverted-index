from mrjob.job import MRJob
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
import os
import json
import sys
from pymemcache.client.base import Client
import math
import nltk
from nltk.corpus import words
nltk.download('punkt')
nltk.download('words')

# Global Variables
NUM_DOCUMENTS = 10000
IP = 'localhost'
PORT = '11212'

# create a dictionary of valid words
english_words = set(words.words())
lowercase_words = [s.lower() for s in english_words]
stop_words = set(stopwords.words('english'))
# Connect to Memcached
try:
    mc = Client((IP,PORT))
    mc.flush_all() # flush all old key-value pairs
except ConnectionRefusedError:
    print("Please modify the IP and Port in the global varible section of the code")
    raise


class InvertedIndex(MRJob):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stemmer = SnowballStemmer('english')
        self.inverted_index = {}

    def mapper(self, _, line):
        # get the path of the current file being processed
        file_path = os.environ['map_input_file']
        # make sure the file path ends with .txt
        base_name, extension = os.path.splitext(file_path)
        if extension == '.txt':
            # tokenize the text into words using NLTK tokenizer
            tokenizer = RegexpTokenizer(r'\w+')
            words = tokenizer.tokenize(line)
            # emit key-value pairs where the key is the stemmed word and the value is the document ID and frequency
            for word in words:
                new_word = self.stemmer.stem(word.lower())
                if new_word.isalpha() and new_word not in stop_words and new_word in lowercase_words: # check if the word is a valid word in the dictionary
                    yield new_word, (file_path, 1)

    def reducer(self, word, document_frequencies):
        # Count the total number of documents that contain the word
        document_ids = set()
        # concatenate the document IDs and their frequencies into a dictionary
        document_dict = {}
        for document_id, frequency in document_frequencies:
            if document_id in document_dict:
                document_dict[document_id] += frequency
            else:
                document_dict[document_id] = frequency
            document_ids.add(document_id)

        document_count = len(document_ids)
        if document_count > 0:
            # Calculate the inverse document frequency (idf) for the word
            idf = math.log(NUM_DOCUMENTS / document_count)

            # Multiply the word frequency by idf and update the dictionary
            for document_id, frequency in document_dict.items():
                tf_idf = frequency * idf
                document_dict[document_id] = tf_idf

            # sort the document_dict items based on decreasing tf_idf scores
            sorted_document_dict = dict(sorted(document_dict.items(), key=lambda x: x[1], reverse=True))
            
            # Store the inverted index in memory
            self.inverted_index[word] = sorted_document_dict

    def reducer_final(self):
        # write the entire inverted index to Memcached
        mc.set_multi(self.inverted_index)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Incorrect Input. Usage: python3 final.py directory_or_file_name")
        sys.exit(1)
    directory_name = sys.argv[1]

    if os.path.isdir(directory_name) == False:
        if os.path.isfile(directory_name) == False:
            print(f"{directory_name} is not a valid directory / file.")
            sys.exit(1)

    InvertedIndex.run()

    while True:
        # prompt the user for a keyword
        keyword = input('Enter a keyword to be searched. Enter "exit0" to quit the interface. ')
        # check if the input is a single keyword
        while len(keyword.split()) != 1:
             keyword = input('Please enter a single word.')
        # if exit, break the loop
        if keyword == "exit0":
            break
        # search the inverted index for the keyword
        result = mc.get(keyword.split()[0].lower())
        if result:
            # decode the bytes object
            result = result.decode()
            # convert it to a dictionary
            result = eval(result)
            # display the top 10 documents
            for i, (document, score) in enumerate(result.items()):
                if i >= 10:
                    break
                print(f'{i+1}. {document} ({score:.4f})')
        else:
            print(f'No documents found for keyword "{keyword}".')


