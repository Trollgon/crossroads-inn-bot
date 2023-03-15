class APIException(Exception):

    def __init__(self, url: str, response_code: int, response_json: dict | None):
        response_text = ""
        if type(response_json) == dict:
            if "text" in response_json:
                response_text = response_json["text"]
            elif "error" in response_json:
                response_text = response_json["error"]
        if not response_text:
            response_text = "unknown api error"
        self.error_message = f"{url} {response_code}: {response_text}"
        super().__init__(self.error_message)
