from langchain.document_loaders import YoutubeLoader
from langchain.llms import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Any, List

from langchain.docstore.document import Document

# from langchain.document_loaders import YoutubeLoader
import snoop
# loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=QsYGlZkevEg", add_video_info=True)

# @snoop
def main():
    loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=4AXTmL4TC6c", add_video_info=True)
    result: List[Document] = loader.load()
    # BL: i can create Document objects from my transcript w/ timestamp.
    
    
    # print (type(result))
    # print (f"Found video from {result[0].metadata['author']} that is {result[0].metadata['length']} seconds long")
    # print ("")
    print (result)
    llm = OpenAI(temperature=0, openai_api_key="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")
    
    chain = load_summarize_chain(llm, chain_type="stuff", verbose=False)
    resp = chain.run(result)
    print("#resp", resp)
    
    # BL: YoutubeLoader does not have timestamps
    
    # split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    print("#text_splitter", text_splitter)
    texts = text_splitter.split_documents(result)
    # print("#len(texts)", len(texts))
    print("#texts", texts)

    chain = load_summarize_chain(llm, chain_type="map_reduce", verbose=True)
    print("#chain", chain)
    resp = chain.run(texts[:4])
    print("#resp", resp)

if __name__ == "__main__":
    main()