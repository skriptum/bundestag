import numpy as np
from PIL import Image
import wordcloud as wc

def word_clouder(dataframe):
    mask = np.array(PIL.Image.open("stencil.jpg"))

    hashtags = get_hashtags(dataframe)[:100]
    hashtags = hashtags.to_dict()

    cloud = wc.WordCloud(background_color="white", mask = mask)
    cloud = cloud.generate_from_frequencies(hashtags)

    cloud.to_image()