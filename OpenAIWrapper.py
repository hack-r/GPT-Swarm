import openai

class OpenAIWrapper:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.clients = [openai.ApiClient(api_key) for api_key in api_keys]

    def set_api_keys(self, api_keys):
        self.api_keys = api_keys
        self.clients = [openai.ApiClient(api_key) for api_key in api_keys]

    def create_completion(self, prompt, chat_mode=False, chat_options=None, model="gpt-3.5-turbo", **kwargs):
        client = self._get_next_client()
        if chat_mode:
            if chat_options is None:
                chat_options = {}
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            messages.extend(chat_options.get("messages", []))
            payload = {
                "model": model,
                "messages": messages,
                "temperature": chat_options.get("temperature", 0.7),
                "max_tokens": chat_options.get("max_tokens", 100),
                "top_p": chat_options.get("top_p", 1.0),
                "n": chat_options.get("n", 1),
                "stop": chat_options.get("stop"),
                "presence_penalty": chat_options.get("presence_penalty", 0.0),
                "frequency_penalty": chat_options.get("frequency_penalty", 0.0)
            }
            payload.update(kwargs)
            return client.create_chat_completion(**payload)
        else:
            return client.create_completion(engine=model, prompt=prompt, **kwargs)

    def create_classification(self, model, examples):
        client = self._get_next_client()
        return client.create_classification(model=model, examples=examples)

    def create_answer(self, question, documents, **kwargs):
        client = self._get_next_client()
        return client.create_answer(question=question, documents=documents, **kwargs)

    def _get_next_client(self):
        if not self.clients:
            raise ValueError("No API keys available.")
        client = self.clients.pop(0)
        self.clients.append(client)
        return client
