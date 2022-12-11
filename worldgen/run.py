"""The Edge of Reality
"""
from io import BytesIO
from uuid import uuid4
import requests
from time import perf_counter
from typing import List, Dict, Optional

import openai
from PIL import Image

from utils.types import WorldFrame


# TODO: Better config
openai.api_key = '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'
_F_SIZE = 512
_F_NUM = 3
#########


def generate_next_frame_url(src_img: str, **kw_settings) -> str:
    """Given a `src_image`, returns the next `_F_SIZE` pixels to the right
    """
    # Get right half of original:
    original = Image.open(src_img)
    left_half = original.crop((_F_SIZE // 2, 0, _F_SIZE, _F_SIZE))

    # Create a new image that will be the right half and empty
    without_right = Image.new('RGBA', (_F_SIZE, _F_SIZE))
    without_right.paste(left_half, (0, 0))

    # Convert image to bytes
    im_bytes = BytesIO()
    without_right.save(im_bytes, format='PNG')

    # Get extend to the right right: 
    response = openai.Image.create_edit(
        image=im_bytes.getvalue(),
        mask=open('masks/right_small.png', 'rb'),
        **kw_settings
    )
    image_url = response['data'][0]['url']
    return image_url


def generate_last_frame_url(first_img: str, last_img: str, **kw_settings) -> str:
    """Given a `src_image`, returns the next 256 pixel to the right
    """
    # Get right half of original:
    first = Image.open(first_img)
    last = Image.open(last_img)

    # cropped_img = img.crop((left, top, right, bottom))

    left_half = last.crop((_F_SIZE // 4 * 3, 0, _F_SIZE, _F_SIZE))
    right_half = first.crop((0, 0, _F_SIZE // 3 * 2, _F_SIZE))

    # Create a new image that will be the right half and empty
    new = Image.new('RGBA', (_F_SIZE, _F_SIZE))
    new.paste(left_half, (0, 0))
    new.paste(right_half, (_F_SIZE // 4 * 3, 0))
    # new.save('.tmpfiles/debug_before_last.png')
    
    # Convert image to bytes
    im_bytes = BytesIO()
    new.save(im_bytes, format='PNG')

    # Get extend to the right right: 
    response = openai.Image.create_edit(
        image=im_bytes.getvalue(),
        mask=open('masks/middle_small_2.png', 'rb'),
        **kw_settings
    )
    image_url = response['data'][0]['url']
    return image_url


def download_image(url: str, dst: Optional[str] = None) -> WorldFrame:
    """
    """
    dst = dst if dst else f'.tmpfiles/{uuid4()}.png'
    print(f'Downloading from url: {url} to {dst}')
    image_data = requests.get(url)
    image = Image.open(BytesIO(image_data.content))
    image.save(dst)
    return WorldFrame(path=dst, image=image)


def merge_frames(frames: List[WorldFrame]) -> None:
    """Merging all frames together, the last frame is used differently #TODO: Explain better
    """
    print('******************************')
    print('Merging all images together...')
    last_frame = frames.pop()

    # Create a new image that will contain all of the merged images
    init_width = sum([i['image'].size[0] for i in frames])
    total_width = (init_width / 2) + _F_SIZE
    new_image = Image.new('RGB', (int(total_width), _F_SIZE))

    # Paste each image into the new image
    x_offset = 0
    for i, frame in enumerate(frames):
        new_image.paste(frame['image'], (x_offset, 0))
        print(f'Pasted image {i}')
        x_offset += frame['image'].size[0] - (_F_SIZE // 2)

    x_offset = x_offset + (_F_SIZE // 4)
    new_image.paste(last_frame['image'], (x_offset, 0))

    # Save the merged image
    new_image.save(f'examples/full_{uuid4()}.png')


def main_loop(settings: Dict) -> None:
    """
    """
    frames: List[WorldFrame] = []
    last_path = ''
    for i in range(_F_NUM):
        print(f'\nGenereting frame #{i}...')
        if i == 0:
            response = openai.Image.create(**settings)
            url = response['data'][0]['url']
        elif i < _F_NUM - 1:
            url = generate_next_frame_url(last_path, **settings)
        else:
            url = generate_last_frame_url(frames[0]['path'], frames[-1]['path'], **settings)

        frame = download_image(url, dst=f'.tmpfiles/{i}.png')
        last_path = frame['path']
        frames.append(frame)

    merge_frames(frames)


if __name__ == '__main__':
    start_time = perf_counter()
    # prompt = input('What world do you want to play in? ')
    prompt = 'Equirectangular render of an alien world, from a first-person point of view, 8k uhd'
    settings = {'n': 1, 'size': f'{_F_SIZE}x{_F_SIZE}', 'prompt': prompt}
    main_loop(settings)
    run_time = perf_counter() - start_time
    print(f'It took {run_time:.2f} seconds to run.')