import pandas as pd
import re
import syllables
import csv
import json
import random



train_output_file = 'train.jsonl'
prompt_file = 'prompt.json'
test_output_file = 'test.jsonl'
file_path = 'spotify_millsongdata.csv'

def load_data(csv_file_path):
    origianl_data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            origianl_data.append(row)
    return origianl_data

    
def convert_data(datas, output_file_path):
    with open(output_file_path, 'w') as file:
        for data in datas:
            lyrics = data['text']
            lyrics = re.sub(r'\n\s*\n', '\n', lyrics)
            lyric_list = list(lyrics.split("\n"))
            syllable =""
            for i in range(len(lyric_list)):
                syllable += str(count_syllables(lyric_list[i]))
                if i != len(lyric_list) - 1:
                    syllable += "\n"
            title = data['song']
            question = f"You are a lyricist and will be working on translations. Given the title of a song and the syllable length of each line of the song, write English lyrics by replacing the words with words of similar syllable length. title: {title}, syllable: {syllable}"
            answer = lyrics
            new_data = {"messages": [{"role": "user", "content": question},{"role": "system", "content": answer}]}
            file.write(json.dumps(new_data))
            file.write("\n")




def count_syllables(text):
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
    words = text.split()
    result = 0
    for word in words:
        word = re.sub(r'^\W+|\W+$', '', word)
        if word.lower().strip() in contractions_syllables:
            syllable_count = contractions_syllables.get(word.lower().strip())
            result += syllable_count
        else:
            word = re.sub(r'^\W+|\W+$', '', word)
            syllable_count = syllables.estimate(word)
            result += syllable_count
            
        
    return result
