import io
import re
import fitz
from PIL import Image
from transformers import VisionEncoderDecoderModel, NougatProcessor
from configs.config import DEVICE, BEST_MODEL_DIR, MAX_NEW_TOKENS

def my_finetuned_ocr_tool_full(pdf_path):
    my_model = VisionEncoderDecoderModel.from_pretrained(BEST_MODEL_DIR).to(DEVICE)
    my_processor = NougatProcessor.from_pretrained(BEST_MODEL_DIR, use_fast=False)
    
    full_markdown_result = []
    
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        for page_num in range(total_pages):
            print(f"Page {page_num + 1}/{total_pages}...")
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            
            pixel_values = my_processor(img, return_tensors="pt").pixel_values.to(DEVICE)
            
            outputs = my_model.generate(
                pixel_values,
                max_new_tokens=MAX_NEW_TOKENS, 
                bad_words_ids=[[my_processor.tokenizer.unk_token_id]],
            )
            
            sequence = my_processor.batch_decode(outputs, skip_special_tokens=True)[0]
            clean_sequence = sequence.replace("[wgn]", "").replace("[MISSING_PAGE_EMPTY]", "").strip()
            clean_sequence = re.sub(r'\n\s*\n', '\n\n', clean_sequence)
            
            full_markdown_result.append(f"\n{clean_sequence}")
            
    return "\n\n---\n\n".join(full_markdown_result)

if __name__ == "__main__":
    from configs.config import TEST_PDF_PATH
    result = my_finetuned_ocr_tool_full(TEST_PDF_PATH)
    print(result)