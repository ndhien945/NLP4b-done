import numpy as np
import evaluate
from transformers import (
    VisionEncoderDecoderModel, 
    Seq2SeqTrainer, 
    Seq2SeqTrainingArguments,
    default_data_collator
)
from src.preprocess import processor, get_preprocess_function
from src.data_loader import load_and_split_data
from configs.config import CHECKPOINT_DIR, BATCH_SIZE, LEARNING_RATE, EPOCHS, BEST_MODEL_DIR

rouge = evaluate.load("rouge")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    labels = np.where(labels != -100, labels, processor.tokenizer.pad_token_id)
    decoded_preds = processor.batch_decode(predictions, skip_special_tokens=True)
    decoded_labels = processor.batch_decode(labels, skip_special_tokens=True)
    
    result = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    return result

def train_model():
    datasets = load_and_split_data()
    available_columns = datasets['train'].column_names
    content_col = 'markdown' if 'markdown' in available_columns else 'content'
    preprocess_fn = get_preprocess_function(content_col)
    
    train_dataset = datasets['train'].map(preprocess_fn, batched=True, remove_columns=available_columns)
    valid_dataset = datasets['valid'].map(preprocess_fn, batched=True, remove_columns=available_columns)
    test_dataset = datasets['test'].map(preprocess_fn, batched=True, remove_columns=available_columns)

    model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-small")
    start_token = processor.tokenizer.bos_token_id or processor.tokenizer.convert_tokens_to_ids("<s>")
    
    model.config.decoder_start_token_id = start_token
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.decoder.decoder_start_token_id = start_token
    model.config.decoder.pad_token_id = processor.tokenizer.pad_token_id
    model.config.use_cache = False
    if hasattr(model.config, 'decoder'):
        model.config.decoder.use_cache = False

    training_args = Seq2SeqTrainingArguments(
        output_dir=CHECKPOINT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        num_train_epochs=EPOCHS,
        eval_strategy="steps",           
        eval_steps=100,
        save_steps=100,
        logging_steps=20,
        predict_with_generate=True,
        report_to="none"
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        processing_class=processor.tokenizer,
        data_collator=default_data_collator,   
        compute_metrics=compute_metrics,
    )
    trainer.train()

    test_results = trainer.predict(test_dataset)
    print("Test metrics:")
    for key, value in test_results.metrics.items():
        print(f"- {key}: {value}")

    model.config.use_cache = True
    if hasattr(model.config, 'decoder'):
        model.config.decoder.use_cache = True
        
    trainer.save_model(BEST_MODEL_DIR)
    processor.save_pretrained(BEST_MODEL_DIR)
    print(f"Save at {BEST_MODEL_DIR}")

if __name__ == "__main__":
    train_model()