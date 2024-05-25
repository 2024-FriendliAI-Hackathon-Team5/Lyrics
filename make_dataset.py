import pandas as pd
import re
import syllables
import csv
import json
import random

en_train_output_file = 'en_train.jsonl'
en_test_output_file = 'en_test.jsonl'
en_train_output_file = 'kr_train.jsonl'
en_test_output_file = 'kr_test.jsonl'
en_file_path = 'spotify_millsongdata.csv'
kr_file_path = 'kr_lyrics_data.csv'

ending = "Suggestion:"
frame_prompt = """Suggest a single line of Korean lyric that matches with given syllables,lyrics, and title.
Ensure to avoid repeating previous lyrics. Focus on creative and original expression.
Match the length of the sentence to the syllables I provide as closely as possible.
For example, if Syllables: 7 given, you should write a 6~8 letter korean sentence.
Your answer should feel like soft, trendy K-pop lyrics without any profanity.
Your answer should be short, and only composed with a single sentence.
Answer with a single line of lyrics you created, and nothing else.

Here,
Title: {title} 
Syllables: {syllables}
Previous Lyrics: {lyric}

Your korean lyric that should be added to the previous lyrics:
"""

languages = ["Korean", "English", "Korean with English"]

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

def split_korean_english(word):
    korean_part = re.findall(r'[\uAC00-\uD7A3]+', word)
    english_part = re.findall(r'[a-zA-Z0-9]+', word)
    return ''.join(korean_part), ''.join(english_part)

def identify_language(word):
    korean_part, english_part = split_korean_english(word)
    
    if korean_part and english_part:
        return "Korean with English"
    elif korean_part:
        return "Korean"
    elif english_part:
        return "English"
    else:
        return "Unknown"

def count_syllables(text):
    lines = text.split('\n')
    result = ""
    count = 0

    for line in lines:
        words = line.split()
        line_result = ""
        line_count = 0
        for word in words:
            if word == "":
                continue
            korean_part, english_part = split_korean_english(word)
            syllable_count = 0
            if korean_part:
                syllable_count += count_korean_syllable(korean_part)
            if english_part:
                syllable_count += count_english_syllable(english_part)
            line_result += f"{syllable_count}-"
            line_count += syllable_count
        if line_result:
            result += line_result[:-1]
            result += '\n'
        if line_count:
            count += line_count

    #return result.rstrip('\n')
    return count

def is_korean(word):
    return bool(re.search(r'[\uAC00-\uD7A3]', word))

def count_english_syllable(word):
    word = re.sub(r'^\W+|\W+$', '', word)
    if word.lower().strip() in contractions_syllables:
        syllable_count = contractions_syllables.get(word.lower().strip())
    else:
        word = re.sub(r'^\W+|\W+$', '', word)
        syllable_count = syllables.estimate(word)
    return syllable_count

def count_korean_syllable(word):
    return len(word)

def save_data(data, output_file):
    with open(output_file, 'w') as file:
        for line in data:
            file.write(f"{str(line)}\n")


def generate_kr_lyrics_data(infile, trainfile, testfile):
    df = pd.read_csv(infile, usecols=['title', 'lyric', 'year'])
    df = df[df['year'] >= 2010]

    # shuffle data
    df = df.sample(frac=1).reset_index(drop=True)
    
    # train:test = 8:2
    train_size = int(len(df) * 0.4)
    test_size = int(len(df) * 0.5)
    train_df = df[:train_size]
    test_df = df[train_size:test_size]

    with open(trainfile, 'w', encoding='utf-8') as train_outfile, open(testfile, 'w', encoding='utf-8') as test_outfile:
        for index, row in train_df.iterrows():
            title = row['title']
            lyric = row['lyric']
            if pd.isna(title) or pd.isna(lyric):
                continue

            lines = lyric.split('\n')
            completed_lyric = ""
            for line in lines:
                syllable = count_syllables(line)
                if syllable:
                    language = identify_language(line)
                    prompt = frame_prompt.format(title=title, lyric=completed_lyric, syllables=syllable)
                    train_outfile.write(json.dumps({"messages": [{"role": "user", "content": prompt}, {"role": "system", "content": line}]}) + "\n")
                    completed_lyric += line + '\n'
        
        for index, row in test_df.iterrows():
            title = row['title']
            lyric = row['lyric']
            if pd.isna(title) or pd.isna(lyric):
                continue

            lines = lyric.split('\n')
            completed_lyric = ""
            language = random.choice(languages)
            for line in lines:
                syllable = count_syllables(line)
                if syllable:
                    language = identify_language(line)
                    prompt = frame_prompt.format(title=title, lyric=completed_lyric, syllables=syllable, language=language)
                    test_outfile.write(json.dumps({"messages": [{"role": "user", "content": prompt}, {"role": "system", "content": line}]}) + "\n")
                    completed_lyric += line + '\n'

generate_kr_lyrics_data(kr_file_path, 'train.jsonl', 'test.jsonl')
ex_lyric = """
example
hello
world
"""
#print(count_syllables(ex_lyric))