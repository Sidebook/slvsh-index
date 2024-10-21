from difflib import SequenceMatcher
from typing import Callable, TypeVar
from tqdm import tqdm
from pydantic import BaseModel
from .recognizer import Recognizer
from .example import load_examples, Example
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed


class PrecisionRecallF1(BaseModel):
    precision: float
    recall: float
    f1: float


def tokenize(s: str) -> list[str]:
    return s.replace(',', ' , ').replace('.', ' . ').split()


def levenshtein_distance(prediction: str, expected: str) -> PrecisionRecallF1:
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

    if len(exp_tokens) == 0:
        recall = 1.0
        precision = 1.0 if len(pred_tokens) == 0 else 0

    f1 = 0
    if (precision + recall) > 0:
        f1 = 2 * (precision * recall) / (precision + recall)

    return PrecisionRecallF1(
        precision=precision,
        recall=recall,
        f1=f1
    )


class EvaluationResult(BaseModel):
    score: PrecisionRecallF1
    example: Example
    prediction: str

    def dump(self) -> dict:
        return {
            **self.example.model_dump(),
            **self.score.model_dump(),
            "prediction": self.prediction
        }


def eval(
        model: Recognizer,
        score_function: Callable[[str, str], PrecisionRecallF1] = levenshtein_distance,
        n_examples: int = -1,
        n_threads: int = None
) -> list[EvaluationResult]:
    examples = load_examples()
    if n_examples != -1:
        examples = examples[:n_examples]

    results = []

    def process_example(example):
        image = example.get_image()

        if image is None:
            raise RuntimeError(
                f"エラー: 画像 {example.image_path} を読み込めませんでした")
        try:
            prediction = model.infer(image)
        except Exception as e:
            raise RuntimeError(
                f'モデルが {example.image_path} の推論に失敗しました', e)

        score = score_function(prediction, example.expected)
        return EvaluationResult(score=score, example=example, prediction=prediction)

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(process_example, example) for example in examples]
        
        for future in tqdm(as_completed(futures), total=len(examples), desc="例の評価中"):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"エラーが発生しました: {str(e)}")

    return results

