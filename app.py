from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Pobieranie klucza API z ENV
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        question = data.get("question")
        answers = data.get("answers")
        multiple = data.get("multiple", False)

        if not question or not answers:
            return jsonify({"error": "Brakuje pytania lub odpowiedzi"}), 400

        messages = [
            {"role": "system", "content": "Jesteś ekspertem, który pomaga wybierać poprawne odpowiedzi na pytania."},
            {"role": "user", "content": f"Pytanie: {question}\nOdpowiedzi: {answers}\nCzy można zaznaczyć więcej niż jedną odpowiedź: {'Tak' if multiple else 'Nie'}\nKtóra odpowiedź jest poprawna? Przepisz poprawną odpowiedź lub odpowiedzi (jeśli więcej niż jedna) tak jak były bez cudzysłowów ani nic sam tekst."}
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        content = completion.choices[0].message.content.strip()

        if multiple:
            correct_answers = [a.strip() for a in content.split(",")]
        else:
            correct_answers = [content]

        return jsonify({"correct_answers": correct_answers})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
