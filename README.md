# Inverted Index Generation with MapReduce
This project implements a MapReduce job to create an inverted index for a corpus of text documents. The inverted index allows efficient searching and retrieval of documents based on keywords. The code utilizes the MRJob library and the Natural Language Toolkit (NLTK) for text preprocessing tasks such as tokenization, stemming, and stop word removal. Additionally, it leverages the pymemcache library to store the inverted index in memory and provide a search interface for users.

## Instructions
- Open a terminal or command prompt.
- Navigate to the directory where final.py is located.
- Run the code by executing the following command: `python3 final.py`

## Project Structure
The code is organized in a single file, `final.py`, which contains the complete implementation of the MapReduce job for generating the inverted index.

## Workflow
The code follows a workflow that includes the following steps:
- Text preprocessing: The code tokenizes, stems, and removes stop words from the input text documents using NLTK libraries.
- MapReduce job: The code employs the MRJob library to perform the MapReduce job. It maps the words to their document IDs and frequencies and reduces them to generate the inverted index.
- Inverted Index Storage: The code utilizes the pymemcache library to store the inverted index in memory for efficient retrieval and searching.
- Search Interface: After the inverted index is generated, the code provides a search interface where users can enter keywords and retrieve relevant documents based on their tf-idf scores.
- Performance Optimization: The code optimizes performance by storing the inverted index in memory and using bulk operations to write it to the Memcached server.

## Dependencies
The code relies on the following dependencies:
- `MRJob`: Library for implementing MapReduce jobs in Python.
- `NLTK`: Natural Language Toolkit for text preprocessing tasks. 
- `pymemcache`: Library for interacting with the Memcached server.
Please ensure that these dependencies are installed before running the code.
 
