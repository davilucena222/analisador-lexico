class Token:
    def __init__(self, type, text):
        self.type = type
        self.text = text

    def __str__(self):
        return f"Token [type={self.type}, text={self.text}]"