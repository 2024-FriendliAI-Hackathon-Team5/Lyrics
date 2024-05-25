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

frame_prompt = """Using the context provided by the title and the preceding lyrics, create a sentence that can come after it. It should complement the mood, theme, and flow of the song. Be sure to match the given syllables and language. The sentence should seamlessly fit into the lyrics, enhancing the overall narrative and emotional impact.

Ensure you count the syllables to match exactly and avoid repeating specific words from the provided lyrics. Focus on creative and original expression.

Create a giben language sentence.
Count the syllables to ensure it matches exactly.
If it doesn't match, revise and count again.
Ensure the sentence does not repeat specific words from the provided lyrics.
Check that the sentence fits the mood, theme, and flow of the song.

1. Here's an English example:

"It's me James"
Let's count the syllables:

It's (1)
me (1)
James (1)
Total: 1 + 1 + 1 = 3

Wrong... I will find a new sentence that matches the syllables.

"Heartbeats racing through the night"

Let's count the syllables:

Heartbeats (2)
racing (2)
through (1)
the (1)
night (1)
Total: 2 + 2 + 1 + 1 + 1 = 7

Correct! This is my suggestion.
"Heartbeats racing through the night"

2. Here's a Korean example:

"심장이 마구 뛰어"

Let's count the syllables:

심장이 (3)
마구 (2)
뛰어 (2)
Total: 3 + 2 + 2 = 7

Correct! This is my suggestion.
"심장이 마구 뛰어"

3. Here's a Korean with English example:

"날아가 fly high"
Let's count the syllables:

날아가 (3)
fly (1)
high (1)
Total: 3 + 1 + 1 = 5

Wrong... I will find a new sentence that matches the syllables.

"내 심장 자꾸 popping"
Let's count the syllables:

내 (1)
심장 (2)
자꾸 (2)
popping (2)
Total: 1 + 2 + 2 + 2 = 7

Correct! This is my suggestion.
"내 심장 자꾸 popping"

Here

Do it for this
Title: {title} 
Lyrics: {lyric}
Syllables: {syllables}
Language: {language}
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

def update_language(current_language):
    if random.random() < 0.5:
        return current_language
    else:
        return random.choice(languages)

def generate_kr_lyrics_data(infile, trainfile, testfile):
    df = pd.read_csv(infile, usecols=['title', 'lyric'])

    # shuffle data
    df = df.sample(frac=1).reset_index(drop=True)
    
    # train:test = 8:2
    train_size = int(len(df) * 0.8)
    train_df = df[:train_size]
    test_df = df[train_size:]

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
                    prompt = frame_prompt.format(title=title, lyric=completed_lyric, syllables=syllable, language=language)
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
ex_lyric = """정말 짜릿했어 어디선가
내게 윙크한 까만 눈동자
Boy, your beautiful eyes got me lost now, yeah, yeah
깜짝 놀라게 하기는 해도
자신만만한 너의 그 태도
Liked you from the get go, cool함은 그대로, 부담감은 '제로'
'Cause you know you're sparkling like a shooting star
I can see us going far, 얼마나 상큼할까
We will pop up all around the world (world) 마법 같은 걸 (걸)
I'm ready, let's go (go), you already know (know, know, know)
That I don't ever want us to be
I don't ever want us to be, I don't ever want us to be apart (ye-yeah)
I don't ever want us to be, I don't ever want us to be apart
코-코-코-코-코-코 (코)
코카콜라 맛있다, 코카콜라 맛있다
See you looking, catch it, here's your Cola
See you looking, catch it, here's your Cola
코카콜라 맛있다, 코카콜라 맛있다
See you looking, catch it, here's your Cola
See you looking, catch it, here's your Cola
사실 궁금했어 저기선가
내 눈에 띄던 까만 네 글자
Boy, your stylish glow up got me hooked now, yeah, yeah
살짝 짓궂게 보이긴 해도
완전 달달한 너의 그 애교
Liked you from the get go, sweet함은 그대로, 불안감은 '제로'
'Cause you know you're sparkling like a shooting star
I can see us going far, 얼마나 상큼할까
We will pop up all around the world (world) 마법 같은 걸 (걸)
I'm ready, let's go (go), you already know (know, know, know)
That I don't ever want us to be
I don't ever want us to be, I don't ever want us to be apart (ye-yeah)
I don't ever want us to be, I don't ever want us to be apart
코-코-코-코-코-코 (코)
코카콜라 맛있다, 코카콜라 맛있다
See you looking, catch it, here's your Cola
See you looking, catch it, here's your Cola
코카콜라 맛있다, 코카콜라 맛있다
See you looking, catch it, here's your Cola
See you looking, catch it, here's your Cola
"""
#print(count_syllables(ex_lyric))