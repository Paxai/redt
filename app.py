from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Pobieranie klucza API z ENV
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("Brakuje zmiennej środowiskowej OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        print("[DEBUG] Dane wejściowe:", data)

        question = data.get("question")
        answers = data.get("answers")
        multiple = data.get("multiple", False)

        if not question or not answers:
            return jsonify({"error": "Brakuje pytania lub odpowiedzi"}), 400

        messages = [
            {
                "role": "system",
                "content": "Jesteś ekspertem, który pomaga wybierać poprawne odpowiedzi na pytania."
            },
            {
                "role": "user",
                "content": (
                    f"Pytanie: {question}\n"
                    f"Odpowiedzi: {answers}\n"
                    f"Czy można zaznaczyć więcej niż jedną odpowiedź: {'Tak' if multiple else 'Nie'}\n"
                    f"Która odpowiedź jest poprawna? Przepisz poprawną odpowiedź lub odpowiedzi "
                    f"(jeśli więcej niż jedna) tak jak były, bez cudzysłowów i bez dodatkowych znaków. "
                    f"Tylko tekst odpowiedzi."
                )
            }
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        response_text = completion.choices[0].message.content.strip()
        print("[DEBUG] Odpowiedź GPT:", response_text)

        if multiple:
            correct_answers = [a.strip() for a in response_text.split(",") if a.strip()]
        else:
            correct_answers = [response_text]

        return jsonify({"correct_answers": correct_answers})

    except Exception as e:
        print("[ERROR] Błąd serwera:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
