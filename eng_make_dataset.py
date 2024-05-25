mport pandas as pd
import re
import syllables
import csv



train_output_file = 'train.jsonl'
test_output_file = 'test.jsonl'
file_path = 'spotify_millsongdata.csv'

contractions_syllables = {
        "you're": 1,
        "i'm": 1,
        "we're": 1,
        "they're": 1,
        "you've": 1,
        "i've": 1,
        "we've": 1,
        "they've": 1,
        "can't": 1,
        "won't": 1,
        "don't": 1,
        "didn't": 2,
        "isn't": 2,
        "aren't": 2,
        "wasn't": 2,
        "weren't": 2,
        "couldn't": 2,
        "shouldn't": 2,
        "wouldn't": 2,
        "hasn't": 2,
        "haven't": 2,
        "hadn't": 2,
        "it's": 1,
        "that's": 1,
        "there's": 1,
        "here's": 1,
        "what's": 1,
        "let's": 1,
    }

def load_data(csv_file_path):
    origianl_data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            origianl_data.append(row)
    return origianl_data


def convert_data(datas):
    dataset = []
    for data in datas:
        lyrics = data['text']
        title = data['song']
        syllable = count_syllables(lyrics)
        question = f"Given a syllable structure and title of the song, write English lyrics that match it. title: {title}, syllable: {syllable}"
        answer = lyrics
        new_data = {
                "messages": [
                    {"role": "user", "content": question},
                    {"role": "system", "content": answer}
                ]
            }
    dataset.append(new_data)
    return dataset




def count_syllables(text):
    
    words = text.split()
    result = ""
    for word in words:
        word = re.sub(r'^\W+|\W+$', '', word)
        if word.lower().strip() in contractions_syllables:
            syllable_count = contractions_syllables.get(word.lower().strip())
            result += f"{syllable_count}-"
        else:
            word = re.sub(r'^\W+|\W+$', '', word)
            syllable_count = syllables.estimate(word)
            result += f"{syllable_count}-"


    return result[:-1]