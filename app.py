from flask import Flask, request, jsonify
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# 🔑 Twój klucz dostępu do endpointa (nie mylić z OpenAI API key)
ACCESS_KEY = os.getenv("ACCESS_KEY") or "YOUR_SECRET_KEY"

# 🔑 Klucz OpenAI (GPT)
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # 🔐 Sprawdzenie klucza dostępu (Authorization header)
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {ACCESS_KEY}":
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()

        question = data.get("question")
        answers = data.get("answers")
        multiple = data.get("multiple", False)

        if not question or not answers:
            return jsonify({"error": "Brakuje pytania lub odpowiedzi"}), 400

        # 💬 Prompt do modelu
        messages = [
            {"role": "system", "content": "Jesteś ekspertem, który wybiera poprawne odpowiedzi na pytania wielokrotnego lub pojedynczego wyboru."},
            {"role": "user", "content": f"""Pytanie: {question}
Odpowiedzi: {answers}
Czy można zaznaczyć więcej niż jedną odpowiedź: {'Tak' if multiple else 'Nie'}
Które odpowiedzi są poprawne? Wypisz dokładnie poprawne odpowiedzi, tak jak są w oryginalnej liście – bez dodawania cudzysłowów ani zmian. Jeśli więcej niż jedna, oddziel przecinkami."""}
        ]

        # 🔁 Wywołanie OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        content = response.choices[0].message.content.strip()
        correct_answers = [ans.strip() for ans in content.split(",")] if multiple else [content.strip()]

        return jsonify({"correct_answers": correct_answers})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
