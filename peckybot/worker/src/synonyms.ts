// Malý slovník synonym/aliasů pro rozšíření dotazu (jen v době dotazu; index se nemění).
// Každá skupina je množina slov; token dotazu ze skupiny přidá ostatní členy s nižší váhou.
// Slova se převádějí stejnou tokenizací jako text (bez diakritiky, zkrácení na 6 znaků).

export const SYNONYM_GROUPS: string[][] = [
  ["telefon", "mobil", "kontakt", "email", "mail", "e-mail"],
  ["starosta", "starosty", "starostovi", "primátor", "představitel"],
  ["místostarosta", "místostarosty", "místostarostka"],
  ["radní", "rada", "rady", "rado", "radě", "radu", "radou", "radnice"],
  ["zastupitel", "zastupitelé", "zastupitelstvo", "zastupitelstva"],
  ["tělocvična", "tělocvičny", "dostavba", "aula", "učebny", "učeben", "ZŠ"],
  ["pozemek", "pozemky", "parcela", "parcely", "prodej", "koupě", "odkoupení", "nemovitost"],
  ["smlouva", "smlouvy", "zakázka", "zakázky", "dodatek"],
  ["volby", "volební", "kandidát", "kandidáti", "kandidátka", "výsledky", "hlasy"],
  ["oběd", "obědy", "menu", "restaurace", "jídlo", "polední"],
  ["akce", "kalendář", "událost", "události", "program", "koncert"],
  ["noviny", "zpravodaj", "časopis"],
  ["rozpočet", "hospodaření", "finance", "výdaje", "příjmy"],
  ["dotace", "dotací", "dotaci", "dotacemi", "grant", "příspěvek", "podpora"],
  ["škola", "základní", "školství", "školní"],
  ["školka", "mateřská", "školky"],
  ["komise", "komisi", "komisí", "komisích", "výbor", "výboru", "výboru", "sbor"],
  ["silnice", "komunikace", "chodník", "oprava"],
  ["odpad", "odpady", "popelnice", "kontejner", "kontejnery", "sběrný"],
  ["svoz", "vývoz", "vyvážejí", "odvoz", "sběr"],
  ["papír", "papíru", "papíry"],
  ["bagr", "bagry", "stavba", "staveniště", "dostavba", "stavební"],
  ["víkend", "sobota", "neděle"],
];
