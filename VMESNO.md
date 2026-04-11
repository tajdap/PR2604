# Vpliv socio-ekonomskih dejavnikov na rodnost v Sloveniji

## Opis problema
V zadnjih letih je bilo veliko govora o upadu rodnosti v Sloveniji. Namen tega projekta je raziskati kateri dejavniki (višina plač, stopnja urbanizacije, stopnja zaposlenosti, dostop do stanovanj, izobrazba ipd.) korelirajo z rodnostjo v državi. 

**Cilj projekta** je raziskati kateri dejavnik ima največji negativen/pozitiven vpliv na rodnost.

## Vprašanja
- Kako plača (povprečna plača, minimalna plača) vpliva na rodnost v posamezni občini ali regiji?
- Ali obstaja povezava med stopnjo zaposlenosti/brezposelnosti in rodnostjo?
- Kako stopnja urbanizacije (mesto vs. podeželje) vpliva na število rojstev?
- Ali višja stopnja izobrazbe prebivalstva vpliva na nižjo/višjo rodnost?

Do vmesnega poročila smo okvirno analizirali podatke zadanih tem in jih grafično prikazali.

## Vir in oblika podatkov
Projekt temelji na odprtih podatkih v obliki tabel na strani SiStat (SURS) 

Za obdelavo podatkov smo uporabili sledeče vire:
- letno število živorojenih (po [regijah](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/05J2008S.px) in [občinah](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/05J2014S.px))
- Povprečne mesečne plače pri pravnih osebah (po [regijah](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/0701023S.px) in [občinah](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/0701024S.px))  
- [stopnja zaposlenosti/brezposelnosti](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/Data/2640005S.px/) 
- [stopnja izobrazbe matere, ko se otrok rodi](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/Data/05J1027S.px/)
- [živorojeni v zakonski zvezi ali zunaj zakonske zveze](https://pxweb.stat.si/SiStatData/pxweb/sl/Data/Data/05J1018S.px/)

## Analiza podatkov

### Rodnost glede na tip okolja
Iz podatkov o gostoti naseljenosti občin, lahko okvirno določimo kakšen tip naselij tam prevladuje. Za podeželjske občine smo vzeli gostoto do 200 prebivalcev na kvadratni meter, za mesto pa vse kar je več od tega. To smo združili s podatki o številu živorojenih na 1000 ljudi posamezne občine.

S tem lahko vidimo, da je rodnost na splošno skozi leta upadala, med letoma 2013-2018 pa se je tudi zgodila ta sprememba, da je rodnost v mestih začela upadati močneje kot na podeželju. Tako je v zadnjih nekaj letih veliko več rojstev v manjših naseljih, morda zaradi večje prisotnosti tradicionalnih vrednot kot v mestih.
![Graf rodnosti](slike/graf_tip_okolja.png)
*Slika 1: Povprečna rodnost v obdobju 2007-2023.*

### Zemljevid rodnosti po občinah
**Največja rodnost** je opazna predvsem v predmestjih Ljubljane. Lahko bi sklepali, da se mladi selijo na obrobje mesta, oziroma je življenje tam bolj cenovno ugodno, sploh kar se tiče nepremičnin, ki so ključen del za ustvarjanje družine. Lahko pa bi sklepali tudi, da gre za vrednote, močne rdeče lise namreč lahko opazimo tudi na jugovzhodu, ter na območju Gorenja vas - Poljane. To so bolj tradicionalno usmerjena območja, kjer je podeželjski način življenja še vedno močno povezan z velikimi družinami. Nobeno od večjih, moderniziranih mest namreč ni temneje obarvano.

**Nizka rodnost** pa je predvsem na odročnih delih in hribovitih legah, kjer se nahajajo le kakšne samotne kmetije - Bovec in Kranjska Gora sredi Alp, ter na Pohorju Ruše in Podvelka. Prav tako je zeleno-rumeno tudi Prekmurje, kjer je mladih vedno manj.

*Občine, ki so obarvane sivo, so v podatkih v tabelah poimenovane drugače, kot v datoteki interaktivnega zemljevida.*

![Zemljevid rodnosti](slike/rodnost_zemljevid.png)
*Slika 2: Porazdelitev rodnosti po slovenskih občinah.*
