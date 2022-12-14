import os
from uuid import uuid4
import webbrowser
import openai

from world_generator.world_generator import generate_new_world
from config import OPENAI_KEY, FRAME_SIZE


openai.api_key = OPENAI_KEY


if __name__ == '__main__':
    world_path = f'client/assets'
    os.makedirs(world_path, exist_ok=True)
    os.makedirs('.tmpfiles', exist_ok=True)

    # prompt = input('What world do you want to play in? ')
    # prompt = 'Equirectangular render of a psychedelic Middle Ages town hall, from a first-person point of view, 8k uhd'
    prompt = 'Middle Ages town hall'
    fixed_prompt = f'Equirectangular render of {prompt}, from a first-person point of view'

    settings = {'n': 1, 'size': f'{FRAME_SIZE}x{FRAME_SIZE}', 'prompt': fixed_prompt}
    generate_new_world(settings, dst=world_path)

    # url = 'http"localhost'
    # webbrowser.open(url, new=2)  # open in new tab