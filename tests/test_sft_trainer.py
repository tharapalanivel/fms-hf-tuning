# Copyright The IBM Tuning Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit Tests for SFT Trainer.
"""    

# Standard
import os
import tempfile

# Local
from tuning import sft_trainer
from tests.helpers import causal_lm_train_kwargs
from tests.fixtures import CAUSAL_LM_MODEL
from tests.data import TWITTER_COMPLAINTS_DATA


HAPPY_PATH_KWARGS = {"model_name_or_path": CAUSAL_LM_MODEL,
    "data_path": TWITTER_COMPLAINTS_DATA,
    "num_train_epochs": 5,
    "per_device_train_batch_size": 4,
    "per_device_eval_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "learning_rate": 0.00001, 
    "weight_decay": 0,
    "warmup_ratio": 0.03,
    "lr_scheduler_type": "cosine",
    "logging_steps": 1,
    "include_tokens_per_second": True,
    "packing": False,
    "response_template": "\\n###Response:",
    "dataset_text_field": "output",
    "use_flash_attn": False,
    "torch_dtype": "float16",
    "modelMaxLength": 4096,
    "peft_method": "pt",
    "target_modules": [],
    "prompt_tuning_init": "RANDOM",
    "num_virtual_tokens": 8,
    "prompt_tuning_init_text": "hello",
    "tokenizer_name_or_path": CAUSAL_LM_MODEL,
    "save_strategy":"epoch"} 

def test_run_causallm_pt():
    """Check if we can bootstrap and run causallm models"""
    with tempfile.TemporaryDirectory() as tempdir:
        HAPPY_PATH_KWARGS["output_dir"] = tempdir
        model_args, data_args, training_args, tune_config = causal_lm_train_kwargs(HAPPY_PATH_KWARGS)
        sft_trainer.train(model_args, data_args, training_args, tune_config)
        _validate_training(tempdir)
        

def test_run_causallm_lora():
    """Check if we can bootstrap and run causallm models"""
    with tempfile.TemporaryDirectory() as tempdir:
        HAPPY_PATH_KWARGS["output_dir"] = tempdir
        HAPPY_PATH_KWARGS["peft_method"] = "lora"
        model_args, data_args, training_args, tune_config = causal_lm_train_kwargs(HAPPY_PATH_KWARGS)
        sft_trainer.train(model_args, data_args, training_args, tune_config)
        _validate_training(tempdir)


def _validate_training(tempdir):
    assert any(x.startswith('checkpoint-') for x in os.listdir(tempdir))
    loss_file_path = "{}/train_loss.jsonl".format(tempdir)
    assert os.path.exists(loss_file_path) == True
    assert os.path.getsize(loss_file_path) > 0