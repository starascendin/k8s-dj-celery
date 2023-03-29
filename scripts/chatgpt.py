from pychatgpt import Chat, Options
from revChatGPT.V1 import Chatbot

# This works
def revchatgpt_main(email, password, question):
    # Create a Chatbot object
    chatbot = Chatbot(config={
    "email": email,
    "password": password
    })

    print("Chatbot: ")
    prev_text = ""
    total = ""
    for data in chatbot.ask(
        question,
    ):
        message = data["message"][len(prev_text) :]
        print(message, end="", flush=True)
        prev_text = data["message"]
        total += message
    print("#total", total)

def pychatgpt_main(email, password, question):
    options = Options()

    # [New] Pass Moderation. https://github.com/rawandahmad698/PyChatGPT/discussions/103
    # options.pass_moderation = False

    # [New] Enable, Disable logs
    options.log = True

    # Track conversation
    options.track = True

    # Use a proxy
    options.proxies = 'http://localhost:8080'

    # Optionally, you can pass a file path to save the conversation
    # They're created if they don't exist

    # options.chat_log = "chat_log.txt"
    # options.id_log = "id_log.txt"

    # Create a Chat object
    chat = Chat(email=email, password=password, options=options)
    answer = chat.ask("How are you?")
    print(answer)


if __name__ == '__main__':
    # pychatgpt_main("bsliu17@gmail.com", "Daski#3178583", "Who is the first president of the United States?")
    # revchatgpt_main("star.ascendin@gmail.com", "w00fyNinjas@023", "tell me a joke about coffee and bagel")
    pass
