from sentence_transformers import SentenceTransformer, util

print(">>> Đang tải Model AI (all-MiniLM-L6-v2) vào RAM... Vui lòng đợi...")
# Sử dụng model all-MiniLM-L6-v2: Siêu nhẹ, siêu nhanh, phù hợp cho đồ án
model = SentenceTransformer('all-MiniLM-L6-v2')
print(">>> Tải Model AI hoàn tất! Sẵn sàng chấm điểm.")

def calculate_match_score(job_text: str, cv_text: str) -> float:
    try:
        # 1. Xử lý ngoại lệ nếu text bị rỗng
        if not job_text or not cv_text:
            return 0.0

        # 2. Biến đổi Văn bản (Text) thành Vector (Dải số)
        job_embedding = model.encode(job_text, convert_to_tensor=True)
        cv_embedding = model.encode(cv_text, convert_to_tensor=True)

        # 3. Dùng Toán học tính độ tương đồng Cosine giữa 2 Vector
        # Kết quả trả về là 1 Tensor, dùng .item() để lấy ra con số thực
        cosine_score = util.cos_sim(job_embedding, cv_embedding).item()

        # 4. Chuyển thành phần trăm (%) và làm tròn 2 chữ số thập phân
        # Ví dụ: 0.8543 -> 85.43
        percentage_score = round(cosine_score * 100, 2)

        # Tránh trường hợp điểm bị âm (do cấu trúc từ vựng ngược nhau)
        if percentage_score < 0:
            percentage_score = 0.0

        return percentage_score

    except Exception as e:
        raise Exception(f"Lỗi khi tính toán AI Matching: {str(e)}")