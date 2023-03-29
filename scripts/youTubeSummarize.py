import openai
import pandas as pd

openai.api_key = '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'

def generate(text_prompt, max_len=600, n=1, temp=0.7):
  rsp = openai.Completion.create(
    # model="text-davinci-003",
    model="gpt-3.5-turbo",
    # model="davinci:ft-personal-2023-01-11-09-50-57",
    prompt=text_prompt,
    temperature=temp,
    max_tokens=max_len,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    n=n
  )
  return rsp

def generateChat(text_prompt):
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text_prompt}]
    )
    return rsp

# import webvtt
#
# data = webvtt.read('transcript.vtt')
#
# for caption in webvtt.read('transcript.vtt'):
#     print(caption.start)
#     print(caption.end)
#     print(caption.text)

def summarize_transcript(fname):
    df = pd.read_csv(f"./data/{fname}.csv")

    token_count = 0
    segments = []
    data = ""
    for r in df.values.tolist():
        r = ', '.join(r)
        token_count += len(r) / 4
        data = data + r
        if token_count > 2800:
            print(f"Segment {len(segments)} {len(data)/4}")
            segments.append(data)
            data = ""
            token_count = 0
    segments.append(data)
    print(sum([len(a) for a in segments]))

    summary_all = []
    for i, s in enumerate(segments):
        print(f"Working on segment {i}")
        prompt = '###\n' + s + '###' + '\n\n Summarize into a list of succinct bullet points. Do not be constrained to keep this list short. List as many bullet points as necessary to cover all key topics. For each bullet add the timestamp of source information at the end in the format of [TIME]\n\n'
        rsp = generateChat(text_prompt=prompt)
        rsp = rsp['choices'][0]['message']['content']
        rsp = rsp.replace("\n\n","")
        print(rsp)
        summary_all.append(rsp)

    final_summary = '\n'.join(summary_all)
    final_summary = final_summary.replace("\n\n", "")
    # print(final_summary)
    final_summary_points = generateChat(text_prompt= '###\n'+final_summary+'\n###\n\nSummarize into bullet points and group bullets by unique topic. For each bullet add the timestamp of source information at the end in the format of [TIME]\n\n')

    blurb_out = final_summary_points['choices'][0]['message']['content']
    print(blurb_out)
    with open(f"./data/Summary_{fname}.txt", "w") as text_file:
        text_file.write(blurb_out)
        text_file.write("\n\n\n Summary Detail\n\n")
        text_file.write(final_summary)
        text_file.close()
    print("############## DONE ##############")


summarize_transcript(r'no_chpt_4ppl')
