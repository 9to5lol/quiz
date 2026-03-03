#!/usr/bin/env python

import re
import random
import sys

def parse_questions(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    questions = []

    # ----------------------------------------
    # 1. Nummerierte Lösungen am Dateiende einsammeln
    # (Format 1)
    # ----------------------------------------
    numbered_solutions = dict(
        re.findall(r"^\s*(\d+)\s+Correct Answer:\s*([^\n]+)",
                   content,
                   re.MULTILINE)
    )

    # ----------------------------------------
    # 2. QUESTION-Blöcke finden
    # ----------------------------------------
    question_blocks = re.findall(
        r"QUESTION\s+(\d+)(.*?)(?=QUESTION\s+\d+|\Z)",
        content,
        re.DOTALL
    )

    for number_str, block in question_blocks:
        number = int(number_str)

        # ----------------------------------------
        # 3. Antwort im Block suchen (Format 2)
        # ----------------------------------------
        answer_match = re.search(r"Correct Answer:\s*(.+)", block)

        if answer_match:
            answer = answer_match.group(1).strip()
        else:
            # Sonst aus Lösungstabelle (Format 1)
            answer = numbered_solutions.get(number_str, "").strip()

        # ----------------------------------------
        # 4. Alles vor "Correct Answer" ist Frage+Optionen
        # ----------------------------------------
        if answer_match:
            block = block[:answer_match.start()]

        lines = block.strip().split("\n")

        question_lines = []
        options = []

        for line in lines:
            stripped = line.strip()

            # Optionen erkennen (auch eingerückt)
            if re.match(r"^[A-E]\.", stripped):
                options.append(stripped)
            else:
                # Meta-Zeilen ignorieren
                if not stripped.startswith("Section") and \
                   not stripped.startswith("Explanation") and \
                   not stripped.startswith("#"):
                    question_lines.append(stripped)

        questions.append({
            "number": number,
            "question": " ".join(question_lines).strip(),
            "options": options,
            "answer": answer
        })

    return questions

def run_quiz(questions,cnt):
    score = 0
    random.shuffle(questions)

    i = 0
    for q in questions:
        i+=1
        if i > cnt:
          break

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
        perc = int( (score/cnt)*100)
        print(f"current score {score}/{cnt} ({perc} %)")

if __name__ == "__main__":
    cnt = int(sys.argv[1])
    questions = []
    questions += parse_questions("101-by.axel-mixed.txt")
    questions += parse_questions("fragen-github.txt")
    run_quiz(questions,cnt)
