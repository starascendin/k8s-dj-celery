from revChatGPT.V1 import Chatbot


class RevChatGPTWrapper:
    def __init__(self, email, password):
        self.chatbot = Chatbot(config={
            "email": email,
            "password": password
        })
        

    def generate_response(self, prompt):
        prev_text = ""
        total = ""
        for data in self.chatbot.ask(
            prompt,
        ):
            message = data["message"][len(prev_text) :]
            print(message, end="", flush=True)
            prev_text = data["message"]
            total += message
        # print("#total", total)
        return total
