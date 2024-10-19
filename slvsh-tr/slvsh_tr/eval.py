from difflib import SequenceMatcher
import json
from typing import Callable, TypeVar
from tqdm import tqdm
from pydantic import BaseModel
from .recognizer import Recognizer
from .example import Example
import os
import cv2

example_file_path = os.path.join(
    os.path.dirname(__file__), "assets", "examples.json")


class PrecisionAndRecall(BaseModel):
    precision: float
    recall: float
    f1: float


def tokenize(s: str) -> list[str]:
    return s.replace(',', ' ,').replace('.', ' .').split()


def levenshtein_distance(prediction: str, expected: str) -> PrecisionAndRecall:
    pred_tokens = tokenize(prediction)
    exp_tokens = tokenize(expected)

    op_codes = SequenceMatcher(None, pred_tokens, exp_tokens).get_opcodes()

    tp = 0
    fp = 0
    fn = 0

    for tag, pred1, pred2, exp1, exp2 in op_codes:
        if tag == 'equal':
            tp += pred2 - pred1
        elif tag == 'delete':
            fp += pred2 - pred1
        elif tag == 'insert':
            fn += exp2 - exp1
        elif tag == 'replace':
            fp += pred2 - pred1
            fn += exp2 - exp1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    f1 = 0
    if (precision + recall) > 0:
        f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1


T = TypeVar('T')


def eval(
        model: Recognizer,
        score_function: Callable[[str, str], T] = levenshtein_distance
) -> list[T]:
    with open(example_file_path) as f:
        raw_examples = json.load(f)
    examples: list[Example] = [Example(**example) for example in raw_examples]

    results = []
    for example in tqdm(examples, desc="Evaluating examples"):
        image = cv2.imread(example.image_path)

        if image is None:
            raise RuntimeError(
                f"Error: Could not load image {example.image_path}")
        try:
            prediction = model.infer(image)
        except Exception as e:
            raise RuntimeError(
                f'The model failed to infer {example.image_path}', e)

        result = score_function(prediction, example.expected)

        # Store the result
        results.append(result)
    return results


