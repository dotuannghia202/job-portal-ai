# services/vector_service.py
from dotenv import load_dotenv
import chromadb
import os
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Khởi tạo ChromaDB lưu trữ cục bộ trong thư mục ./chroma_data
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="custom_interview_bank")


def get_embedding(text: str) -> list[float]:
    """Use Gemini to convert text into vector embeddings"""
    result = client.models.embed_content(
        model="text-embedding-004",
        contents=text
    )
    return result.embeddings[0].values


def add_custom_question(question_id: str, specialization: str, question_text: str, rubric: str):
    """API to save your core questions to a Vector DB"""
    content_to_embed = f"Majors: {specialization}. Questions: {question_text}. Criteria: {rubric}"
    vector = get_embedding(content_to_embed)

    collection.add(
        ids=[question_id],
        embeddings=[vector],
        documents=[question_text],
        metadatas=[{
            "specialization": specialization,
            "rubric": rubric
        }]
    )


def search_custom_questions(query_text: str, n_results: int = 2) -> list[dict]:
    """Find core questions that best match the JD and CV"""
    if collection.count() == 0:
        return []

    query_vector = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(n_results, collection.count())
    )

    found_questions = []
    if results and results["documents"]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            found_questions.append({
                "question": doc,
                "specialization": meta.get("specialization"),
                "rubric": meta.get("rubric")
            })

    return found_questions