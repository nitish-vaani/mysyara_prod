import re

def remove_emojis(text):
    emoji_pattern = re.compile(
        r'[\U00010000-\U0010FFFF]',  # Match all supplementary Unicode characters (includes all emojis)
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def remove_asterics(text):
    text = text.replace("*", "")
    return text

def preprocess_text(text):
    text = remove_emojis(text)
    text = remove_asterics(text)
    return text

if __name__ == "__main__":
    # Example usage
    text_with_emojis = "Hello world! 😊 This is a test 😜.  Another test 🤣."
    text_without_emojis = remove_emojis(text_with_emojis)
    print(f"Original string: {text_with_emojis}")
    print(f"String without emojis: {text_without_emojis}")
