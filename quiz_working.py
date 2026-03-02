#!/usr/bin/env python

import re
import random

def parse_questions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Lösungen extrahieren
    answer_pattern = re.findall(r"(\d+)\s+Correct Answer:\s*([A-Z]+)", content)
    solutions = {int(num): ans.strip() for num, ans in answer_pattern}

    # Fragen inklusive Nummer finden
    question_pattern = re.findall(
        r"QUESTION\s+(\d+)\n(.*?)(?=\nQUESTION\s+\d+|\n\d+\s+Correct Answer:)",
        content,
        re.DOTALL
    )

    questions = []

    for number_str, block in question_pattern:
        number = int(number_str)

        lines = block.strip().split("\n")
        question_lines = []
        options = []

        for line in lines:
            line = line.strip()
            if re.match(r"^[A-E]\.", line):
                options.append(line)
            else:
                question_lines.append(line)

        questions.append({
            "number": number,
            "question": " ".join(question_lines),
            "options": options,
            "answer": solutions.get(number, "")
        })

    return questions


def run_quiz(questions):
    score = 0
    random.shuffle(questions)

    for q in questions:
        print("\n" + "="*60)
        print(f"QUESTION {q['number']}")
        print(q["question"])
        print()

        for option in q["options"]:
            print(option)

        user_input = input("\nYour answer: ").strip()

        # ----------------------------------------
        # FALL 1: Multiple Choice (A–E vorhanden)
        # ----------------------------------------
        if q["options"]:
            given_set = set(user_input.upper().replace(" ", ""))
            correct_set = set(q["answer"].upper())

            valid_letters = {"A", "B", "C", "D", "E"}
            given_set = given_set.intersection(valid_letters)

            if given_set == correct_set:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Wrong! Correct answer: {''.join(sorted(correct_set))}")

        # ----------------------------------------
        # FALL 2: Freitext mit | getrennten Lösungen
        # ----------------------------------------
        else:
            valid_answers = [a.strip() for a in q["answer"].split("|")]

            # normalize (case-insensitive + trailing slash tolerant)
            normalized_input = user_input.strip().lower().rstrip("/")

            normalized_valid = [
                a.lower().rstrip("/") for a in valid_answers
            ]

            if normalized_input in normalized_valid:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Wrong! Correct answer: {q['answer']}")

    print("\n" + "="*60)
    print(f"Final score: {score} / {len(questions)}")

if __name__ == "__main__":
    filename = "fragen.txt"
    questions = parse_questions(filename)
    run_quiz(questions)
