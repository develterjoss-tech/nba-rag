from pathlib import Path
import json
import random

SECTIONS = Path("data/interim/sections.json")


def split_questions(questions, seed=42) :
    sections = json.loads(SECTIONS.read_text(encoding="utf-8"))
    ids ={s["id"] for s in sections}
    for question in questions :
        for gold_id in question["gold_ids"] :
            if gold_id not in ids :
                raise ValueError(f"question: {question["qid"]},id introuvable:{gold_id} ")

    random.seed(seed)
    dev=[]
    test=[]

    for t in ["lexical","multi","paraphrase"] :
        groupe = [ q for q in questions if q["type"]== t]
        random.shuffle(groupe)
        n = round(len(groupe) / 3)
        dev.extend(groupe[:n])
        test.extend(groupe[n:])

    path_test= Path("eval/questions_test.json")
    path_dev= Path("eval/questions_dev.json")
    path_test.parent.mkdir(parents=True,exist_ok=True)
    path_dev.parent.mkdir(parents=True,exist_ok=True)
    path_test.write_text(json.dumps(test,indent=2,ensure_ascii=False))
    path_dev.write_text(json.dumps(dev,indent=2,ensure_ascii=False),encoding="utf-8")

    return dev,test

if __name__ == "__main__" :
    questions = json.loads(Path("eval/questions.json").read_text(encoding="utf-8"))
    dev,test = split_questions(questions,seed=42)
    print(f"Len dev : {len(dev)}, Len test : {len(test)}")