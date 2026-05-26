Link: https://www.kaggle.com/code/danghiennguyen/raw-success

Github: https://github.com/ndhien945/NLP4b-done

Link bộ dữ liệu dùng để đánh giá: https://www.kaggle.com/datasets/danghiennguyen/arxiv-pdf-big

Link demo web: https://youtu.be/78zRLF5UaPo

Link bộ dữ liệu dùng để demo web: https://www.kaggle.com/datasets/danghiennguyen/arxiv-pdf-small

Link slide: https://drive.google.com/file/d/1--T_Clp6USmF15x2dttVFHoI-mq3jTP1/view?usp=sharing 

## Tổng quan bài toán
Đây là hệ thống Chuyển đổi file tài liệu định dạng PDF sang định dạng Markdown có cấu trúc. Hệ thống có thể nhận diện được tiêu đề, đoạn văn, và quan trọng nhất là các biểu thức toán học phức tạp mà không làm gãy phông hoặc sai lệch ký tự. 
Sau đó, hệ thống cho phép người dùng đặt câu hỏi trực tiếp. Hệ thống sẽ tự động phân tách tài liệu, và sử dụng mô hình ngôn ngữ lớn (LLM) để trích xuất câu trả lời chính xác nhất.

## Cách setup môi trường
Cài đặt các thư viện theo file requirements.txt, file requirements.txt được tạo ra bởi lệnh
```python
pipreqs . --force
```

Để cài đặt các thư viện trên, ta dùng lệnh
```python
pip install -r requirements.txt
```

Sau đó, ta sẽ khởi chạy các file python:
```python
python <các_file>.py
```

Về phần Web, em đã tổng hợp các file thành một file ai-agentic.ipynb để dễ tạo tunnel từ Kaggle nhằm kết với với web ở Visual Studio Code.
Để thuận tiện hơn, ta có thể cài thêm extension Live Server để hỗ trợ deploy web.




