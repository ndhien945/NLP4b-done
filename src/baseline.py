import os
import io
import fitz
import pytesseract
import evaluate
from PIL import Image
from tqdm.auto import tqdm
from configs.config import PDF_DIR

def evaluate_baseline(test_dataset):
    rouge = evaluate.load("rouge")
    baseline_preds = []
    ground_truths = []
    content_col = 'markdown' if 'markdown' in test_dataset.column_names else 'content'
    
    for example in tqdm(test_dataset):
        arxiv_id = example['arxiv_id']
        ground_truth = str(example[content_col])[:1024]
        pdf_path = os.path.join(PDF_DIR, f"{arxiv_id}.pdf")
        
        if not os.path.exists(pdf_path):
            continue
            
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0) 
            pix = page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            doc.close()
            
            pred_text = pytesseract.image_to_string(img)
            baseline_preds.append(pred_text)
            ground_truths.append(ground_truth)
        except Exception as e:
            print(f"Skip {arxiv_id}: {e}")
            
    baseline_results = rouge.compute(predictions=baseline_preds, references=ground_truths, use_stemmer=True)
    print("Baseline Results:")
    for key, value in baseline_results.items():
        print(f"- {key}: {round(value, 4)}")
    return baseline_results