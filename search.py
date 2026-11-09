from pathlib import Path
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import json
import numpy as np
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

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
CACHE = Path("data/interim/embeddings.npy")

def load_embeddings() :

    if CACHE.exists() :
        emb = np.load(CACHE)
    else :
        emb = embedding_model.encode(textes,normalize_embeddings=True,show_progress_bar=True)
        np.save(CACHE,emb)

    return emb

emb = load_embeddings()
#print(emb.shape, embedding_model.max_seq_length)


def search_embed(question,k=5) :
    q = embedding_model.encode([question],normalize_embeddings=True)[0]
    scores = emb @ q 
    indices = scores.argsort()[::-1][:k]
    return [ids[i] for i in indices]
        



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
#print(evaluate(search_random, dev))
#print(evaluate(search_bm25, dev))
#print("=== EMBEDDINGS ===")
#print(evaluate(search_embed, dev))

for nom, fn in [("random", search_random), ("BM25", search_bm25), ("embeddings", search_embed)]:
    r = evaluate(fn, dev)
    rec, mrr = r["recall@5"], r["mrr"]
    print(f"| {nom} | {rec['global']:.2f} | {mrr['global']:.2f} | {rec['lexical']:.2f} | {rec['paraphrase']:.2f} | {rec['multi']:.2f} |")

def rang(resultats, gold):
    return next((i for i, r in enumerate(resultats, 1) if r in gold), None)

print("\n=== DIFFÉRENCES BM25 vs EMBEDDINGS (dev) ===")
for q in dev:
    rb = search_bm25(q["q"], 5)
    re_ = search_embed(q["q"], 5)
    sb = recall_at_k(rb, q["gold_ids"])
    se = recall_at_k(re_, q["gold_ids"])
    if sb != se or rang(rb, q["gold_ids"]) != rang(re_, q["gold_ids"]):
        print(f'{q["type"]:10} | BM25 {sb:.2f} rang {rang(rb, q["gold_ids"])} | EMB {se:.2f} rang {rang(re_, q["gold_ids"])} | {q["q"]}')