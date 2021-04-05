# -*- coding: UTF-8 -*-
# Copyright 2010-2014 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Loads all Belgian cities into the database.  Supposes that
:mod:`few_cities <lino_xl.lib.countries.fixtures.few_cities>` has also
been loaded and thus does not load the cities defined there.

This list of Belgian cities is in no way authoritative, but "works for me".

The result is available for public access under
http://belref.lino-framework.org

Original sources:

- http://www.charline.be/info/codepost/cpost.htm
- https://fr.wikibooks.org/wiki/N%C3%A9erlandais_pour_traducteurs_:_les_villes_belges

"""

from lino.core.utils import resolve_model
from lino.utils.instantiator import Instantiator
from lino.api import dd, rt


# german names are my spontaneous guessings...
belgian_cities_nl_fr = u"""
4770 |Amel                |Amblève              |Amel
2000 |Antwerpen           |Anvers               |Antwerpen
1547 |Bever               |Biévène              |Bever
8000 |Brugge              |Bruges               |Brügge
7780 |Komen-Waasten       |Comines-Warneton     |Comines-Warneton
7090 |'s-Gravenbrakel     |Braine-le-Comte      |Braine-le-Comte
8500 |Kortrijk            |Courtrai             |Kortrijk
8670 |Koksijde            |Coxyde               |Koksijde
8600 |Diksmuide           |Dixmude              |Diksmuide
7850 |Edingen             |Enghien              |Enghien
8587 |Spiere-Helkijn      |Espierres-Helchin    |Spiere-Helkijn
8587 |Spiere              |Espierres            |Spiere
8587 |Helkijn             |Helchin              |Helkijn
3790 |Voeren              |Fourons              |Fourons 
8630 |Veurne              |Furnes               |Veurne
1570 |Galmaarden          |Gammerages           |Galmaarden
9000 |Gent                |Gand                 |Gent
1470 |Genappe             |Genepiën             |Genappe
9500 |Geraardsbergen      |Grammont             |Grammont
1500 |Hal                 |Halle                |Halle 
4280 |Hannuit             |Hannut               |Hannut
9520 |Sint-Lievens-Houtem |Hautem-Saint-Liévin  |Sint-Lievens-Houtem
3540 |Herk-de-Stad        |Herck-la-Ville       |Herk-de-Stad
4500 |Hoei                |Huy                  |Huy
9830 |Sint-Martens-Latem  |Laethem-Saint-Martin |Sint-Martens-Latem
1310 |Terhulpen           |La Hulpe             |La Hulpe 
3440 |Zoutleeuw           |Léau                 |Léau
7860 |Lessen              |Lessines             |Lessines
4287 |Lijsem              |Lincent              |Lincent
3000 |Leuven              |Louvain              |Löwen
1348 |Louvain-la-Neuve    |Louvain-la-Neuve     |Neu-Löwen
2800 |Mechelen            |Malines              |Mechelen
8930 |Menen               |Menin                |Menen
3270 |Scherpenheuvel      |Montaigu             |Montaigu
7700 |Moeskroen           |Moucron              |Moucron
8620 |Nieuwpoort          |Nieuport             |Nieuwpoort
1400 |Nijvel              |Nivelles             |Nivelles 
4360 |Oerle               |Oreye                |Oreye 
1360 |Perwijs             |Perwez               |Perwez 
9100 |Sint-Niklaas        |Saint-Nicolas        |Saint-Nicolas
3800 |Sint-Truiden        |Saint-Trond          |Saint-Trond
3700 |Tongeren            |Tongres              |Tongeren
1800 |Vilvoorde           |Vilvorde             |Vilvoorde
8900 |Ieper               |Ypres                |Ypres
"""

belgian_cities = u"""
9420 Aaigem 
8511 Aalbeke 
9880 Aalter 
3200 Aarschot 
8700 Aarsele 
8211 Aartrijke 
2630 Aartselaar 
4557 Abée 
4280 Abolens 
3930 Achel 
5590 Achêne 
5362 Achet 
4219 Acosse 
6280 Acoz 
9991 Adegem 
8660 Adinkerke 
1790 Affligem 
9051 Afsnee 
5544 Agimont 
4317 Aineffe 
5310 Aische-en-Refail 
6250 Aiseau 
6250 Aiseau-Presles 
5070 Aisemont 
3570 Alken 
5550 Alle 
4432 Alleur 
1652 Alsemberg 
8690 Alveringem 
4540 Amay 
6680 Amberloup 
6953 Ambly 
4219 Ambresin 
6997 Amonines 
7750 Amougies 
4540 Ampsin 
5300 Andenne 
1070 Anderlecht 
6150 Anderlues 
4821 Andrimont 
7387 Angre 
7387 Angreau 
5537 Anhée 
6721 Anlier 
6890 Anloy 
5537 Annevoie-Rouillon 
5500 Anseremme 
7750 Anseroeul 
5520 Anthée 
4520 Antheit 
4160 Anthisnes 
7640 Antoing 
2018 Antwerpen 1
2020 Antwerpen 2 
2030 Antwerpen 3 
2040 Antwerpen 4 
2050 Antwerpen 5 
2060 Antwerpen 6 
7910 Anvaing 
8570 Anzegem 
9200 Appels 
9400 Appelterre-Eichem 
7811 Arbre (Ht.) 
5170 Arbre (Nam.) 
4990 Arbrefontaine 
7910 Arc-Ainières 
1390 Archennes 
7910 Arc-Wattripont 
8850 Ardooie 
2370 Arendonk 
4601 Argenteau 
6700 Arlon 
7181 Arquennes 
5060 Arsimont 
6870 Arville 
3665 As 
9404 Aspelare 
9890 Asper 
7040 Asquillies 
1730 Asse 
8310 Assebroek 
9960 Assenede 
6860 Assenois 
3460 Assent 
5330 Assesse 
9800 Astene 
7800 Ath 
7387 Athis 
6791 Athus 
3404 Attenhoven 
3384 Attenrode 
6717 Attert 
7941 Attre 
6790 Aubange 
7972 Aubechies 
4880 Aubel 
5660 Aublain 
6880 Auby-sur-Semois 
1160 Auderghem 
7382 Audregnies 
7040 Aulnois 
6706 Autelbas 
1367 Autre-Eglise 
7387 Autreppe 
5060 Auvelais 
5580 Ave-et-Auffe 
8630 Avekapelle 
8580 Avelgem 
4260 Avennes 
3271 Averbode 
4280 Avernas-le-Bauduin 
4280 Avin 
4340 Awans 
6870 Awenne 
4400 Awirs 
6900 Aye 
4630 Ayeneux 
4920 Aywaille 
9890 Baaigem 
3128 Baal 
# 9310 Baardegem
2387 Baarle-Hertog 
9200 Baasrode 
9800 Bachte-Maria-Leerne 
5550 Bagimont 
6464 Baileux 
6460 Bailièvre 
5555 Baillamont 
7730 Bailleul 
5377 Baillonville 
7380 Baisieux 
1470 Baisy-thy 
5190 Balâtre 
9860 Balegem 
2490 Balen 
9420 Bambrugge 
6951 Bande 
6500 Barbençon 
4671 Barchon 
5570 Baronville 
7534 Barry 
5370 Barvaux-Condroz 
6940 Barvaux-sur-Ourthe 
7971 Basècles 
4520 Bas-Oha 
4983 Basse-Bodeux 
4690 Bassenge 
9968 Bassevelde 
7830 Bassilly 
6600 Bastogne 
7784 Bas-Warneton 
3870 Batsheers 
4651 Battice 
7130 Battignies 
7331 Baudour 
7870 Bauffe 
7604 Baugnies 
1401 Baulers 
9520 Bavegem 
8531 Bavikhove 
9150 Bazel 
4052 Beaufays 
6500 Beaumont 
5570 Beauraing 
6980 Beausaint 
1320 Beauvechain 
6594 Beauwelz 
7532 Beclers 
3960 Beek 
9630 Beerlegem 
8730 Beernem 
2340 Beerse 
1650 Beersel 
8600 Beerst 
1673 Beert 
9080 Beervelde 
2580 Beerzel 
5000 Beez 
6987 Beffe 
3130 Begijnendijk 
6672 Beho 
1852 Beigem 
8480 Bekegem 
1730 Bekkerzeel 
3460 Bekkevoort 
5001 Belgrade 
4610 Bellaire 
7170 Bellecourt 
6730 Bellefontaine (Lux.) 
5555 Bellefontaine (Nam.) 
8510 Bellegem 
9881 Bellem 
6834 Bellevaux 
4960 Bellevaux-Ligneuville 
1674 Bellingen 
7970 Beloeil 
9111 Belsele 
4500 Ben-Ahin 
6941 Bende 
3540 Berbroek 
2600 Berchem (Antwerpen) 
9690 Berchem (O.-Vl.) 
1082 Berchem-Sainte-Agathe 
2040 Berendrecht 
1910 Berg (Bt.) 
3700 Berg (Limb.) 
4360 Bergilers 
3580 Beringen 
2590 Berlaar 
9290 Berlare 
3830 Berlingen 
4257 Berloz 
4607 Berneau 
7320 Bernissart 
6560 Bersillies-l'Abbaye 
3060 Bertem 
6687 Bertogne 
4280 Bertrée 
6880 Bertrix 
5651 Berzée 
8980 Beselare 
3130 Betekom 
4300 Bettincourt 
5030 Beuzet 
2560 Bevel 
4960 Bevercé 
9700 Bevere 
8791 Beveren (Leie) 
8800 Beveren (Roeselare) 
8691 Beveren-aan-den-Ijzer 
9120 Beveren-Waas 
3581 Beverlo 
3740 Beverst 
4610 Beyne-Heusay 
6543 Bienne-lez-Happart 
3360 Bierbeek 
6533 Biercée 
1301 Bierges 
1430 Bierghes 
4460 Bierset 
5380 Bierwart 
5640 Biesme 
5640 Biesmerée 
6531 Biesme-sous-Thuin 
1547 Biévène 
5555 Bièvre 
1390 Biez 
6690 Bihain 
8920 Bikschote 
4831 Bilstain 
3740 Bilzen 
7130 Binche 
3850 Binderveld 
3211 Binkom 
5537 Bioul 
8501 Bissegem 
7783 Bizet 
2830 Blaasveld 
5542 Blaimont 
7522 Blandain 
3052 Blanden 
8370 Blankenberge 
7040 Blaregnies 
7321 Blaton 
7370 Blaugies 
# 4670 Blégny 
7620 Bléharies 
4280 Blehen 
6760 Bleid 
4300 Bleret 
7903 Blicquy 
3950 Bocholt 
2530 Boechout 
3890 Boekhout 
9961 Boekhoute 
4250 Boëlhe 
8904 Boezinge 
1670 Bogaarden 
5550 Bohan 
5140 Boignée 
4690 Boirs 
7866 Bois-de-Lessines 
5170 Bois-de-Villers 
7170 Bois-d'Haine 
4560 Bois-et-Borsu 
5310 Bolinne 
4653 Bolland 
1367 Bomal (Bt.) 
6941 Bomal-sur-Ourthe 
4607 Bombaye 
3840 Bommershoven 
4100 Boncelles 
5310 Boneffe 
2820 Bonheiden 
5021 Boninne 
1325 Bonlez 
6700 Bonnert 
5300 Bonneville 
7603 Bon-Secours 
5377 Bonsin 
2221 Booischot 
8630 Booitshoeke 
2850 Boom 
3631 Boorsem 
3190 Boortmeerbeek 
1761 Borchtlombeek 
2140 Borgerhout (Antwerpen) 
3840 Borgloon 
4317 Borlez 
3891 Borlo 
6941 Borlon 
2880 Bornem 
1404 Bornival 
2150 Borsbeek (Antw.) 
9552 Borsbeke 
5032 Bossière 
8583 Bossuit 
1390 Bossut-Gottechain 
3300 Bost 
5032 Bothey 
9820 Bottelare 
6200 Bouffioulx 
5004 Bouge 
7040 Bougnies 
6830 Bouillon 
6464 Bourlers 
5575 Bourseigne-Neuve 
5575 Bourseigne-Vieille 
7110 Boussoit 
7300 Boussu 
5660 Boussu-en-Fagne 
6440 Boussu-lez-Walcourt 
1470 Bousval 
3370 Boutersem 
5500 Bouvignes-sur-Meuse 
7803 Bouvignies 
2288 Bouwel 
8680 Bovekerke 
3870 Bovelingen 
4300 Bovenistier 
5081 Bovesse 
6671 Bovigny 
4990 Bra 
7604 Braffe 
5590 Braibant 
1420 Braine-l'Alleud 
1440 Braine-le-Château 
4260 Braives 
9660 Brakel 
5310 Branchon 
6800 Bras 
7604 Brasmenil 
2930 Brasschaat 
7130 Bray 
2960 Brecht 
8450 Bredene 
3960 Bree 
2870 Breendonk 
4020 Bressoux 
8900 Brielen 
2520 Broechem 
3840 Broekom 
1931 Brucargo 
7940 Brugelette 
5660 Brûly 
5660 Brûly-de-Pesche 
7620 Brunehaut 
1785 Brussegem 
1120 Brussel 12
1130 Brussel 13 
1140 Brussel 14 
1150 Brussel 15 
1160 Brussel 16 
1170 Brussel 17 
1180 Brussel 18 
1190 Brussel 19 
1020 Brussel 2 
1200 Brussel 20 
1210 Brussel 21 
1030 Brussel 3 
1040 Brussel 4 
1050 Brussel 5 
1060 Brussel 6 
1070 Brussel 7 
1080 Brussel 8 
1090 Brussel 9 
3800 Brustem 
# 1000 Bruxelles 1 
1120 Bruxelles 12 
1130 Bruxelles 13 
1140 Bruxelles 14 
1150 Bruxelles 15 
1160 Bruxelles 16 
1170 Bruxelles 17 
1180 Bruxelles 18 
1190 Bruxelles 19 
1020 Bruxelles 2 
1200 Bruxelles 20 
1210 Bruxelles 21 
1030 Bruxelles 3 
1040 Bruxelles 4 
1050 Bruxelles 5 
1060 Bruxelles 6 
1070 Bruxelles 7 
1080 Bruxelles 8 
1090 Bruxelles 9 
7641 Bruyelle 
6222 Brye 
3440 Budingen 
9255 Buggenhout 
7911 Buissenal 
5580 Buissonville 
1501 Buizingen 
1910 Buken 
# 4760 Bullange 
# 4760 Büllingen 
8630 Bulskamp 
3380 Bunsbeek 
2070 Burcht 
# 4210 Burdinne 
6927 Bure 
# 4790 Burg-Reuland 
9420 Burst 
7602 Bury 
# 4750 Bütgenbach 
3891 Buvingen 
7133 Buvrinnes 
6743 Buzenol 
6230 Buzet 
7604 Callenelle 
7642 Calonne 
7940 Cambron-Casteau 
7870 Cambron-Saint-Vincent 
6850 Carlsbourg 
7141 Carnières 
7020 Casteau (Mons) 
7061 Casteau (Soignies) 
5650 Castillon 
7760 Celles (Ht.) 
4317 Celles (Lg.) 
5561 Celles (Nam.) 
4632 Cerexhe-Heuseux 
# 5630 Cerfontaine 
1341 Céroux-Mousty 
7063 Ch.-Notre-Dame-Louvignies 
4650 Chaineux 
5550 Chairière 
5020 Champion 
6971 Champlon 
6921 Chanly 
6742 Chantemelle 
7903 Chapelle-à-Oie 
7903 Chapelle-à-Wattines 
7160 Chapelle-lez-Herlaimont 
4537 Chapon-Seraing 
6000 Charleroi
4654 Charneux 
6824 Chassepierre 
1450 Chastre 
5650 Chastrès 
1450 Chastre-Villeroux-Blanmont 
6200 Châtelet 
6200 Châtelineau 
6747 Châtillon 
4050 Chaudfontaine 
1325 Chaumont-Gistoux 
4032 Chênée 
6673 Cherain 
4602 Cheratte 
7521 Chercq 
5590 Chevetogne 
4987 Chevron 
7950 Chièvres 
6460 Chimay 
6810 Chiny 
4400 Chokier 
5560 Ciergnon 
5590 Ciney 
4260 Ciplet 
7024 Ciply 
1480 Clabecq 
4560 Clavier 
4890 Clermont (Lg.) 
5650 Clermont (Nam.) 
4480 Clermont-sous-Huy 
5022 Cognelée 
7340 Colfontaine 
4170 Comblain-au-Pont 
4180 Comblain-Fairon 
4180 Comblain-la-Tour 
7780 Comines 
5590 Conneux 
1435 Corbais 
6838 Corbion 
7910 Cordes 
5620 Corenne 
4860 Cornesse 
5555 Cornimont 
5032 Corroy-le-Château 
1325 Corroy-le-Grand 
4257 Corswarem 
1450 Cortil-Noirmont 
5380 Cortil-Wodon 
6010 Couillet 
6180 Courcelles 
5336 Courrière 
6120 Cour-sur-Heure 
1490 Court-Saint-Etienne 
4218 Couthuin 
5300 Coutisse 
1380 Couture-Saint-Germain 
5660 Couvin 
4280 Cras-Avernas 
4280 Crehen 
4367 Crisnée 
7120 Croix-lez-Rouveroy 
4784 Crombach 
5332 Crupet 
# 7033 Cuesmes 
6880 Cugnon 
5660 Cul-des-Sarts 
5562 Custinne 
8890 Dadizele 
5660 Dailly 
9160 Daknam 
4607 Dalhem 
8340 Damme 
6767 Dampicourt 
6020 Dampremy 
4253 Darion 
5630 Daussois 
5020 Daussoulx 
5100 Dave 
6929 Daverdisse 
8420 De Haan 
9170 De Klinge 
8630 De Moeren 
8660 De Panne 
9840 De Pinte 
8540 Deerlijk 
9570 Deftinge 
9800 Deinze 
9280 Denderbelle 
9450 Denderhoutem 
9470 Denderleeuw 
9200 Dendermonde 
9400 Denderwindeke 
5537 Denée 
8720 Dentergem 
7912 Dergneau 
2480 Dessel 
8792 Desselgem 
9070 Destelbergen 
9831 Deurle 
2100 Deurne (Antwerpen) 
3290 Deurne (Bt.) 
7864 Deux-Acren 
5310 Dhuy 
1831 Diegem 
3590 Diepenbeek 
3290 Diest 
3700 Diets-Heur 
8900 Dikkebus 
9630 Dikkele 
9890 Dikkelvenne 
1700 Dilbeek 
3650 Dilsen 
5500 Dinant 
5570 Dion 
1325 Dion-Valmont 
4820 Dison 
6960 Dochamps 
9130 Doel 
6836 Dohan 
5680 Doische 
4140 Dolembreux 
4357 Donceel 
1370 Dongelberg 
3540 Donk 
6536 Donstiennes 
5530 Dorinne 
3440 Dormaal 
7711 Dottenijs 
7711 Dottignies 
7370 Dour 
5670 Dourbes 
8951 Dranouter 
5500 Dréhance 
8600 Driekapellen 
3350 Drieslinter 
1620 Drogenbos 
9031 Drongen 
8380 Dudzele 
2570 Duffel 
3080 Duisburg 
3803 Duras 
6940 Durbuy 
5530 Durnal 
1653 Dworp 
4690 Eben-Emael 
6860 Ebly 
7190 Ecaussinnes 
7190 Ecaussinnes-d'Enghien 
7191 Ecaussinnes-Lalaing 
2650 Edegem 
9700 Edelare 
9900 Eeklo 
8480 Eernegem 
8740 Egem 
8630 Eggewaartskapelle 
5310 Eghezée 
4480 Ehein (Engis) 
4120 Ehein (Neupré) 
3740 Eigenbilzen 
2430 Eindhout 
9700 Eine 
3630 Eisden 
9810 Eke 
2180 Ekeren (Antwerpen) 
9160 Eksaarde 
3941 Eksel 
3650 Elen 
9620 Elene 
1982 Elewijt 
3400 Eliksem 
1671 Elingen 
4590 Ellemelle 
7890 Ellezelles 
7910 Ellignies-lez-Frasnes 
7972 Ellignies-Sainte-Anne 
3670 Ellikom 
7370 Elouges 
9790 Elsegem 
4750 Elsenborn 
1050 Elsene 
9660 Elst 
8906 Elverdinge 
9140 Elversele 
2520 Emblem 
4053 Embourg 
8870 Emelgem 
5080 Emines 
5363 Emptinne 
9700 Ename 
3800 Engelmanshoven 
# 7850 Enghien 
4480 Engis 
1350 Enines 
4800 Ensival 
7134 Epinois 
1980 Eppegem 
5580 Eprave 
7050 Erbaut 
7050 Erbisoeul 
7500 Ere 
# 9320 Erembodegem 
6997 Erezée 
5644 Ermeton-sur-Biert 
5030 Ernage 
6972 Erneuville 
4920 Ernonheid 
9420 Erondegem 
9420 Erpe 
9420 Erpe-Mere 
5101 Erpent 
6441 Erpion 
3071 Erps-kwerps 
6560 Erquelinnes 
7387 Erquennes 
9940 Ertvelde 
9620 Erwetegem 
7760 Escanaffles 
8600 Esen 
4130 Esneux 
# 8587 Espierres 
# 8587 Espierres-Helchin 
7502 Esplechin 
7743 Esquelmes 
2910 Essen 
1790 Essene 
7730 Estaimbourg 
7730 Estaimpuis 
7120 Estinnes 
7120 Estinnes-au-Mont 
7120 Estinnes-au-Val 
6740 Etalle 
6760 Ethe 
9680 Etikhove 
8460 Ettelgem 
1040 Etterbeek 
7340 Eugies (Colfontaine) 
7080 Eugies (Frameries) 
# 4700 Eupen 
4631 Evegnée 
5350 Evelette 
9660 Everbeek 
3078 Everberg 
1140 Evere 
9940 Evergem 
7730 Evregnies 
5530 Evrehailles 
4731 Eynatten 
3400 Ezemaal 
5600 Fagnolle 
4317 Faimes 
5522 Falaën 
5060 Falisolle 
4260 Fallais 
5500 Falmagne 
5500 Falmignoul 
7181 Familleureux 
6240 Farciennes 
5340 Faulx-les-Tombes 
7120 Fauroeulx 
6637 Fauvillers 
4950 Faymonville 
6856 Fays-les-Veneurs 
7387 Fayt-le-Franc 
7170 Fayt-lez-Manage 
5570 Felenne 
7181 Feluy 
4607 Feneur 
5380 Fernelmont 
4190 Ferrières 
5570 Feschaux 
4347 Fexhe-le-Haut-Clocher 
4458 Fexhe-Slins 
4181 Filot 
5560 Finnevaux 
4530 Fize-Fontaine 
4367 Fize-le-Marsal 
6686 Flamierge 
5620 Flavion 
5020 Flawinne 
4400 Flémalle 
4400 Flémalle-Grande 
4400 Flémalle-Haute 
7012 Flénu 
4620 Fléron 
6220 Fleurus 
7880 Flobecq 
4540 Flône 
5334 Florée 
5150 Floreffe 
5620 Florennes 
6820 Florenville 
5150 Floriffoux 
5370 Flostoy 
5572 Focant 
1350 Folx-les-Caves 
6140 Fontaine-l'Evêque 
6567 Fontaine-Valmont 
5650 Fontenelle 
6820 Fontenoille 
7643 Fontenoy 
4340 Fooz 
6141 Forchies-la-Marche 
1190 Forest 
7910 Forest (Ht.) 
4870 Forêt 
6596 Forge-Philippe 
6464 Forges 
6953 Forrières 
5380 Forville 
4980 Fosse (Lg.) 
5070 Fosses-la-Ville 
7830 Fouleng 
6440 Fourbechies 
3798 Fouron-le-Comte 
3790 Fouron-Saint-Martin 
3792 Fouron-Saint-Pierre 
5504 Foy-Notre-Dame 
4870 Fraipont 
5650 Fraire 
4557 Fraiture 
7080 Frameries 
6853 Framont 
5600 Franchimont 
4970 Francorchamps 
5380 Franc-Waret 
5150 Franière 
5660 Frasnes (Nam.) 
7911 Frasnes-lez-Buissenal 
6210 Frasnes-lez-Gosselies 
4347 Freloux 
6800 Freux 
6440 Froidchapelle 
5576 Froidfontaine 
7504 Froidmont 
6990 Fronville 
7503 Froyennes 
4260 Fumal 
5500 Furfooz 
5641 Furnaux 
1750 Gaasbeek 
7943 Gages 
7906 Gallaix 
1083 Ganshoren 
7530 Gaurain-Ramecroix 
9890 Gavere 
5575 Gedinne 
2440 Geel 
4250 Geer 
1367 Geest-Gérompont-Pt-Rosière 
3450 Geetbets 
5024 Gelbressée 
3800 Gelinden 
3620 Gellik 
3200 Gelrode 
8980 Geluveld 
8940 Geluwe 
6929 Gembes 
5030 Gembloux 
4851 Gemmenich 
3600 Genk 
7040 Genly 
3770 Genoelselderen 
9050 Gentbrugge 
1450 Gentinnes 
1332 Genval 
3960 Gerdingen 
5524 Gerin 
1367 Gérompont 
6769 Gérouville 
6280 Gerpinnes 
2590 Gestel 
5340 Gesves 
7822 Ghislenghien 
7011 Ghlin 
7863 Ghoy 
7823 Gibecq 
2275 Gierle 
8691 Gijverinkhove 
# 9308 Gijzegem
8570 Gijzelbrechtegem 
9860 Gijzenzele 
6060 Gilly (Charleroi) 
5680 Gimnée 
3890 Gingelom 
8470 Gistel 
8830 Gits 
7041 Givry 
1473 Glabais 
3380 Glabbeek(Zuurbemde) 
4000 Glain 
4400 Gleixhe 
1315 Glimes 
4690 Glons 
5680 Gochenée 
7160 Godarville 
5530 Godinne 
9620 Godveerdegem 
4834 Goé 
9500 Goeferdinge 
7040 Goegnies-Chaussée 
5353 Goesnes 
3300 Goetsenhoven 
4140 Gomze-Andoumont 
7830 Gondregnies 
5660 Gonrieux 
9090 Gontrode 
1755 Gooik 
3803 Gorsem 
3840 Gors-Opleeuw 
6041 Gosselies 
3840 Gotem 
9800 Gottem 
7070 Gottignies 
6280 Gougnies 
5651 Gourdinne 
6030 Goutroux 
6670 Gouvy 
6181 Gouy-lez-Piéton 
6534 Gozée 
4460 Grâce-Berleur 
4460 Grâce-Hollogne 
5555 Graide 
9800 Grammene 
4300 Grand-Axhe 
7973 Grandglise 
4280 Grand-Hallet 
6698 Grand-Halleux 
6940 Grandhan 
5031 Grand-Leez 
5030 Grand-Manil 
6960 Grandmenil 
7900 Grandmetz 
4650 Grand-Rechain 
6560 Grand-Reng 
6470 Grandrieu 
1367 Grand-Rosière-Hottomont 
4360 Grandville 
6840 Grandvoir 
6840 Grapfontaine 
7830 Graty 
5640 Graux 
3450 Grazen 
9200 Grembergen 
1390 Grez-Doiceau 
1850 Grimbergen 
9506 Grimminge 
4030 Grivegnée (Liège) 
2280 Grobbendonk 
1702 Groot-Bijgaarden 
3800 Groot-Gelmen 
3840 Groot-Loon 
7950 Grosage 
5555 Gros-Fays 
3990 Grote-Brogel 
9620 Grotenberge 
3740 Grote-Spouwen 
3670 Gruitrode 
6952 Grune 
6927 Grupont 
7620 Guignies 
3723 Guigoven 
6704 Guirsch 
8560 Gullegem 
3870 Gutschoven 
3150 Haacht 
9450 Haaltert 
9120 Haasdonk 
3053 Haasrode 
6720 Habay 
6720 Habay-la-Neuve 
6723 Habay-la-Vieille 
6782 Habergy 
4684 Haccourt 
6720 Hachy 
7911 Hacquegnies 
5351 Haillot 
7100 Haine-Saint-Paul 
7100 Haine-Saint-Pierre 
7350 Hainin 
3300 Hakendover 
6792 Halanzy 
3545 Halen 
2220 Hallaar 
2980 Halle (Kempen) 
3440 Halle-Booienhoven 
6986 Halleux 
6922 Halma 
3800 Halmaal 
5340 Haltinne 
3945 Ham 
6840 Hamipré 
1785 Hamme (Bt.) 
9220 Hamme (O.-Vl.) 
1320 Hamme-Mille 
4180 Hamoir 
5360 Hamois 
3930 Hamont 
3930 Hamont-Achel 
6990 Hampteau 
6120 Ham-sur-Heure 
6120 Ham-sur-Heure/Nalinnes 
5190 Ham-sur-Sambre 
8610 Handzame 
4357 Haneffe 
4210 Hannêche 
5310 Hanret 
9850 Hansbeke 
5580 Han-sur-Lesse 
6560 Hantes-Wihéries 
5621 Hanzinelle 
5621 Hanzinne 
7321 Harchies 
8530 Harelbeke 
3840 Haren (Borgloon) 
3700 Haren (Tongeren) 
6900 Hargimont 
7022 Harmignies 
6767 Harnoncourt 
6960 Harre 
6950 Harsin 
7022 Harveng 
4920 Harzé 
3500 Hasselt 
5540 Hastière 
5540 Hastière-Lavaux 
5541 Hastière-par-Delà 
6870 Hatrival 
7120 Haulchin 
4730 Hauset 
6929 Haut-Fays 
1461 Haut-Ittre 
5537 Haut-le-Wastia 
7334 Hautrage 
7041 Havay 
5370 Havelange 
5590 Haversin 
7531 Havinnes 
7021 Havré 
3940 Hechtel 
5543 Heer 
3870 Heers 
3740 Hees 
8551 Heestert 
2801 Heffen 
1670 Heikruis 
2830 Heindonk 
6700 Heinsch 
8301 Heist-aan-Zee 
2220 Heist-Op-Den-Berg 
1790 Hekelgem 
3870 Heks 
# 8587 Helchin 
3530 Helchteren 
9450 Heldergem 
1357 Hélécine 
3440 Helen-Bos 
# 8587 Helkijn 
7830 Hellebecq 
9571 Hemelveerdegem 
2620 Hemiksem 
5380 Hemptinne (Fernelmont) 
5620 Hemptinne-lez-Florennes 
3840 Hendrieken 
3700 Henis 
7090 Hennuyères 
4841 Henri-Chapelle 
7090 Henripont 
7350 Hensies 
3971 Heppen 
4771 Heppenbach 
6220 Heppignies 
6887 Herbeumont 
7050 Herchies 
3770 Herderen 
# 9310 Herdersem
3020 Herent 
2200 Herentals 
2270 Herenthout 
1540 Herfelingen 
4728 Hergenrath 
7742 Hérinnes-lez-Pecq 
4681 Hermalle-sous-Argenteau 
4480 Hermalle-sous-Huy 
4680 Hermée 
5540 Hermeton-sur-Meuse 
1540 Herne 
4217 Héron 
7911 Herquegies 
7712 Herseaux 
2230 Herselt 
4040 Herstal 
3717 Herstappe 
7522 Hertain 
3831 Herten 
8020 Hertsberge 
4650 Herve 
9550 Herzele 
8501 Heule 
5377 Heure (Nam.) 
4682 Heure-le-Romain 
9700 Heurne 
3550 Heusden (Limb.) 
9070 Heusden (O.-Vl.) 
3550 Heusden-Zolder 
4802 Heusy 
3191 Hever 
3001 Heverlee 
1435 Hévillers 
6941 Heyd 
9550 Hillegem 
2880 Hingene 
5380 Hingeon 
6984 Hives 
2660 Hoboken (Antwerpen) 
4351 Hodeige 
6987 Hodister 
4162 Hody 
3320 Hoegaarden 
1560 Hoeilaart 
8340 Hoeke 
3746 Hoelbeek 
3471 Hoeleden 
3840 Hoepertingen 
3730 Hoeselt 
2940 Hoevenen 
1981 Hofstade (Bt.) 
# 9308 Hofstade (O.-Vl.) 
5377 Hogne 
4342 Hognoul 
7620 Hollain 
6637 Hollange 
8902 Hollebeke 
4460 Hollogne-aux-Pierres 
4250 Hollogne-sur-Geer 
3220 Holsbeek 
2811 Hombeek 
4852 Hombourg 
6640 Hompré 
6780 Hondelange 
5570 Honnay 
7387 Honnelles 
8830 Hooglede 
8690 Hoogstade 
2320 Hoogstraten 
9667 Horebeke 
4460 Horion-Hozémont 
7301 Hornu 
3870 Horpmaal 
7060 Horrues 
6990 Hotton 
6724 Houdemont 
7110 Houdeng-Aimeries 
7110 Houdeng-Goegnies 
5575 Houdremont 
6660 Houffalize 
5563 Hour 
4671 Housse 
7812 Houtaing 
1476 Houtain-le-Val 
4682 Houtain-Saint-Siméon 
8377 Houtave 
8630 Houtem (W.-Vl.) 
3530 Houthalen 
3530 Houthalen-Helchteren 
7781 Houthem (Comines) 
8650 Houthulst 
2235 Houtvenne 
3390 Houwaart 
5530 Houx 
5560 Houyet 
2540 Hove 
7830 Hoves (Ht.) 
7624 Howardries 
4520 Huccorgne 
9750 Huise 
7950 Huissignies 
1654 Huizingen 
3040 Huldenberg 
2235 Hulshout 
5560 Hulsonniaux 
8531 Hulste 
6900 Humain 
1851 Humbeek 
9630 Hundelgem 
1367 Huppaye 
7022 Hyon 
8480 Ichtegem 
9472 Iddergem 
9506 Idegem 
9340 Impe 
1315 Incourt 
8770 Ingelmunster 
8570 Ingooigem 
7801 Irchonwelz 
7822 Isières 
5032 Isnes 
2222 Itegem 
1701 Itterbeek 
1460 Ittre 
4400 Ivoz-Ramet 
1050 Ixelles 
8870 Izegem 
6810 Izel 
8691 Izenberge 
6941 Izier 
8490 Jabbeke 
4845 Jalhay 
5354 Jallet 
5600 Jamagne 
5100 Jambes (Namur) 
5600 Jamiolle 
6120 Jamioulx 
6810 Jamoigne 
1350 Jandrain-Jandrenouille 
1350 Jauche 
1370 Jauchelette 
5570 Javingue 
4540 Jehay 
6880 Jehonville 
7012 Jemappes 
5580 Jemelle 
4101 Jemeppe-sur-Meuse 
5190 Jemeppe-sur-Sambre 
4357 Jeneffe (Lg.) 
5370 Jeneffe (Nam.) 
3840 Jesseren 
1090 Jette 
3890 Jeuk 
1370 Jodoigne 
1370 Jodoigne-Souveraine 
7620 Jollain-Merlin 
6280 Joncret 
4650 Julémont 
6040 Jumet (Charleroi) 
4020 Jupille-sur-Meuse 
4450 Juprelle 
7050 Jurbise 
6642 Juseret 
8600 Kaaskerke 
8870 Kachtem 
3293 Kaggevinne 
7540 Kain (Tournai) 
9270 Kalken 
9120 Kallo (Beveren-Waas) 
9130 Kallo (Kieldrecht) 
2920 Kalmthout 
1910 Kampenhout 
8700 Kanegem 
3770 Kanne 
2950 Kapellen (Antw.) 
3381 Kapellen (Bt.) 
1880 Kapelle-op-den-Bos 
9970 Kaprijke 
8572 Kaster 
2460 Kasterlee 
3950 Kaulille 
3140 Keerbergen 
8600 Keiem 
# 4720 Kelmis 
4367 Kemexhe 
8956 Kemmel 
9190 Kemzeke 
8581 Kerkhove 
3370 Kerkom 
3800 Kerkom-bij-Sint-Truiden 
9451 Kerksken 
3510 Kermt 
3840 Kerniel 
3472 Kersbeek-Miskom 
2560 Kessel 
3010 Kessel-Lo 
3640 Kessenich 
1755 Kester 
# 4701 Kettenis 
5060 Keumiée 
9130 Kieldrecht (Beveren) 
3640 Kinrooi 
3990 Kleine-Brogel 
3740 Kleine-Spouwen 
3870 Klein-Gelmen 
8420 Klemskerke 
8650 Klerken 
9690 Kluisbergen 
9940 Kluizen 
9910 Knesselare 
8300 Knokke 
8300 Knokke-Heist 
1730 Kobbegem 
8680 Koekelare 
1081 Koekelberg 
3582 Koersel 
3840 Kolmont (Borgloon) 
3700 Kolmont (Tongeren) 
7780 Komen 
7780 Komen-Waasten 
2500 Koningshooikt 
3700 Koninksem 
2550 Kontich 
8510 Kooigem 
8000 Koolkerke 
8851 Koolskamp 
3060 Korbeek-Dijle 
3360 Korbeek-Lo 
8610 Kortemark 
3470 Kortenaken 
3070 Kortenberg 
3720 Kortessem 
3890 Kortijs 
3220 Kortrijk-Dutsel 
3850 Kozen 
1950 Kraainem 
8972 Krombeke 
9150 Kruibeke 
9770 Kruishoutem 
3300 Kumtich 
3511 Kuringen 
3840 Kuttekoven 
8520 Kuurne 
3945 Kwaadmechelen 
9690 Kwaremont 
7080 La Bouverie 
# 4720 La Calamine 
7611 La Glanerie 
4987 La Gleize 
7170 La Hestre 
7100 La Louvière 
# 4910 La Reid
6980 La Roche-en-Ardenne 
3400 Laar 
9270 Laarne 
6567 Labuissière 
6821 Lacuisine 
7950 Ladeuze 
1020 Laeken 
5550 Laforêt 
7890 Lahamaide 
7522 Lamain 
4800 Lambermont 
6220 Lambusart 
4350 Lamine 
4210 Lamontzée 
6767 Lamorteau 
8600 Lampernisse 
3620 Lanaken 
4600 Lanaye 
9850 Landegem 
6111 Landelies 
3400 Landen 
5300 Landenne 
9860 Landskouter 
5651 Laneffe 
3201 Langdorp 
8920 Langemark 
8920 Langemark-Poelkapelle 
3650 Lanklaar 
7800 Lanquesaint 
4450 Lantin 
4300 Lantremange 
7622 Laplaigne 
8340 Lapscheure 
1380 Lasne 
1380 Lasne-Chapelle-St-Lambert 
1370 Lathuy 
4261 Latinne 
6761 Latour 
3700 Lauw 
8930 Lauwe 
6681 Lavacherie 
5580 Lavaux-Sainte-Anne 
4217 Lavoir 
5670 Le Mesnil 
7070 Le Roeulx 
5070 Le Roux 
9280 Lebbeke 
1320 L'Ecluse 
9340 Lede 
9050 Ledeberg (Gent) 
8880 Ledegem 
3061 Leefdaal 
1755 Leerbeek 
6142 Leernes 
6530 Leers-et-Fosteau 
7730 Leers-Nord 
2811 Leest 
9620 Leeuwergem 
8432 Leffinge 
6860 Léglise 
5590 Leignon 
8691 Leisele 
8600 Leke 
1502 Lembeek 
9971 Lembeke 
9820 Lemberge 
8860 Lendelede 
1750 Lennik 
7870 Lens 
4280 Lens-Saint-Remy 
4250 Lens-Saint-Servais 
4360 Lens-sur-Geer 
3970 Leopoldsburg 
4560 Les Avins 
6811 Les Bulles 
6830 Les Hayons 
4317 Les Waleffes 
6464 L'Escaillère 
7621 Lesdain 
5580 Lessive 
6953 Lesterny 
5170 Lesve 
7850 Lettelingen 
9521 Letterhoutem 
6500 Leugnies 
9700 Leupegem 
3630 Leut 
5310 Leuze (Nam.) 
7900 Leuze-en-Hainaut 
6500 Leval-Chaudeville 
7134 Leval-Trahegnies 
6238 Liberchies 
6890 Libin 
6800 Libramont-Chevigny 
2460 Lichtaart 
8810 Lichtervelde 
1770 Liedekerke 
9400 Lieferinge 
# 4000 Liège 1
# 4020 Liège 2 
2500 Lier 
9570 Lierde 
4990 Lierneux 
5310 Liernu 
4042 Liers 
2870 Liezele 
7812 Ligne 
4254 Ligney 
5140 Ligny 
2275 Lille 
2040 Lillo 
1428 Lillois-Witterzée 
1300 Limal 
4830 Limbourg 
1342 Limelette 
6670 Limerlé 
4357 Limont 
3210 Linden 
1630 Linkebeek 
3560 Linkhout 
1357 Linsmeau 
2547 Lint 
3350 Linter 
2890 Lippelo 
5501 Lisogne 
8380 Lissewege 
5101 Lives-sur-Meuse 
4600 Lixhe 
8647 Lo 
6540 Lobbes 
9080 Lochristi 
6042 Lodelinsart 
2990 Loenhout 
8958 Loker 
9160 Lokeren 
3545 Loksbergen 
8434 Lombardsijde 
7870 Lombise 
3920 Lommel 
4783 Lommersweiler 
6463 Lompret 
6924 Lomprez 
4431 Loncin 
1840 Londerzeel 
6688 Longchamps (Lux.) 
5310 Longchamps (Nam.) 
6840 Longlier 
1325 Longueville 
6600 Longvilly 
4710 Lontzen 
5030 Lonzée 
3040 Loonbeek 
8210 Loppem 
4987 Lorcé 
8647 Lo-Reninge 
1651 Lot 
9880 Lotenhulle 
5575 Louette-Saint-Denis 
5575 Louette-Saint-Pierre 
1471 Loupoigne 
4920 Louveigné (Aywaille) 
4141 Louveigné (Sprimont) 
9920 Lovendegem 
3360 Lovenjoel 
6280 Loverval 
5101 Loyers 
3210 Lubbeek 
7700 Luingne 
3560 Lummen 
5170 Lustin 
6238 Luttre 
9680 Maarkedal 
9680 Maarke-Kerkem 
3680 Maaseik 
3630 Maasmechelen 
6663 Mabompré 
1830 Machelen (Bt) 
9870 Machelen (O.-Vl.) 
6591 Macon 
6593 Macquenoise 
5374 Maffe 
7810 Maffle 
4623 Magnée 
5330 Maillen 
7812 Mainvault 
7020 Maisières 
6852 Maissin 
5300 Maizeret 
3700 Mal 
9990 Maldegem 
1840 Malderen 
6960 Malempré 
1360 Malèves-Ste-Marie-Wastines 
2390 Malle 
4960 Malmédy 
5020 Malonne 
5575 Malvoisin 
7170 Manage 
4760 Manderfeld 
6960 Manhay 
8433 Mannekensvere 
1380 Maransart 
1495 Marbais (Bt.) 
6120 Marbaix (Ht.) 
6900 Marche-en-Famenne 
5024 Marche-les-Dames 
7190 Marche-lez-Ecaussinnes 
6030 Marchienne-au-Pont 
4570 Marchin 
7387 Marchipont 
5380 Marchovelette 
6001 Marcinelle 
6987 Marcourt 
7850 Marcq 
6990 Marenne 
9030 Mariakerke (Gent) 
2880 Mariekerke (Bornem) 
5660 Mariembourg 
1350 Marilles 
7850 Mark 
8510 Marke (Kortrijk) 
8720 Markegem 
4210 Marneffe 
7522 Marquain 
6630 Martelange 
3742 Martenslinde 
5573 Martouzin-Neuville 
6953 Masbourg 
7020 Masnuy-Saint-Jean (Mons) 
7050 Masnuy-Saint-Pierre 
7050 Masnuy-St-Jean (Jurbise) 
9230 Massemen 
2240 Massenhoven 
5680 Matagne-la-Grande 
5680 Matagne-la-Petite 
9700 Mater 
7640 Maubray 
7534 Maulde 
7110 Maurage 
5670 Mazée 
1745 Mazenzele 
5032 Mazy 
5372 Méan 
3630 Mechelen-aan-de-Maas 
3870 Mechelen-Bovelingen 
4219 Meeffe 
3391 Meensel-Kiezegem 
2321 Meer 
3078 Meerbeek 
9402 Meerbeke 
9170 Meerdonk 
2450 Meerhout 
2328 Meerle 
3630 Meeswijk 
8377 Meetkerke 
3670 Meeuwen 
3670 Meeuwen-Gruitrode 
5310 Mehaigne 
9800 Meigem 
9630 Meilegem 
1860 Meise 
6769 Meix-devant-Virton 
6747 Meix-le-Tige 
9700 Melden 
3320 Meldert (Bt.) 
3560 Meldert (Limb.) 
# 9310 Meldert (O.-Vl.) 
4633 Melen 
1370 Mélin 
3350 Melkwezer 
9090 Melle 
1495 Mellery 
7540 Melles 
6211 Mellet 
6860 Mellier 
1820 Melsbroek 
9120 Melsele 
9820 Melsen 
4837 Membach 
5550 Membre 
3770 Membruggen 
9042 Mendonk 
6567 Merbes-le-Château 
6567 Merbes-Sainte-Marie 
1785 Merchtem 
4280 Merdorp 
9420 Mere 
9820 Merelbeke 
9850 Merendree 
8650 Merkem 
2170 Merksem (Antwerpen) 
2330 Merksplas 
5600 Merlemont 
8957 Mesen 
7822 Meslin-l'Evêque 
5560 Mesnil-Eglise 
5560 Mesnil-Saint-Blaise 
9200 Mespelare 
6780 Messancy 
3272 Messelbroek 
8957 Messines 
7022 Mesvin 
3870 Mettekoven 
5640 Mettet 
8760 Meulebeke 
5081 Meux 
7942 Mévergnies-lez-Lens 
4770 Meyrode 
9660 Michelbeke 
4630 Micheroux 
9992 Middelburg 
8430 Middelkerke 
5376 Miécret 
3891 Mielen-boven-Aalst 
7070 Mignault 
3770 Millen 
4041 Milmort 
2322 Minderhout 
6870 Mirwart 
4577 Modave 
3790 Moelingen 
8552 Moen 
9500 Moerbeke 
9180 Moerbeke-Waas 
8470 Moere 
8340 Moerkerke 
9220 Moerzeke 
4520 Moha 
5361 Mohiville 
5060 Moignelée 
6800 Moircy 
2400 Mol 
7760 Molenbaix 
1080 Molenbeek-Saint-Jean 
3461 Molenbeek-Wersbeek 
3640 Molenbeersel 
3294 Molenstede 
1730 Mollem 
4350 Momalle 
6590 Momignies 
5555 Monceau-en-Ardenne 
6592 Monceau-Imbrechies 
6031 Monceau-sur-Sambre 
4400 Mons-lez-Liège 
1400 Monstreux 
6661 Mont (Lux.) 
5530 Mont (Nam.) 
6470 Montbliart 
7750 Mont-de-l'Enclus 
4420 Montegnée 
3890 Montenaken 
5580 Mont-Gauthier 
7870 Montignies-lez-Lens 
6560 Montignies-St-Christophe 
7387 Montignies-sur-Roc 
6061 Montignies-sur-Sambre 
6110 Montigny-le-Tilleul 
6674 Montleban 
7911 Montroeul-au-Bois 
7350 Montroeul-sur-Haine 
1367 Mont-Saint-André 
7542 Mont-Saint-Aubert 
7141 Mont-Sainte-Aldegonde 
6540 Mont-Sainte-Geneviève 
1435 Mont-Saint-Guibert 
6032 Mont-sur-Marchienne 
4850 Montzen 
# 9310 Moorsel 
8560 Moorsele 
8890 Moorslede 
9860 Moortsele 
3740 Mopertingen 
9790 Moregem 
4850 Moresnet 
6640 Morhet 
5621 Morialmé 
2200 Morkhoven 
7140 Morlanwelz 
7140 Morlanwelz-Mariemont 
6997 Mormont 
5190 Mornimont 
# 4670 Mortier 
4607 Mortroux 
2640 Mortsel 
5620 Morville 
3790 Mouland 
7812 Moulbaix 
7543 Mourcourt 
7700 Mouscron 
7911 Moustier (Ht.) 
5190 Moustier-sur-Sambre 
5550 Mouzaive 
4280 Moxhe 
5340 Mozet 
3891 Muizen (Limb.) 
2812 Muizen (Mechelen) 
9700 Mullem 
9630 Munkzwalm 
6820 Muno 
3740 Munsterbilzen 
9820 Munte 
6750 Musson 
6750 Mussy-la-Ville 
4190 My 
7062 Naast 
6660 Nadrin 
5550 Nafraiture 
6120 Nalinnes 
5300 Namêche 
# 5000 Namur
4550 Nandrin 
5100 Naninne 
5555 Naomé 
6950 Nassogne 
5360 Natoye 
9810 Nazareth 
7730 Néchin 
1120 Neder-over-Heembeek 
9500 Nederboelare 
9660 Nederbrakel 
9700 Nederename 
9400 Nederhasselt 
1910 Nederokkerzeel 
9636 Nederzwalm-Hermelgem 
3670 Neerglabbeek 
3620 Neerharen 
3350 Neerhespen 
1357 Neerheylissem 
3040 Neerijse 
3404 Neerlanden 
3350 Neerlinter 
3680 Neeroeteren 
3910 Neerpelt 
3700 Neerrepen 
3370 Neervelp 
7784 Neerwaasten 
3400 Neerwinden 
9403 Neigem 
3700 Nerem 
4870 Nessonvaux 
1390 Nethen 
5377 Nettinne 
6840 Neufchâteau 
4608 Neufchâteau (Lg.) 
7332 Neufmaison 
7063 Neufvilles 
4721 Neu-Moresnet 
4120 Neupré 
5600 Neuville (Philippeville) 
4121 Neuville-en-Condroz 
9850 Nevele 
2845 Niel 
3668 Niel-bij-As 
3890 Niel-bij-Sint-Truiden 
9506 Nieuwenhove 
1880 Nieuwenrode 
# 9320 Nieuwerkerken (Aalst) 
3850 Nieuwerkerken (Limb.) 
8600 Nieuwkapelle 
8950 Nieuwkerke 
9100 Nieuwkerken-Waas 
8377 Nieuwmunster 
3221 Nieuwrode 
2560 Nijlen 
1457 Nil-St-Vincent-St-Martin 
7020 Nimy (Mons) 
9400 Ninove 
5670 Nismes 
5680 Niverlée 
6640 Nives 
6717 Nobressart 
1320 Nodebais 
1350 Noduwez 
7080 Noirchain 
6831 Noirefontaine 
5377 Noiseux 
9771 Nokere 
6851 Nollevaux 
2200 Noorderwijk 
8647 Noordschote 
1930 Nossegem 
6717 Nothomb 
7022 Nouvelles 
4347 Noville (Lg.) 
6600 Noville (Lux.) 
5380 Noville-les-Bois 
5310 Noville-sur-Méhaigne 
9681 Nukerke 
6230 Obaix 
7743 Obigies 
7034 Obourg 
6890 Ochamps 
4560 Ocquier 
6960 Odeigne 
4367 Odeur 
8730 Oedelem 
8800 Oekene 
2520 Oelegem 
8690 Oeren 
8720 Oeselgem 
1755 Oetingen 
7911 Oeudeghien 
2260 Oevel 
6850 Offagne 
7862 Ogy 
1380 Ohain 
5350 Ohey 
5670 Oignies-en-Thiérache 
1480 Oisquercq 
5555 Oizy 
9400 Okegem 
2250 Olen 
4300 Oleye 
7866 Ollignies 
5670 Olloy-sur-Viroin 
2491 Olmen 
4877 Olne 
9870 Olsene 
4252 Omal 
4540 Ombret 
5600 Omezée 
6900 On 
5520 Onhaye 
9500 Onkerzele 
7387 Onnezies 
5190 Onoz 
1760 Onze-Lieve-Vrouw-Lombeek 
2861 Onze-Lieve-Vrouw-Waver 
8710 Ooigem 
9700 Ooike (Oudenaarde) 
9790 Ooike (Wortegem-Petegem) 
9520 Oomb.(St-Lievens-Houtem) 
9620 Oombergen (Zottegem) 
3300 Oorbeek 
9340 Oordegem 
9041 Oostakker 
8670 Oostduinkerke 
9968 Oosteeklo 
# 8400 Oostende 
9860 Oosterzele 
3945 Oostham 
8020 Oostkamp 
8340 Oostkerke (Damme) 
8600 Oostkerke (Diksmuide) 
2390 Oostmalle 
8840 Oostnieuwkerke 
8780 Oostrozebeke 
8640 Oostvleteren 
9931 Oostwinkel 
9660 Opbrakel 
9255 Opdorp 
3660 Opglabbeek 
3630 Opgrimbie 
1421 Ophain-Bois-Seigneur-Isaac 
9500 Ophasselt 
3870 Opheers 
1357 Opheylissem 
3640 Ophoven 
3960 Opitter 
3300 Oplinter 
3680 Opoeteren 
6852 Opont 
1315 Opprebais 
2890 Oppuurs 
3360 Opvelp 
1745 Opwijk 
1360 Orbais 
5550 Orchimont 
7501 Orcq 
3800 Ordingen 
5640 Oret 
6880 Orgeo 
7802 Ormeignies 
1350 Orp-Jauche 
1350 Orp-le-Grand 
7750 Orroir 
3350 Orsmaal-Gussenhoven 
6983 Ortho 
7804 Ostiches 
8553 Otegem 
4210 Oteppe 
4340 Othée 
4360 Otrange 
3040 Ottenburg 
9420 Ottergem 
# 1340 Ottignies 
9200 Oudegem 
8600 Oudekapelle 
9700 Oudenaarde 
1600 Oudenaken 
8460 Oudenburg 
1160 Oudergem 
3050 Oud-Heverlee 
2360 Oud-Turnhout 
4590 Ouffet 
4102 Ougrée 
4680 Oupeye 
9406 Outer 
3321 Outgaarden 
4577 Outrelouxhe 
8582 Outrijve 
9750 Ouwegem 
9500 Overboelare 
3350 Overhespen 
3090 Overijse 
9290 Overmere 
3900 Overpelt 
3700 Overrepen 
3400 Overwinden 
3583 Paal 
4452 Paifve 
4560 Pailhe 
6850 Paliseul 
1760 Pamel 
7861 Papignies 
9661 Parike 
8980 Passendale 
5575 Patignies 
7340 Pâturages 
9630 Paulatem 
7740 Pecq 
3990 Peer 
7120 Peissant 
4287 Pellaines 
3212 Pellenberg 
1670 Pepingen 
4860 Pepinster 
1820 Perk 
7640 Péronnes-lez-Antoing 
7134 Péronnes-lez-Binche 
7600 Péruwelz 
8600 Pervijze 
5352 Perwez-Haillot 
5660 Pesche 
5590 Pessoux 
9800 Petegem-aan-de-Leie 
9790 Petegem-aan-de-Schelde 
5660 Petigny 
5660 Petite-Chapelle 
7850 Petit-Enghien 
5555 Petit-Fays 
4280 Petit-Hallet 
4800 Petit-Rechain 
7090 Petit-Roeulx-lez-Braine 
7181 Petit-Roeulx-lez-Nivelles 
6692 Petit-Thier 
1800 Peutie 
5600 Philippeville 
7160 Piéton 
1370 Piétrain 
1315 Piètrebais 
7904 Pipaix 
3700 Piringen 
6240 Pironchamps 
8740 Pittem 
4122 Plainevaux 
1380 Plancenoit 
7782 Ploegsteert 
4850 Plombières 
2275 Poederlee 
9880 Poeke 
8920 Poelkapelle 
9850 Poesele 
9401 Pollare 
4910 Polleur (Theux) 
4800 Polleur (Verviers) 
8647 Pollinkhove 
7322 Pommeroeul 
5574 Pondrôme 
6230 Pont-à-Celles 
6250 Pont-de-Loup 
5380 Pontillas 
8970 Poperinge 
2382 Poppel 
7760 Popuelles 
6929 Porcheresse (Lux.) 
5370 Porcheresse (Nam.) 
7760 Pottes 
4280 Poucet 
4171 Poulseur 
6830 Poupehan 
4350 Pousset 
5660 Presgaux 
6250 Presles 
5170 Profondeville 
8972 Proven 
5650 Pry 
2242 Pulderbos 
2243 Pulle 
5530 Purnode 
5550 Pussemange 
2580 Putte 
2870 Puurs 
7390 Quaregnon 
7540 Quartes 
1430 Quenast 
4610 Queue-du-Bois 
7972 Quevaucamps 
7040 Quévy-le-Grand 
7040 Quévy-le-Petit 
7380 Quiévrain 
6792 Rachecourt 
4287 Racour 
# 4730 Raeren 
6532 Ragnies 
4987 Rahier 
7971 Ramegnies 
7520 Ramegnies-Chin 
4557 Ramelot 
1367 Ramillies 
1880 Ramsdonk 
2230 Ramsel 
8301 Ramskapelle (Knokke-Heist) 
8620 Ramskapelle (Nieuwpoort) 
6470 Rance 
6043 Ransart 
3470 Ransberg 
2520 Ranst 
2380 Ravels 
7804 Rebaix 
1430 Rebecq 
1430 Rebecq-Rognon 
# 4780 Recht
6800 Recogne 
6890 Redu 
2840 Reet 
3621 Rekem 
8930 Rekkem 
1731 Relegem 
6800 Remagne 
3791 Remersdaal 
4350 Remicourt 
9600 Renaix 
6987 Rendeux 
8647 Reninge 
8970 Reningelst 
6500 Renlies 
3950 Reppel 
7134 Ressaix 
9551 Ressegem 
6927 Resteigne 
2470 Retie 
4621 Retinne 
# 4790 Reuland 
6210 Rèves 
5080 Rhisnes 
1640 Rhode-Saint-Genèse 
4600 Richelle 
3770 Riemst 
5575 Rienne 
6464 Rièzes 
3840 Rijkel 
2310 Rijkevorsel 
3740 Rijkhoven 
2820 Rijmenam 
3700 Riksingen 
3202 Rillaar 
5170 Rivière 
1330 Rixensart 
6460 Robechies 
6769 Robelmont 
4950 Robertville 
9630 Roborst 
5580 Rochefort 
6830 Rochehaut 
4761 Rocherath 
4690 Roclenge-sur-Geer 
4000 Rocourt 
8972 Roesbrugge-Haringe 
8800 Roeselare 
5651 Rognée 
7387 Roisin 
8460 Roksem 
8510 Rollegem 
8880 Rollegem-Kapelle 
4347 Roloux 
5600 Roly 
5600 Romedenne 
5680 Romerée 
3730 Romershoven 
4624 Romsée 
7623 Rongy 
7090 Ronquières 
9600 Ronse 
9932 Ronsele 
3370 Roosbeek 
1760 Roosdaal 
5620 Rosée 
6250 Roselies 
1331 Rosières 
3740 Rosmeer 
4257 Rosoux-Crenwick 
6730 Rossignol 
3650 Rotem 
4120 Rotheux-Rimière 
3110 Rotselaar 
7601 Roucourt 
7120 Rouveroy (Ht.) 
4140 Rouvreux 
6767 Rouvroy 
6044 Roux 
1315 Roux-Miroir 
6900 Roy 
9630 Rozebeke 
8020 Ruddervoorde 
6760 Ruette 
9690 Ruien 
2870 Ruisbroek (Antw.) 
1601 Ruisbroek (Bt.) 
8755 Ruiselede 
3870 Rukkelingen-Loon 
6724 Rulles 
8800 Rumbeke 
7610 Rumes 
7540 Rumillies 
3454 Rummen 
3400 Rumsdorp 
2840 Rumst 
3803 Runkelen 
9150 Rupelmonde 
7750 Russeignies 
3700 Rutten 
3798 's Gravenvoeren 
2970 's Gravenwezel 
3700 's Herenelderen 
6221 Saint-Amand 
4606 Saint-André 
5620 Saint-Aubin 
7034 Saint-Denis (Ht.) 
5081 Saint-Denis-Bovesse 
6820 Sainte-Cécile 
6800 Sainte-Marie-Chevigny 
6740 Sainte-Marie-sur-Semois 
6680 Sainte-Ode 
1480 Saintes 
4470 Saint-Georges-sur-Meuse 
5640 Saint-Gérard 
5310 Saint-Germain 
1450 Saint-Géry 
7330 Saint-Ghislain 
1060 Saint-Gilles 
6870 Saint-Hubert 
1370 Saint-Jean-Geest 
1210 Saint-Josse-ten-Noode 
7730 Saint-Léger (Ht.) 
6747 Saint-Léger (Lux.) 
5003 Saint-Marc 
6762 Saint-Mard 
5190 Saint-Martin 
7500 Saint-Maur 
6887 Saint-Médard 
4420 Saint-Nicolas (Lg.) 
6800 Saint-Pierre 
6460 Saint-Remy (Ht.) 
4672 Saint-Remy (Lg.) 
1370 Saint-Remy-Geest 
7912 Saint-Sauveur 
5002 Saint-Servais 
4550 Saint-Séverin 
7030 Saint-Symphorien 
7100 Saint-Vaast 
6730 Saint-Vincent 
# 4780 Saint-Vith 
4671 Saive 
6460 Salles 
5600 Samart 
5060 Sambreville 
6982 Samrée 
# 4780 Sankt Vith 
7080 Sars-la-Bruyère 
6542 Sars-la-Buissière 
5330 Sart-Bernard 
5575 Sart-Custinne 
1495 Sart-Dames-Avelines 
5600 Sart-en-Fagne 
5070 Sart-Eustache 
4845 Sart-lez-Spa 
5070 Sart-Saint-Laurent 
6470 Sautin 
5600 Sautour 
5030 Sauvenière 
1030 Schaarbeek 
1030 Schaerbeek 
3290 Schaffen 
3732 Schalkhoven 
5364 Schaltin 
9820 Schelderode 
9860 Scheldewindeke 
2627 Schelle 
9260 Schellebelle 
9506 Schendelbeke 
1703 Schepdaal 
2970 Schilde 
4782 Schoenberg 
4782 Schönberg 
9200 Schoonaarde 
8433 Schore 
9688 Schorisse 
2900 Schoten 
2223 Schriek 
8700 Schuiferskapelle 
3540 Schulen 
5300 Sclayn 
5361 Scy 
5300 Seilles 
6781 Sélange 
6596 Seloignes 
9890 Semmerzake 
7180 Seneffe 
6832 Sensenruth 
4557 Seny 
5630 Senzeille 
6940 Septon 
4100 Seraing 
4537 Seraing-le-Château 
5590 Serinchamps 
9260 Serskamp 
5521 Serville 
6640 Sibret 
6750 Signeulx 
8340 Sijsele 
5630 Silenrieux 
7830 Silly 
9112 Sinaai-Waas 
5377 Sinsin 
1080 Sint-Agatha-Berchem 
3040 Sint-Agatha-Rode 
2890 Sint-Amands 
9040 Sint-Amandsberg 
8200 Sint-Andries 
9550 Sint-Antelinks 
8710 Sint-Baafs-Vijve 
9630 Sint-Blasius-Boekel 
8554 Sint-Denijs 
9630 Sint-Denijs-Boekel 
9051 Sint-Denijs-Westrem 
8793 Sint-Eloois-Vijve 
8880 Sint-Eloois-Winkel 
1640 Sint-Genesius-Rode 
1060 Sint-Gillis 
9170 Sint-Gillis-Waas 
9620 Sint-Goriks-Oudenhove 
3730 Sint-Huibrechts-Hern 
3910 Sint-Huibrechts-Lille 
8600 Sint-Jacobs-Kapelle 
8900 Sint-Jan 
9982 Sint-Jan-in-Eremo 
1080 Sint-Jans-Molenbeek 
2960 Sint-Job-in-'t-Goor 
1210 Sint-Joost-ten-Node 
8730 Sint-Joris (Beernem) 
8620 Sint-Joris (Nieuwpoort) 
3051 Sint-Joris-Weert 
3390 Sint-Joris-Winge 
2860 Sint-Katelijne-Waver 
1742 Sint-Katherina-lombeek 
9667 Sint-Kornelis-Horebeke 
8310 Sint-Kruis (Brugge) 
9042 Sint-Kruis-Winkel 
1750 Sint-Kwintens-Lennik 
3500 Sint-Lambrechts-Herk 
1200 Sint-Lambrechts-Woluwe 
9980 Sint-Laureins 
1600 Sint-Laureins-Berchem 
2960 Sint-Lenaerts 
9550 Sint-Lievens-Esse 
9981 Sint-Margriete 
9667 Sint-Maria-Horebeke 
9630 Sint-Maria-Latem 
9570 Sint-Maria-Lierde 
1700 Sint-Martens-Bodegem 
9800 Sint-Martens-Leerne 
1750 Sint-Martens-Lennik 
9572 Sint-Martens-Lierde 
3790 Sint-Martens-Voeren 
8200 Sint-Michiels 
9170 Sint-Pauwels 
1541 Sint-Pieters-Kapelle (Bt.) 
1600 Sint-Pieters-Leeuw 
3220 Sint-Pieters-Rode 
3792 Sint-Pieters-Voeren 
1150 Sint-Pieters-Woluwe 
8690 Sint-Rijkers 
1932 Sint-Stevens-Woluwe 
1700 Sint-Ulriks-Kapelle 
4851 Sippenaeken 
7332 Sirault 
6470 Sivry 
6470 Sivry-Rance 
9940 Sleidinge 
8433 Slijpe 
4450 Slins 
3700 Sluizen 
9506 Smeerebbe-Vloerzegem 
9340 Smetlede 
6890 Smuid 
8470 Snaaskerke 
8490 Snellegem 
4557 Soheit-Tinlot 
6920 Sohier 
7060 Soignies 
4861 Soiron 
6500 Solre-Saint-Géry 
6560 Solre-sur-Sambre 
5140 Sombreffe 
5377 Somme-Leuze 
6769 Sommethonne 
5523 Sommière 
5651 Somzée 
5340 Sorée 
5333 Sorinne-la-Longue 
5503 Sorinnes 
5537 Sosoye 
4920 Sougné-Remouchamps 
5680 Soulme 
4630 Soumagne 
5630 Soumoy 
4950 Sourbrodt 
6182 Souvret 
5590 Sovet 
6997 Soy 
5150 Soye (Nam.) 
4900 Spa 
3510 Spalbeek 
7032 Spiennes 
# 8587 Spiere 
5530 Spontin 
4140 Sprimont 
5190 Spy 
2940 Stabroek 
8840 Staden 
8490 Stalhille 
7973 Stambruges 
5646 Stave 
8691 Stavele 
4970 Stavelot 
9140 Steendorp 
1840 Steenhuffel 
9550 Steenhuize-Wijnhuize 
8630 Steenkerke (W.-VL.) 
7090 Steenkerque (Ht.) 
1820 Steenokkerzeel 
9190 Stekene 
4801 Stembert 
8400 Stene 
1933 Sterrebeek 
3512 Stevoort 
9200 St-Gillis-bij-Dendermonde 
3470 St-Margriete (Kortenaken) 
3300 St-Margriete-Houtem(Tien.) 
9660 St-Maria-Oudenhove(Brakel) 
9620 St-Maria-Oudenhove(Zott.) 
3650 Stokkem 
3511 Stokrooie 
4987 Stoumont 
8433 St-Pieters-Kapelle(W.-Vl.) 
6887 Straimont 
6511 Strée (Ht.) 
4577 Strée-lez-Huy 
7110 Strépy-Bracquegnies 
9620 Strijpen 
1760 Strijtem 
1853 Strombeek-Bever 
8600 Stuivekenskerke 
5020 Suarlée 
5550 Sugny 
5600 Surice 
6812 Suxy 
6661 Tailles 
7618 Taintignies 
5060 Tamines 
5651 Tarcienne 
4163 Tavier 
5310 Taviers (Nam.) 
6662 Tavigny 
6927 Tellin 
7520 Templeuve 
5020 Temploux 
9140 Temse 
6970 Tenneville 
1790 Teralfene 
2840 Terhagen 
6813 Termes 
1740 Ternat 
7333 Tertre 
3080 Tervuren 
4560 Terwagne 
3980 Tessenderlo 
3272 Testelt 
3793 Teuven 
4910 Theux 
6717 Thiaumont 
7070 Thieu 
7901 Thieulain 
#7061 Thieusies 
6230 Thiméon 
4890 Thimister 
4890 Thimister-Clermont 
7533 Thimougies 
1402 Thines 
6500 Thirimont 
4280 Thisnes 
4791 Thommen 
5300 Thon 
1360 Thorembais-les-Béguines 
1360 Thorembais-Saint-Trond 
7830 Thoricourt 
6536 Thuillies 
6530 Thuin 
7350 Thulin 
7971 Thumaide 
5621 Thy-le-Bauduin 
5651 Thy-le-Château 
5502 Thynes 
4367 Thys 
8573 Tiegem 
2460 Tielen 
9140 Tielrode 
8700 Tielt 
3390 Tielt (Bt.) 
3300 Tienen 
4630 Tignée 
4500 Tihange 
3150 Tildonk 
4130 Tilff 
6680 Tillet 
4420 Tilleur 
5380 Tillier 
1495 Tilly 
4557 Tinlot 
6637 Tintange 
6730 Tintigny 
2830 Tisselt 
6700 Toernich 
6941 Tohogne 
1570 Tollembeek 
2260 Tongerlo (Antw.) 
3960 Tongerlo (Limb.) 
7951 Tongre-Notre-Dame 
7950 Tongre-Saint-Martin 
5140 Tongrinne 
6717 Tontelange 
6767 Torgny 
8820 Torhout 
4263 Tourinne (Lg.) 
1320 Tourinnes-la-Grosse 
1457 Tourinnes-Saint-Lambert 
7500 Tournai 
6840 Tournay 
7904 Tourpes 
6890 Transinne 
6183 Trazegnies 
5670 Treignes 
# 4670 Trembleur 
3120 Tremelo 
7100 Trivières 
4280 Trognée 
4980 Trois-Ponts 
4870 Trooz 
1480 Tubize 
2300 Turnhout 
1180 Uccle 
6833 Ucimont 
3631 Uikhoven 
9290 Uitbergen 
8370 Uitkerke 
1180 Ukkel 
3832 Ulbeek 
5310 Upigny 
9910 Ursel 
3054 Vaalbeek 
3770 Val-Meer 
6741 Vance 
2431 Varendonk 
8490 Varsenare 
5680 Vaucelles 
7536 Vaulx (Tournai) 
6462 Vaulx-lez-Chimay 
6960 Vaux-Chavanne 
4530 Vaux-et-Borset 
6640 Vaux-lez-Rosières 
4051 Vaux-sous-Chèvremont 
6640 Vaux-sur-Sûre 
3870 Vechmaal 
5020 Vedrin 
2431 Veerle 
7760 Velaines 
5060 Velaine-sur-Sambre 
8210 Veldegem 
3620 Veldwezelt 
7120 Vellereille-les-Brayeux 
7120 Vellereille-le-Sec 
3806 Velm 
4460 Velroux 
3020 Veltem-Beisem 
9620 Velzeke-Ruddershove 
5575 Vencimont 
6440 Vergnies 
4537 Verlaine 
5370 Verlée 
9130 Verrebroek 
3370 Vertrijk 
4800 Verviers 
6870 Vesqueville 
3870 Veulen 
5300 Vezin 
7538 Vezon 
9500 Viane 
8570 Vichte 
6690 Vielsalm 
4317 Viemme 
2240 Viersel 
4577 Vierset-Barse 
5670 Vierves-sur-Viroin 
6230 Viesville 
1472 Vieux-Genappe 
4190 Vieuxville 
4530 Vieux-Waleffe 
6890 Villance 
4260 Ville-en-Hesbaye 
7322 Ville-Pommeroeul 
7334 Villerot 
4161 Villers-aux-Tours 
5630 Villers-Deux-Eglises 
6823 Villers-devant-Orval 
5600 Villers-en-Fagne 
6600 Villers-la-Bonne-Eau 
6769 Villers-la-Loue 
6460 Villers-la-Tour 
1495 Villers-la-Ville 
4530 Villers-le-Bouillet 
5600 Villers-le-Gambon 
4280 Villers-le-Peuplier 
4550 Villers-le-Temple 
4340 Villers-l'Evêque 
5080 Villers-lez-Heest 
7812 Villers-Notre-Dame 
6210 Villers-Perwin 
6280 Villers-Poterie 
7812 Villers-Saint-Amand 
6941 Villers-Sainte-Gertrude 
7031 Villers-Saint-Ghislain 
4453 Villers-Saint-Siméon 
5580 Villers-sur-Lesse 
6740 Villers-sur-Semois 
7021 Ville-sur-Haine (Mons) 
7070 Ville-sur-Haine(Le Roeulx) 
4520 Vinalmont 
9921 Vinderhoute 
8630 Vinkem 
9800 Vinkt 
6461 Virelles 
1460 Virginal-Samme 
5670 Viroinval 
6760 Virton 
4600 Visé 
3300 Vissenaken 
5070 Vitrival 
4683 Vivegnis 
6833 Vivy 
8600 Vladslo 
8908 Vlamertinge 
9420 Vlekkem 
8640 Vleteren 
1602 Vlezenbeek 
3724 Vliermaal 
3721 Vliermaalroot 
9520 Vlierzele 
3770 Vlijtingen 
2340 Vlimmeren 
8421 Vlissegem 
7880 Vloesberg 
5600 Vodecée 
5680 Vodelée 
3790 Voeren 
5650 Vogenée 
9700 Volkegem 
1570 Vollezele 
5570 Vonêche 
9400 Voorde 
8902 Voormezele 
3840 Voort 
4347 Voroux-Goreux 
4451 Voroux-lez-Liers 
2290 Vorselaar 
3890 Vorsen 
1190 Vorst 
2430 Vorst (Kempen) 
2350 Vosselaar 
9850 Vosselare 
3080 Vossem 
4041 Vottem 
9120 Vrasene 
2531 Vremde 
3700 Vreren 
5550 Vresse-sur-Semois 
3770 Vroenhoven 
3630 Vucht 
9890 Vurste 
4570 Vyle-et-Tharoul 
3473 Waanrode 
9506 Waarbeke 
8020 Waardamme 
2550 Waarloos 
8581 Waarmaarde 
9950 Waarschoot 
3401 Waasmont 
9250 Waasmunster 
7784 Waasten 
9185 Wachtebeke 
7971 Wadelincourt 
6223 Wagnelée 
6900 Waha 
5377 Waillet 
4950 Waimes 
8720 Wakken 
5650 Walcourt 
2800 Walem 
1457 Walhain 
1457 Walhain-Saint-Paul 
4711 Walhorn 
3401 Walsbets 
3401 Walshoutem 
3740 Waltwilder 
1741 Wambeek 
5570 Wancennes 
4020 Wandre 
6224 Wanfercée-Baulet 
3400 Wange 
6220 Wangenies 
5564 Wanlin 
4980 Wanne 
7861 Wannebecq 
9772 Wannegem-Lede 
4280 Wansin 
4520 Wanze 
9340 Wanzele 
7548 Warchin 
7740 Warcoing 
6600 Wardin 
8790 Waregem 
4300 Waremme 
5310 Waret-la-Chaussée 
4217 Waret-l'Evêque 
5080 Warisoulx 
5537 Warnant 
4530 Warnant-Dreye 
7784 Warneton 
7340 Warquignies 
4608 Warsage 
4590 Warzée 
7340 Wasmes 
7604 Wasmes-Audemez-Briffoeil 
7390 Wasmuel 
4219 Wasseiges 
9988 Waterland-Oudeman 
1410 Waterloo 
1170 Watermaal-Bosvoorde 
1170 Watermael-Boitsfort 
9988 Watervliet 
8978 Watou 
7910 Wattripont 
7131 Waudrez 
5540 Waulsort 
1440 Wauthier-Braine 
1300 Wavre 
5580 Wavreille 
6210 Wayaux 
1474 Ways 
3290 Webbekom 
2275 Wechelderzande 
2381 Weelde 
1982 Weerde 
2880 Weert 
4860 Wegnez 
5523 Weillen 
4950 Weismes 
9700 Welden 
4840 Welkenraedt 
9473 Welle 
3830 Wellen 
6920 Wellin 
1780 Wemmel 
8420 Wenduine 
5100 Wépion 
4190 Werbomont 
3118 Werchter 
6940 Wéris 
8610 Werken 
3730 Werm 
8940 Wervik 
3150 Wespelaar 
8434 Westende 
2260 Westerlo 
8300 Westkapelle 
8460 Westkerke 
2390 Westmalle 
2235 Westmeerbeek 
8954 Westouter 
9230 Westrem 
8840 Westrozebeke 
8640 Westvleteren 
9230 Wetteren 
8560 Wevelgem 
3111 Wezemaal 
1970 Wezembeek-Oppem 
3401 Wezeren 
7620 Wez-Velvain 
6666 Wibrin 
9260 Wichelen 
3700 Widooie 
2222 Wiekevorst 
8710 Wielsbeke 
5100 Wierde 
7608 Wiers 
5571 Wiesme 
9280 Wieze 
7370 Wihéries 
4452 Wihogne 
3990 Wijchmaal 
3850 Wijer 
3018 Wijgmaal (Bt.) 
2110 Wijnegem 
3670 Wijshagen 
8953 Wijtschate 
3803 Wilderen 
7904 Willaupuis 
3370 Willebringen 
2830 Willebroek 
7506 Willemeau 
5575 Willerzie 
2610 Wilrijk (Antwerpen) 
3012 Wilsele 
8431 Wilskerke 
3501 Wimmertingen 
5570 Winenne 
8750 Wingene 
3020 Winksele 
3722 Wintershoven 
6860 Witry 
7890 Wodecq 
8640 Woesten 
6780 Wolkrange 
1200 Woluwé-Saint-Lambert 
1150 Woluwé-Saint-Pierre 
1861 Wolvertem 
2160 Wommelgem 
3350 Wommersom 
4690 Wonck 
9032 Wondelgem 
9800 Wontergem 
9790 Wortegem 
9790 Wortegem-Petegem 
2323 Wortel 
9550 Woubrechtegem 
8600 Woumen 
8670 Wulpen 
8952 Wulvergem 
8630 Wulveringem 
2990 Wuustwezel 
4652 Xhendelesse 
4432 Xhendremael 
4190 Xhoris 
4550 Yernée-Fraineux 
5650 Yves-Gomezée 
5530 Yvoir 
9080 Zaffelare 
9506 Zandbergen 
8680 Zande 
2240 Zandhoven 
2040 Zandvliet 
8400 Zandvoorde (Oostende) 
8980 Zandvoorde (Zonnebeke) 
9500 Zarlardinge 
8610 Zarren 
1930 Zaventem 
8210 Zedelgem 
8380 Zeebrugge (Brugge) 
9660 Zegelsem 
9240 Zele 
3545 Zelem 
1731 Zellik 
9060 Zelzate 
1980 Zemst 
3800 Zepperen 
8490 Zerkegem 
1370 Zétrud-Lumay 
8470 Zevekote 
9080 Zeveneken 
9800 Zeveren 
9840 Zevergem 
3271 Zichem 
3770 Zichen-Zussen-Bolder 
8902 Zillebeke 
9750 Zingem 
2260 Zoerle-Parwijs 
2980 Zoersel 
3550 Zolder 
9930 Zomergem 
3520 Zonhoven 
8980 Zonnebeke 
9520 Zonnegem 
9620 Zottegem 
8630 Zoutenaaie 
8904 Zuidschote 
8377 Zuienkerke 
9870 Zulte 
9690 Zulzeke 
3690 Zutendaal 
9630 Zwalm 
8550 Zwevegem 
8750 Zwevezele 
9052 Zwijnaarde 
2070 Zwijndrecht
"""

fr = u"""
4750 Butgenbach 
75008 PARIS 
40120 ROQUEFORT 
69650 VILLENEUVE D'ASCQ
59650 VILLENEUVE D'ASCQ 
59651 VILLENEUVE D'ASCQ 
"""


def objects():
    countries = dd.resolve_app('countries')
    city = Instantiator(countries.Place, "zip_code name",
                        country='BE',
                        type=countries.PlaceTypes.city).build
    for ln in belgian_cities.splitlines():
        ln = ln.strip()
        if ln and ln[0] != '#':
            args = ln.split(None, 1)
            o = city(*args)
            # print "%r %r" % (o.zip_code, o.name)
            yield o
            #~ print __name__, "20121114"
            #~ return
    for ln in belgian_cities_nl_fr.splitlines():
        ln = ln.strip()
        if ln and ln[0] != '#':
            args = ln.split('|')
            if len(args) != 4:
                raise Exception("Invalid format : \n%s" % ln)
            args = [x.strip() for x in args]
            o = city(zip_code=args[0], **dd.babel_values('name',
                     nl=args[1], fr=args[2], de=args[3], en=args[3]))
            yield o
