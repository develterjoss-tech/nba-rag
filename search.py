from pathlib import Path
from rank_bm25 import BM25Okapi
import json
import random
import re


sections = json.loads(Path("data/interim/sections.json").read_text(encoding="utf-8"))
textes = []
ids = []

for section in sections :
    textes.append(
        section["page"] +" " + section["path"] + " " + section["text"]
    )
    ids.append(
        section["id"]
    )


def tokenize(texte: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", texte.lower())


def search_random(question,k=5) : #fais nimporte quoi expres, sert de comparaison
    return  random.Random(42).sample(ids, k)

corpus_tokenize = [tokenize(t) for t in textes]
bm25 = BM25Okapi(corpus=corpus_tokenize)


def search_bm25(question,k=5) :
    scores = bm25.get_scores(tokenize(question))
    indices = scores.argsort()[::-1][:k]
    return [ids[i] for i in indices]


def recall_at_k(results,gold_ids) :
    compteur = 0
    for result in results :
        if result in gold_ids :
            compteur+=1
    return compteur / len(gold_ids)

def reciprocal_rank(results, gold_ids) :
    for rank ,result in enumerate(results,start=1) :
        if result in gold_ids :
           return 1/rank
    return 0

def moyennes (dico:dict) -> dict : 
    toutes = sum(dico.values(),[])
    res = {"global":sum(toutes)/len(toutes) }
    for key ,value in dico.items() :
        res[key] = sum(value) / len(value)

    return res 


def evaluate(search_fn, questions, k=5) :
    recalls = {"lexical": [],"multi" : [], "paraphrase": [] }
    rrs =  {"lexical": [],"multi" : [], "paraphrase": [] }
    for question in questions :
        result = search_fn(question["q"],k)
        recall = recall_at_k(result,question["gold_ids"])
        rank = reciprocal_rank(result,question["gold_ids"])
        recalls[question["type"]].append(recall)
        rrs[question["type"]].append(rank)
        if recall ==0 :
            print(f"Question non trouvé : {question["q"]},Gold ids : {question["gold_ids"]}, Result : {result}")

    return {"recall@5": moyennes(recalls) , "mrr" : moyennes(rrs)}




    

#TEST ================================
#res = search_bm25("At what age did Derrick Rose win the NBA MVP award?")
#gold = ["derrick-rose#summary",
#        "derrick-rose#professional-career/chicago-bulls-2008-2016/2010-11-season-mvp-season"]
#print(recall_at_k(res, gold)) 
#print(reciprocal_rank(res, gold))  

dev = json.loads(Path("eval/questions_dev.json").read_text(encoding="utf-8"))
print(evaluate(search_random, dev))
print(evaluate(search_bm25, dev))

