from functools import lru_cache

import numpy as np
from easy_vqa import (get_answers, get_test_image_paths, get_test_questions,
                      get_train_image_paths, get_train_questions)
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical


def load_and_proccess_image(image_path):
    # Load image, then scale and shift pixel values to [-0.5, 0.5]
    im = img_to_array(load_img(image_path))
    return im / 255 - 0.5


def read_images(paths):
    # paths is a dict mapping image ID to image path
    # Returns a dict mapping image ID to the processed image
    ims = {}
    for image_id, image_path in paths.items():
        ims[image_id] = load_and_proccess_image(image_path)
    return ims

@lru_cache()
def get_data():
    # Read questions from the easy-vqa package
    train_qs, train_answers, train_image_ids = get_train_questions()
    test_qs, test_answers, test_image_ids = get_test_questions()
    print(f'Read {len(train_qs)} training questions and {len(test_qs)} testing questions.')

    # Read answers from the easy-vqa package
    all_answers = get_answers()
    num_answers = len(all_answers)
    print(f'Found {num_answers} total answers:')


    # Read images from the easy-vqa package
    train_ims = read_images(get_train_image_paths())
    test_ims = read_images(get_test_image_paths())
    im_shape = train_ims[0].shape
    print(f'Read {len(train_ims)} training images and {len(test_ims)} testing images.')
    print(f'Each image has shape {im_shape}.')

    print('\n--- Fitting question tokenizer...')
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(train_qs)

    # We add one because the Keras Tokenizer reserves index 0 and never uses it.
    vocab_size = len(tokenizer.word_index) + 1
    print(f'Vocab Size: {vocab_size}')
    print(tokenizer.word_index)

    print('\n--- Converting questions to bags of words...')
    train_X_seqs = tokenizer.texts_to_matrix(train_qs)
    test_X_seqs = tokenizer.texts_to_matrix(test_qs)
    print(f'Example question bag of words: {train_X_seqs[0]}')

    print('\n--- Creating model input images...')
    train_X_ims = np.array([train_ims[id] for id in train_image_ids])
    test_X_ims = np.array([test_ims[id] for id in test_image_ids])

    print('\n--- Creating model outputs...')
    train_answer_indices = [all_answers.index(a) for a in train_answers]
    test_answer_indices = [all_answers.index(a) for a in test_answers]
    train_Y = to_categorical(train_answer_indices)
    test_Y = to_categorical(test_answer_indices)
    print(f'Example model output: {train_Y[0]}')

    return (train_X_ims, train_X_seqs, train_Y, test_X_ims, test_X_seqs,
            test_Y, im_shape, vocab_size, num_answers,
            all_answers, test_qs, test_answer_indices)  # for the analyze script
