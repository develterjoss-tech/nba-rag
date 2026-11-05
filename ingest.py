import wikipediaapi
import json
import re
from pathlib import Path

wiki = wikipediaapi.Wikipedia(user_agent="rag-nba-perso joss.applestore@gmail.com",language="en")

EXCLUDED = {"References", "External links", "See also", "Notes", "Further reading"}
RAW = Path("data/raw")
PAGES = [
    # 30 franchises
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
    "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
    "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns",
    "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors",
    "Utah Jazz", "Washington Wizards",
    # 20 joueurs
    "Stephen Curry", "Derrick Rose", "LeBron James", "Michael Jordan", "Kobe Bryant",
    "Kevin Durant", "Nikola Jokić", "Giannis Antetokounmpo", "Luka Dončić",
    "Victor Wembanyama", "Shai Gilgeous-Alexander", "Jayson Tatum", "Joel Embiid",
    "Tim Duncan", "Shaquille O'Neal", "Magic Johnson", "Larry Bird",
    "Kareem Abdul-Jabbar", "Dirk Nowitzki", "Kawhi Leonard",
]



# output : [{"path": "Early life, family and education", "text": "Curry was born on March 14, 1988..."},{"path": "College career >
def flatten(sections, parent_path="") :
    res = []
    for section in sections :
        if parent_path :
            path = parent_path + " > " + section.title
        else :
            path = section.title
        if section.text  :
            res.append({"path" : path, "text" : section.text})
        res.extend(flatten(section.sections,parent_path=path))

    return res

def  download_page(title) :
    path_res = Path( f"data/raw/{title}.json" )
    if path_res.exists() :
            res = json.loads(path_res.read_text(encoding="utf-8"))
    path_res.parent.mkdir(parents=True,exist_ok=True)
    page_download = wiki.page(title)
    if not page_download.exists() :
        raise ValueError({f"Page Introuvable: {title}"})
    

    flat = flatten(page_download.sections)
        
    res = { "title" : title,
            "summary": page_download.summary,
            "sections" : flat  }
    
    compte_rendu = json.dumps(res,indent=2,ensure_ascii=False)
    path_res.write_text(compte_rendu,encoding="utf-8")

    return  res

def slugify(texte:str) :
     res = texte.lower() 
     return re.sub(r"[^a-z0-9]+", "-", res).strip("-")


def build_sections(raw_pages) :
    res =[]
    for page in raw_pages :
        title_id = slugify(page["title"])
        res.append({
            "id" : title_id + "#summary",
            "page" : page["title"],
            "path" : "Summary",
            "text" : page["summary"]
                })
        
        for section in page["sections"] :
            morceaux = section["path"].split(" > ")

            section_id = slugify(page["title"])+"#"+"/".join(slugify(m) for m in morceaux)
            if morceaux[0] not in EXCLUDED :
                res.append({
                    "id":section_id,
                    "page":page["title"],
                    "path":section["path"],
                    "text":section["text"]
                      })
    
    ids = [s["id"] for s in res]
    assert len(ids) == len(set(ids)), "IDs en double"

    return res



def main() :
    raw_pages =[download_page(t) for t in PAGES]
    sections = build_sections(raw_pages=raw_pages)
    path_sec = Path("data/interim/sections.json")
    path_sec.parent.mkdir(parents=True,exist_ok=True)

    file = json.dumps(sections,indent=2,ensure_ascii=False)
    path_sec.write_text(file,encoding="utf-8")
    longueurs = sorted(len(s["text"].split()) for s in sections)
    print(f"{len(raw_pages)} pages")
    print(f"{len(sections)} sections")
    print(f"longueur (mots) : min {longueurs[0]}, médiane {longueurs[len(longueurs) // 2]}, max {longueurs[-1]}")


if __name__ == "__main__" :
    main()
          
     

#TEST=================================
#for s in flatten(list_sections):
 #   print(s["path"])

#print(download_page("Derrick Rose"))
#print(slugify("Stephen Curry")) 

#sections = build_sections([download_page("Derrick Rose")])
#for s in sections[:5]:
#    print(s["id"])
#print(len(sections))