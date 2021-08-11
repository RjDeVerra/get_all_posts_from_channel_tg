import nltk
import pymorphy2
from nltk import word_tokenize

#nltk.download('punkt')

# probability score threshold
prob_thresh = 0.4

morph = pymorphy2.MorphAnalyzer()

text = """
Александр Невский
"""

for word in nltk.word_tokenize(text):
    for p in morph.parse(word):
        if 'Name' in p.tag and p.score >= prob_thresh:
            print('{:<12}\t({:>12})\tscore:\t{:0.3}'.format(word, p.normal_form, p.score))