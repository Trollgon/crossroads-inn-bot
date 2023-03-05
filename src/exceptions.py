class APIException(Exception):

    def __init__(self, url: str, response_code: int, response_json: dict):
        if type(response_json) == dict and "text" in response_json:
            response_text = response_json["text"]
        else:
            response_text = "unknown api error"
        self.error_message = f"{url} {response_code}: {response_text}"
        super().__init__(self.error_message)
