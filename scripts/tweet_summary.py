import os
import pandas as pd
import openai
import time

openai.api_key = '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'

def generateChat(text_prompt):
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an expert at making strong factual summarizations for Twitter. Extract the key facts out of this text. Use as many bullet points as needed. Don't include opinions. Summarize in bullet points and keep the reference url in the same format as the following example: \n\n-[Summary bullet point1] [reference tweet url1] [tweet url]\n-[Summary bullet point2] [tweet url, tweet url]\n\n"},
                  {"role": "user", "content": text_prompt}]
    )
    return rsp

fname = "tweet_list_db.csv"

df = pd.read_csv(fname)
df = df.drop_duplicates(['text'], keep='first', ignore_index=True)
df['combined'] = '* ' + df['text'] + " (Tweet url: https://twitter.com/anyuser/status/" + df['id'].astype(str) + ")"


segments = []
data = []
token_count = 0
for l in df['combined']:
    token_count += len(l) / 4
    data.append(l)
    if token_count > 2800:
        print(f"Segment {len(segments)} {len(data)}")
        segments.append(data)
        data = []
        token_count = 0
segments.append(data)  ## append last piece

summary_all = []
for i, s in enumerate(segments):
    while True:
        try:
            print(f"Working on segment {i}")
            # prompt = '###\n' + ' '.join(s) + '###' + '\n\n Each item above is a tweet. \nTask1: Summarize and describe each unique idea in bullet points. Longer tweets take priority. At the end of each bullet point, add the reference tweet urls related to this idea. \nOutput Format: [Title: UNIQUE IDEAS]\nTask2: Additional points missed from above summarization. . At the end of each bullet point, add the reference tweet urls related to this point. \nOutput Format: [Title: MISSED POINTS]. \n\n'
            prompt = '###\n' + ' '.join(s) + '###' + \
                     '\n\n Each item above is a tweet. \nSummarize and describe in detail each unique idea above in bullet points. Longer tweets have higher priority. ' \
                     'Add the related tweet urls at the end of each bullet point. Make sure each url starts with "https://". \n\n'
            rsp = generateChat(text_prompt=prompt)
            summary = rsp['choices'][0]['message']['content']
            summary = summary.replace("\n\n", "")
            print(summary)
            summary_all.append(summary)
            break
        except Exception as e:
            print(e)
            time.sleep(60)

final_summary = '\n'.join(summary_all)
print(final_summary)
final_summary_points = generateChat(text_prompt='###\n' + final_summary + '\n###\n\nSummarize the bullets above and group by unique topics. keep the reference urls for each bullet.')
blurb_out = final_summary_points['choices'][0]['message']['content']
print(blurb_out)
with open(f"Summary_{fname}.txt", "w") as text_file:
    text_file.write(blurb_out)
    text_file.write("\n\n\n Summary Detail\n\n")
    text_file.write(final_summary)
    text_file.close()
print("############## DONE ##############")


