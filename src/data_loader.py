import os
from datasets import load_dataset, DatasetDict
from configs.config import DATASET_NAME, PDF_DIR, TEST_SIZE, VALID_SIZE, SEED

def check_local_pdf(example):
    pdf_path = os.path.join(PDF_DIR, f"{example['arxiv_id']}.pdf")
    return os.path.exists(pdf_path)

def load_and_split_data():
    dataset = load_dataset(DATASET_NAME, split="train")
    dataset = dataset.filter(check_local_pdf)
    
    total_found = len(dataset)
    if total_found == 0:
        raise FileNotFoundError("404 Not Found.")
        
    train_test_split = dataset.train_test_split(test_size=TEST_SIZE, seed=SEED)
    test_dataset = train_test_split['test']
    train_valid_split = train_test_split['train'].train_test_split(test_size=VALID_SIZE, seed=SEED)
    
    final_datasets = DatasetDict({
        'train': train_valid_split['train'],
        'valid': train_valid_split['test'],
        'test': test_dataset
    })
    
    print(f"Train: {len(final_datasets['train'])} mẫu")
    print(f"Valid: {len(final_datasets['valid'])} mẫu")
    print(f"Test: {len(final_datasets['test'])} mẫu")
    
    return final_datasets

if __name__ == "__main__":
    load_and_split_data()