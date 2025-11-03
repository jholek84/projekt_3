##Projekt číslo 3: Election Scraper 

  

##Popis 

Cílem projektu je vyscrapovat z webu voleb do PSPČR výsledky za libovolnou obec.  

Do projektu jsem si vybral obce v okrese Olomouc. 

Odkaz: Výsledky hlasování za územní celky – výběr obce | volby.cz 

   

Potřebné knihovny: 

Potřebné knihovny, které jsem musel doinstalovat jsou uloženy ve složce requirements.txt.  Bylo nutné vytvořit si virtuální prostředí a nainstalovat balíčky. 

 

Projekt 

Pro spuštění projektu jsou třeba 2 povinné argumenty 

url územního celku 

Soubor.csv 

 

Argument 1: python main.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7102"  

Argument 2: "vysledky_olomouc_final.csv" 

 

Jak program spustit 

python main.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7102" "vysledky_olomouc_final.csv" 

 

Ukázka výstupu: 

500496,Olomouc,0,682,457,38,0,0,38,0,21,34,11,4,2,1,1,36,1,10,153,0,1,66,0,1,0,3,31,1 

589764,Nezamyslice,0,617,375,35,0,0,24,0,14,44,0,4,4,0,0,35,0,9,129,0,0,28,0,0,2,3,41,2 
