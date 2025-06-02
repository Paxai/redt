from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Ustaw klucz API (można przez zmienne środowiskowe)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        question = data.get("question")
        answers = data.get("answers")
        multiple = data.get("multiple")

        if not question or not answers:
            return jsonify({"error": "Brakuje danych"}), 400

        messages = [
            {"role": "system", "content": "Jesteś ekspertem, który pomaga wybierać poprawne odpowiedzi na pytania."},
            {"role": "user", "content": f"Pytanie: {question}\nOdpowiedzi: {answers}\nCzy można zaznaczyć więcej niż jedną odpowiedź: {'Tak' if multiple else 'Nie'}\nKtóra odpowiedź jest poprawna? Przepisz poprawną odpowiedź lub odpowiedzi (jeśli więcej niż jedna) tak jak były bez cudzysłowów ani nic sam tekst."}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        content = response.choices[0].message.content.strip()

        if multiple:
            correct_answers = [x.strip() for x in content.split(",")]
        else:
            correct_answers = [content]

        return jsonify({"correct_answers": correct_answers})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# uruchamianie aplikacji
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
