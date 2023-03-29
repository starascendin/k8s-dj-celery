import pandas as pd
import snoop
# load a content processed csv (post transcription)

@snoop
def load_csv_to_pd(filename):
    ### load csv into pandas
    df = pd.read_csv(filename)

    pass


if __name__ == "__main__":
    filename = "/Users/bryanliu/Downloads/c08ec6f2-b8bc-4a57-a56e-e8ab872da4c0.txt"
    load_csv_to_pd(filename)
