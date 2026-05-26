const OCR_SERVER_URL = "https://monsoonal-unbolstered-elizabet.ngrok-free.dev/upload-pdf"; 
const AGENT_SERVER_URL = "https://monsoonal-unbolstered-elizabet.ngrok-free.dev";    

document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('gemini-file-input');
    const previewArea = document.getElementById('preview-area');
    const previewFileName = document.getElementById('preview-file-name');
    const previewFileStatus = document.getElementById('preview-file-status');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatBox = document.getElementById('chat-box');

    let selectedFile = null; 
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        const fileExt = file.name.split('.').pop().toLowerCase();
        if (fileExt !== 'pdf' && fileExt !== 'md') {
            alert("Hệ thống chỉ hỗ trợ xử lý tệp tin định dạng .pdf hoặc .md!");
            return;
        }
        selectedFile = file;
        previewFileName.textContent = file.name;
        previewFileStatus.textContent = fileExt === 'pdf' ? "Tệp PDF (Sẽ chạy xử lý OCR)" : "Tệp Markdown (Sẵn sàng nạp)";
        previewArea.style.display = "block";
    }

    removeFileBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        previewArea.style.display = "none";
    });
    sendBtn.addEventListener('click', handleSendAction);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendAction();
    });

    async function handleSendAction() {
        const text = userInput.value.trim();
        if (!text && !selectedFile) return;
        if (text) {
            appendMessage(text, 'user-msg');
            userInput.value = ''; 
        }
        if (selectedFile) {
            const currentFile = selectedFile;
            selectedFile = null;
            previewArea.style.display = "none";

            const fileExt = currentFile.name.split('.').pop().toLowerCase();
            const loadingMsgDiv = appendMessage(`Đang tải lên và phân tích tài liệu: <b>${currentFile.name}</b>...`, 'ai-msg');

            try {
                if (fileExt === 'pdf') {
                    loadingMsgDiv.innerHTML = `Đang thực hiện OCR hình ảnh từ file PDF bằng mô hình Nougat...`;
                    const ocrFormData = new FormData();
                    ocrFormData.append("file", currentFile);

                    const ocrResponse = await fetch(OCR_SERVER_URL, { method: 'POST', body: ocrFormData });
                    if (!ocrResponse.ok) throw new Error("Không thể kết nối đến máy chủ xử lý OCR PDF");
                    
                    const markdownText = await ocrResponse.text();
                    
                    loadingMsgDiv.innerHTML = `Đang số hóa tài liệu và nạp dữ liệu tri thức vào AI Agentic...`;
                    const blob = new Blob([markdownText], { type: 'text/markdown' });
                    const agentFormData = new FormData();
                    agentFormData.append("file", blob, `${currentFile.name.split('.')[0]}.md`);

                    const agentLoadResponse = await fetch(`${AGENT_SERVER_URL}/upload-markdown`, { method: 'POST', body: agentFormData });
                    if (!agentLoadResponse.ok) throw new Error("Máy chủ AI Agent không tiếp nhận cấu trúc bộ nhớ");

                    loadingMsgDiv.innerHTML = `<b>[Hệ thống]:</b> Đã nạp thành công tài liệu: <u>${currentFile.name}</u> vào bộ nhớ AI Agent.`;
                } 
                else if (fileExt === 'md') {
                    const agentFormData = new FormData();
                    agentFormData.append("file", currentFile);

                    const agentLoadResponse = await fetch(`${AGENT_SERVER_URL}/upload-markdown`, { method: 'POST', body: agentFormData });
                    if (!agentLoadResponse.ok) throw new Error("Máy chủ AI Agent không phản hồi dữ liệu");

                    loadingMsgDiv.innerHTML = `<b>[Hệ thống]:</b> Đã nạp thành công file tri thức: <u>${currentFile.name}</u>.`;
                }
                if (text) {
                    await callAgentChatQuery(text);
                }

            } catch (err) {
                loadingMsgDiv.innerHTML = `Lỗi tiến trình xử lý tài liệu: ${err.message}. Vui lòng kiểm tra lại trạng thái kết nối Server Kaggle.`;
            }
        } 
        else if (text) {
            await callAgentChatQuery(text);
        }
    }
    async function callAgentChatQuery(questionString) {
        const aiMsgDiv = appendMessage("AI Agent đang trích xuất dữ liệu và suy nghĩ...", 'ai-msg');
        try {
            const response = await fetch(`${AGENT_SERVER_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: questionString })
            });
            if (!response.ok) throw new Error("Mất kết nối với dịch vụ AI Agent");
            
            const data = await response.json();
            aiMsgDiv.textContent = data.answer; 
        } catch (error) {
            aiMsgDiv.textContent = `Hệ thống không phản hồi. Hãy đảm bảo bạn đã tải tài liệu lên trước khi đặt câu hỏi.`;
        }
    }

    function appendMessage(content, className) {
        const msgDiv = document.createElement('div');
        msgDiv.className = className;
        if (className === 'ai-msg') {
            try {
                msgDiv.innerHTML = marked.parse(content);
            } catch (e) {
                msgDiv.innerHTML = content;
            }
        } else {
            msgDiv.textContent = content;
        }
        
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight; 
        return msgDiv;
    }
    const ocrFileInput = document.getElementById('pdf-file');
    const convertBtn = document.getElementById('convert-btn');
    const resultContainer = document.getElementById('result-container');
    const convertStatus = document.getElementById('convert-status');
    const downloadLink = document.getElementById('download-link');

    if (convertBtn && ocrFileInput) {
        convertBtn.addEventListener('click', async () => {
            const file = ocrFileInput.files[0];
            if (!file) {
                alert("Vui lòng chọn một tệp tin PDF trước khi bấm nút phân tích!");
                return;
            }
            const fileExt = file.name.split('.').pop().toLowerCase();
            if (fileExt !== 'pdf') {
                alert("Hệ thống ở phần này chỉ hỗ trợ xử lý tệp tin định dạng .pdf!");
                return;
            }
            resultContainer.style.display = "block";
            convertStatus.innerHTML = "Đang thực hiện OCR hình ảnh từ file PDF bằng mô hình Nougat (Vui lòng đợi)...";
            downloadLink.style.display = "none";

            try {
                const formData = new FormData();
                formData.append("file", file);

                const response = await fetch(OCR_SERVER_URL, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Không thể kết nối đến máy chủ xử lý OCR PDF. Vui lòng kiểm tra Server Kaggle.");
                const markdownText = await response.text();
                const blob = new Blob([markdownText], { type: 'text/markdown' });
                const downloadUrl = URL.createObjectURL(blob);
                downloadLink.href = downloadUrl;
                downloadLink.download = file.name.substring(0, file.name.lastIndexOf('.')) + ".md";
                downloadLink.style.display = "inline-block";
                
                convertStatus.innerHTML = "<b>Xử lý OCR thành công!</b> Bạn có thể tải tệp tin Markdown về máy ở nút bên dưới.";

            } catch (err) {
                convertStatus.innerHTML = `Lỗi tiến trình OCR: ${err.message}`;
            }
        });
    }
});