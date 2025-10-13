import os
import yaml
from charset_normalizer import from_path
from pathlib import Path
import pytz
from datetime import datetime
import re


def load_prompt(filename, full_path):
    """Load a prompt from a YAML file."""
    if not full_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(script_dir, "prompts", filename)
    else:
        prompt_path = filename

    # try:
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_data = yaml.safe_load(file)
        return prompt_data.get("instructions", "")
    # except (FileNotFoundError, yaml.YAMLError) as e:
    #     print(f"Error loading prompt file {filename}: {e}")
    #     return ""

# def load_prompt(filename):
#     """Load a prompt from a YAML file."""
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     prompt_path = os.path.join(script_dir, "prompts", filename)

#     try:
#         with open(prompt_path, "r", encoding="utf-8") as file:
#             prompt_data = yaml.safe_load(file)
#             return prompt_data.get("instructions", "")
#     except (FileNotFoundError, yaml.YAMLError) as e:
#         print(f"Error loading prompt file {filename}: {e}")
#         return ""

def read_text_auto_encoding(file_path: str) -> str:
    """
    Reads a text file with auto-detected encoding using charset-normalizer.

    :param file_path: Path to the text file
    :return: Content of the file as a string
    :raises FileNotFoundError: If the file does not exist
    :raises ValueError: If file content could not be decoded
    """

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    result = from_path(file_path)
    best_guess = result.best()
    if best_guess is None:
        raise ValueError(f"Could not decode file: {file_path}")
    print(f"type(best_guess): {type(best_guess)}")
    print(f"dir(best_guess): {dir(best_guess)}")

    return best_guess.text  # ✅ This is the correct method

def current_time(timezone: str = "GMT") -> str:
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.timezone("GMT")

    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def get_month_year_as_string():
    now_ = datetime.now()
    current_month = now_.strftime("%B")
    current_year = now_.year
    return f"{current_year}/{current_month}"

