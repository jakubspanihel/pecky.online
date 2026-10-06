// Malý slovník synonym/aliasů pro rozšíření dotazu (jen v době dotazu; index se nemění).
// Každá skupina je množina slov; token dotazu ze skupiny přidá ostatní členy s nižší váhou.
// Slova se převádějí stejnou tokenizací jako text (bez diakritiky, zkrácení na 6 znaků).

export const SYNONYM_GROUPS: string[][] = [
  ["telefon", "mobil", "kontakt", "email", "mail", "e-mail"],
  ["starosta", "starosty", "starostovi", "primátor", "představitel"],
  ["místostarosta", "místostarosty", "místostarostka"],
  ["radní", "rada", "rady", "radnice"],
  ["zastupitel", "zastupitelé", "zastupitelstvo", "zastupitelstva"],
  ["tělocvična", "tělocvičny", "dostavba", "aula", "učebny", "učeben", "ZŠ"],
  ["pozemek", "pozemky", "parcela", "parcely", "prodej", "koupě", "odkoupení", "nemovitost"],
  ["smlouva", "smlouvy", "zakázka", "zakázky", "dodatek"],
  ["volby", "volební", "kandidát", "kandidáti", "kandidátka", "výsledky", "hlasy"],
  ["oběd", "obědy", "menu", "restaurace", "jídlo", "polední"],
  ["akce", "kalendář", "událost", "události", "program", "koncert"],
  ["noviny", "zpravodaj", "časopis"],
  ["rozpočet", "hospodaření", "finance", "výdaje", "příjmy"],
  ["dotace", "grant", "příspěvek", "podpora"],
  ["škola", "školka", "školství", "školní"],
  ["komise", "výbor", "sbor"],
  ["silnice", "komunikace", "chodník", "oprava"],
  ["odpad", "odpady", "popelnice", "svoz", "sběrný"],
];
