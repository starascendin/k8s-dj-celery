import openai
import asyncio
import openai_async
import re
import logging
import os


LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

logger = logging.getLogger(__name__)


class OpenaiSdk:
    output_tokens = 3000
    max_tokens_allowed = 4096
    prompt_tokens = 150
    target_prompt_tokens = max_tokens_allowed - output_tokens - prompt_tokens


    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
        
    async def generate_completion(self, prompt, model_name="text-davinci-003"):
        # Create the asynchronous request
        try:

            response = await openai.Completion.acreate(
                engine=model_name,
                prompt=prompt,
                n=1,
                max_tokens=2000,
                temperature=0.1,
            )

            # Get the generated text

            generated_text = response.choices[0].text
            concat_txt = ""
            for choice in response.choices:
                concat_txt += choice.text

            return generated_text
        except Exception as e:
            print("#error", e)
            return f"OPENAI PROMPT ERROR: {e}"
        
    async def generate_one_chat_completion(self, prompt):
        
        messages = [{"role": "user", "content": prompt}]
        response = await openai_async.chat_complete(
            self.api_key,
            timeout=60,
            payload={"model": "gpt-3.5-turbo", "messages": messages},
        )
        return response.json()

        
    async def generate_chat_completion(self, prompt):
        estimated_tokens = self.estimate_tokens(prompt)
        prompts_to_send = []
        try:
            if estimated_tokens > self.output_tokens:
                logger.info("# Exec generate_chat_completion and SPLITTING large prompt of estimated_tokens", estimated_tokens)

                prompt_only, prompt_task = prompt.split("---")
                arr_prompts = prompt_only.split(" ")
                
                num_chunks = 3
                chunk_size = len(arr_prompts) // num_chunks
                
                chunks = [arr_prompts[i:i+chunk_size] for i in range(0, len(arr_prompts), chunk_size)]
                prompts = [ " ".join(chunk) + f"--- \n\n{prompt_task}" for chunk in chunks ]

                # TODO: these can be parallelized
                logger.info(f"sending openai split prompts ... ")
                for i, prompt in enumerate(prompts):
                    messages = [{"role": "user", "content": prompt}]
                    response = await openai_async.chat_complete(
                        self.api_key,
                        timeout=120,
                        payload={"model": "gpt-3.5-turbo", "messages": messages},
                    )
                    if response.status_code == 200:
                        content = response.json()['choices'][0]['message']['content']
                        content_without_blank_lines = re.sub(r"\n\s*\n", "\n", content)
                        prompts_to_send.append(content_without_blank_lines)
                    elif response.status_code == 400:
                        print("#error 400", response.json())
                        return response.json()
            else: 
                logger.info(f"# Exec generate_chat_completion and normal prompt of estimated_tokens: {estimated_tokens}")
                messages = [{"role": "user", "content": prompt}]
                logger.info(f"sending openai one prompt ... ")
                response = await openai_async.chat_complete(
                    self.api_key,
                    timeout=60,
                    payload={"model": "gpt-3.5-turbo", "messages": messages},
                )
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    content_without_blank_lines = re.sub(r"\n\s*\n", "\n", content)
                    prompts_to_send.append(content_without_blank_lines)
                elif response.status_code == 400:
                    print("#error 400", response.json())
                    return response.json()
            all_contents_resp = "#####\n".join(prompts_to_send)
            return all_contents_resp
        except Exception as e:
            logger.error(f"#OPENAI API CALL ERROR {str(e)}")
            return f"OPENAI API CALL ERROR: {e}"


    async def generate_completions(self, prompts):
        # Create a list of asynchronous tasks
        # tasks = [self.generate_completion(prompt) for prompt in prompts]
  
    
        tasks = [self.generate_chat_completion(prompt) for prompt in prompts]
        
        # Use asyncio.gather to run the tasks in parallel
        results = await asyncio.gather(*tasks)

        # Return the results
        return results

    def run(self, prompts):
        # Create a new event loop
        logger.info(f'Executing openai_sdk.run of prompts len {len(prompts)}....')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the async function and get the results
        results = loop.run_until_complete(self.generate_completions(prompts))
        logger.info(f'DONE executing openai_sdk.run ....')
        # Close the event loop
        loop.close()

        # Return the results
        return results


    @staticmethod
    def estimate_tokens(text, method="min"):
            word_count = len(text.split(" "))
            char_count = len(text)
            tokens_count_word_est = float(word_count) / 0.75
            tokens_count_char_est = float(char_count) / 4.0
            output = 0
            if method == "average":
                output = (tokens_count_word_est + tokens_count_char_est) / 2
            elif method == "words":
                output = tokens_count_word_est
            elif method == 'max':
                output = max([tokens_count_word_est,tokens_count_char_est])
            elif method == 'min':
                output = min([tokens_count_word_est,tokens_count_char_est])
            else:
                output = min([tokens_count_word_est,tokens_count_char_est])
            return  int(output)


import asyncio

if __name__ == "__main__":
    sdk = OpenaiSdk("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")
    
    prompt = "Tell me 3 jokes"
    
    
    resp = asyncio.run(sdk.generate_one_chat_completion(prompt))
    print("#resp", resp)
