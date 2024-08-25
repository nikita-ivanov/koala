import numpy as np
import onnxruntime
from tokenizers import Tokenizer

from .configuration import load_config

BASE_DIR = "utils/assets"
config = load_config()

model_path = f"{BASE_DIR}/translator_transformer_v4_2_layers.onnx"

ort_session = onnxruntime.InferenceSession(config.translator_model_path,
                                           providers=["CPUExecutionProvider"])

ort_inputs_info = ort_session.get_inputs()
src_seq_length = ort_inputs_info[0].shape[1]
tgt_seq_length = ort_inputs_info[1].shape[1]

# we need our tokenizers which original model used for training
src_lang = Tokenizer.from_file(config.de_tokenizer_path)
tgt_lang = Tokenizer.from_file(config.en_tokenizer_path)


def translate(src_sentence: str,
              max_tgt_length: int = 100) -> str:
    """
    Translate a sentence using ONNX model.
    We pass one token at a time, i.e. generating autoregressively
    using model's own outputs as inputs.
    """
    input_ids = src_lang.encode(src_sentence).ids[:src_seq_length]
    input_ids = np.pad(input_ids, (0, src_seq_length - len(input_ids)),
                       constant_values=src_lang.token_to_id("<PAD>"))

    input_ids = np.reshape(input_ids, (1, -1))

    tgt_indices = [tgt_lang.token_to_id("<BOS>")]  # type: list[int]

    for t in range(max_tgt_length):
        tgt_ids = np.array(tgt_indices)
        tgt_ids = np.pad(tgt_ids, (0, tgt_seq_length - len(tgt_ids)),
                         constant_values=tgt_lang.token_to_id("<PAD>"))
        tgt_ids = np.reshape(tgt_ids, (1, -1))

        # shape (1, 128, 8000) -> (batch_size, seq_length, tgt_vocab_size)
        model_outputs = ort_session.run(None, {"l_src_": input_ids,
                                        "l_tgt_": tgt_ids})[0]

        # we take the best prediction for step t only (generating autoregressivly)
        prediction = model_outputs[0, t].argmax()  # type: int
        tgt_indices.append(prediction)

        if prediction == tgt_lang.token_to_id("<EOS>"):
            break

    sentence = tgt_lang.decode(tgt_indices, skip_special_tokens=True)

    return sentence
