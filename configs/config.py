import os
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PDF_DIR = "/kaggle/input/datasets/danghiennguyen/arxiv-pdf-small/arxiv_dataset_pdfs/"
DATASET_NAME = "marcodsn/arxiv-markdown"
TEST_PDF_PATH = "/kaggle/input/datasets/danghiennguyen/test-pdf/Prokct.pdf"
CHECKPOINT_DIR = "./ocr_finetuned_checkpoints"
BEST_MODEL_DIR = "./models/best_ocr_model" 

TEST_SIZE = 0.15
VALID_SIZE = 0.15
SEED = 42

BATCH_SIZE = 2
LEARNING_RATE = 3e-5
EPOCHS = 2
MAX_LENGTH = 512
MAX_NEW_TOKENS = 1024