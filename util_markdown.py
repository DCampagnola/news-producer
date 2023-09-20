
chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

def escape(text):
    for char in chars_to_escape:
        text = text.replace(char, '\\' + char)
    return text
