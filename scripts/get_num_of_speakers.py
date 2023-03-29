# import nltk
# import snoop
# nltk.download("punkt")
# nltk.download("averaged_perceptron_tagger")

# ## doesn't work

# @snoop
# def detect_speakers(description):
#     words = nltk.word_tokenize(description)
#     pos_tags = nltk.pos_tag(words)
#     speaker_count = 0
#     for word, pos in pos_tags:
#         if pos == "NNP":
#             speaker_count += 1
#     return speaker_count

# # description = "Trey Lockerbie sits down with Morgan Housel, the author of the international best-selling book, The Psychology of Money, who is a partner at Venture Capital and PE firm Collaborative Fund. He’s a former columnist at The Motley Fool and Wall Street Journal."
# # speaker_count = detect_speakers(description)
# # print("Number of speakers:", speaker_count)


# if __name__ == "__main__":
#     description = "Trey Lockerbie sits down with Morgan Housel, the author of the international best-selling book, The Psychology of Money, who is a partner at Venture Capital and PE firm Collaborative Fund. He’s a former columnist at The Motley Fool and Wall Street Journal."
#     speaker_count = detect_speakers(description)
#     print("Number of speakers:", speaker_count)



import spacy
import snoop
@snoop
def detect_speakers(description):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(description)
    speaker_count = 0
    for entity in doc.ents:
        print( entity.text, entity.label_)
        if entity.label_ == "PERSON":
            speaker_count += 1
    return speaker_count


if __name__ == "__main__":
    description = "Trey Lockerbie sits down with Morgan Smith, the author of the international best-selling book, The Psychology of Money, who is a partner at Venture Capital and PE firm Collaborative Fund. He’s a former columnist at The Motley Fool and Wall Street Journal."
    speaker_count = detect_speakers(description)
    print("Number of speakers:", speaker_count)
