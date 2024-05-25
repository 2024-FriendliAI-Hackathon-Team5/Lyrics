import os
import dotenv
import openai
import random
import make_dataset
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.friendli import ChatFriendli

dotenv.load_dotenv()

llm = ChatFriendli(
    friendli_token = os.getenv("FRIENDLI_API_KEY"),
    model = "meta-llama-3-70b-instruct",
    streaming = False,
    # temperature=0.5,
    # max_tokens=100,
    # top_p=0.9,
    # frequency_penalty=0.0,
    # stop=["\n"],
)

frame_prompt = """Suggest a single line of Korean lyric that matches with given syllables,lyrics, and title.
Ensure to avoid repeating previous lyrics. Focus on creative and original expression.
Match the length of the sentence to the syllables I provide as closely as possible.
For example, if Syllables: 7 given, you should write a 6~8 letter korean sentence.
Your answer should feel like soft, trendy K-pop lyrics without any profanity.
Your answer should be short, and only composed with a single sentence.
Answer with a single line of lyrics you created, and nothing else.

Here,
Title: {title}
Mood and Symbol: {mood}
Previous Lyrics: {lyric}
Syllables: {syllables}

Your korean lyric that should be added to the previous lyrics:
"""

client = openai.OpenAI(base_url="https://inference.friendli.ai/dedicated/v1", api_key=os.getenv("FRIENDLI_API_KEY"))

def update_language(current_language):
    if random.random() < 0.8:
        return current_language
    else:
        return random.choice(make_dataset.languages)

def extract_message(text, ending):
    pattern = re.escape(ending) + r'([^"\n]+)'
    match = re.search(pattern, text)
    if match:
        message = match.group(1).strip()
        return message.strip('"')
    return "" 

def find_mood(lyric):
    prompt = PromptTemplate.from_template("find mood and symbolic keyword of the given song. one sentence each. song: {lyric}. Mood and symbol: ")
    formatted_prompt = prompt.format(lyric=lyric)

    feedback_chain = (
        llm
        | StrOutputParser()
    )

    return feedback_chain.invoke(formatted_prompt)

def generate_korean_lyrics(title, lyric):
    """
    prompt = make_dataset.frame_prompt.format(title=title, lyric=lyric, syllables=make_dataset.count_syllables(lyric))
    response = client.chat.completions.create(
                    model=os.getenv("KR_ENDPOINT"),
                    messages=[
                        {"role": "system", "content": f"You are an assistant of lyricist"},
                      
                        {"role": "user", "content": prompt},
                    ],
                )
    return response.choices[0].message.content
    """
    lines = lyric.split('\n')
    result = ""
    mood = find_mood(lyric)
    print(mood)
    for line in lines:
        if len(line) > 0:
            candidate = ""
            candidate_count = 7
            syllables = make_dataset.count_syllables(line)
            for i in range(1):
                #print("Original:", line)
                response = client.chat.completions.create(
                    model=os.getenv("KR_ENDPOINT"),
                    messages=[
                        {"role": "system", "content": f"You are an assistant of lyricist"},
                        {"role": "user", "content": frame_prompt.format(title=title, lyric=result, syllables=syllables, mood=mood)},
                    ],
                )
                suggestion = response.choices[0].message.content
                count = make_dataset.count_syllables(suggestion)
                if count == syllables:
                    #print(f"[Success!] Suggestion {i}:", suggestion)
                    candidate = suggestion
                    break
                elif count < syllables:
                    if syllables - count < candidate_count:
                        candidate = suggestion
                        candidate_count = syllables - count
                else:
                    if count - syllables < candidate_count:
                        candidate = suggestion
                        candidate_count = count - syllables
                #print(f"[Fail!] Suggestion {i}:", suggestion)
            result += candidate + '\n'
    return result
