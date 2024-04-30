"""Image processing tool."""
import io
import logging
import requests
from typing import List

from promptflow import tool
from PIL import Image as Image
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
NO_OF_IMAGES_TO_PROCESS = 1

@tool
def process_image(image_urls: List[str]) -> List[str]:
    """
    Resize input product images as per the required size.

    Args:
        image_urls (list[str]): List of urls for original product images

    Returns:
        list[PFImage]: List of resized product images
    """
    required_size = (1024, 1024)

    resized_images = []
    image_counter = 0
    for image_url in image_urls:
        try:
            # Download product image from input URL
            response = requests.get(image_url)
            response.raise_for_status()

            # Open image and resize it to required size
            data_bytes = io.BytesIO(response.content)
            image = Image.open(data_bytes)
            logger.info(
                f"Original image size: Width {image.width}, Height: {image.height}")

            if image.width > required_size[0] or image.height > required_size[1]:
                logger.info(f"Resizing image to {required_size}")
                image.thumbnail(required_size)

            bytes_arr = io.BytesIO()
            image.save(bytes_arr, format='JPEG')
            logger.info(
                f"Image size after resizing: Width {image.width}, Height: {image.height}")

            base64_image = base64.b64encode(
                bytes_arr.getvalue()).decode('utf-8')
            resized_images.append(base64_image)
            image_counter += 1
            if image_counter == NO_OF_IMAGES_TO_PROCESS:
                break
        except requests.RequestException as e:
            logger.error(f"Error fetching image from {image_url}: {e}")
            raise
        except (IOError, OSError) as e:
            logger.error(f"Error opening/saving image from {image_url}: {e}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error occurred during image processing: {e}")
            raise

    return resized_images