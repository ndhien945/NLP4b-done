import os
import io
import fitz
from PIL import Image
from transformers import NougatProcessor
from configs.config import PDF_DIR, MAX_LENGTH

processor = NougatProcessor.from_pretrained("facebook/nougat-small", use_fast=False)

def get_preprocess_function(content_col):
    def preprocess_function(examples):
        pixel_values, labels = [], []
        batch_arxiv_ids = examples['arxiv_id']
        batch_markdowns = examples[content_col]
        
        for arxiv_id, markdown_text in zip(batch_arxiv_ids, batch_markdowns):
            pdf_path = os.path.join(PDF_DIR, f"{arxiv_id}.pdf")
            if not os.path.exists(pdf_path):
                continue
                
            try:
                doc = fitz.open(pdf_path)
                page = doc.load_page(0) 
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                doc.close()
                
                processed_img = processor(img, return_tensors="pt").pixel_values.squeeze()
                pixel_values.append(processed_img)
                
                tokenized_text = processor.tokenizer(
                    str(markdown_text)[:1024], padding="max_length", 
                    max_length=MAX_LENGTH, truncation=True, return_tensors="pt"
                ).input_ids.squeeze()
                tokenized_text[tokenized_text == processor.tokenizer.pad_token_id] = -100
                labels.append(tokenized_text)
                
            except Exception as e:
                print(f"Skip {arxiv_id}: {e}")
                continue
                
        return {"pixel_values": pixel_values, "labels": labels}
    return preprocess_function