# Nonogrammu risināšana ar simulēto atkvēlināšanu

Konsoles programma Python 3.10 vai jaunākai versijai. Risinātājs, līniju variantu ģenerēšana un soda funkcija realizēti patstāvīgi. Izmantota tikai Python standarta bibliotēka; papildu pakotnes nav jāinstalē.

## Failu struktūra

| Fails vai mape | Saturs |
| --- | --- |
| [nonogram.py](nonogram.py) | Programmas palaišanas punkts; saglabā arī iepriekšējos funkciju importus. |
| [nonogram_solver/puzzle.py](nonogram_solver/puzzle.py) | Matricas lasīšana, norāžu iegūšana un pieļaujamo līniju variantu ģenerēšana. |
| [nonogram_solver/evaluation.py](nonogram_solver/evaluation.py) | Kolonnas soda aprēķins un LRU kešatmiņa. |
| [nonogram_solver/moves.py](nonogram_solver/moves.py) | Bloka nobīde, ievērojot rindas norādes un robežas. |
| [nonogram_solver/solver.py](nonogram_solver/solver.py) | SA meklēšana, temperatūra, gājienu pieņemšana, labākais stāvoklis un rezultāts. |
| [nonogram_solver/cli.py](nonogram_solver/cli.py) | Komandrindas argumenti, animācija, atkārtotas palaišanas un CSV izvade. |
| [nonogram_solver/__init__.py](nonogram_solver/__init__.py) | Paketes publiskās funkcijas importēšanai. |
| [tests/](tests/) | 15 korektuma testi SA un pārlases pārbaudēm. |
| [benchmark_bruteforce.py](benchmark_bruteforce.py) | Pilnās pārlases ātruma mērījums. |
| [examples/](examples/) | Visas 35 testa matricas. |
| [old test results/](old%20test%20results/) | Iepriekšējie eksperimenti, papildu palaišanu CSV un rezultātu rezerves kopijas. |

## Testa matricas un ievade

| Izmērs | Piemēru skaits |
| --- | --- |
| 5×5 | 8 |
| 10×10 | 8 |
| 15×15 | 8 |
| 20×20 | 7 |
| 30×30 | 2 |
| 50×50 | 2 |

Faili mapē `../examples` satur nulles un vieniniekus: `1` ir aizpildīta šūna, `0` — tukša. Atļautas atstarpes, tukšas rindas un komentāri pēc `#`. Visām matricas rindām jābūt vienāda garuma.

```text
# Krusts 5×5
00100
01110
11111
01110
00100
```

No matricas iegūst rindu un kolonnu norādes. Meklēšanā sākotnējais attēls netiek izmantots. Par pareizu uzskata jebkuru matricu ar tām pašām norādēm. Piemēri ietver gan figūras, gan nejaušus režģus. `sparse_30` un `sparse_50` satur 50% vieninieku un daudz īsu bloku; tie atšķiras no mazāko sparse piemēru ģenerēšanas ar aizpildīšanas varbūtību 0,35.

## Palaišana bez animācijas

```console
python nonogram.py solve examples/heart_10.txt --move mixed --shift-probability 0.5 --iterations 100000 --restart-every 100000 --seed 0
```

Labākās atrastās matricas saglabāšana failā:

```console
python nonogram.py solve examples/heart_10.txt --move mixed --shift-probability 0.5 --iterations 100000 --restart-every 100000 --seed 0 --output solutions/heart_10.txt
```

## Palaišana ar animāciju

```console
python nonogram.py solve examples/heart_10.txt --move mixed --shift-probability 0.5 --iterations 100000 --restart-every 100000 --seed 0 --animate --delay 0.03
```

Animācija izmanto ANSI termināļa komandas, tāpēc piemērots ir Windows Terminal vai cits terminālis ar ANSI atbalstu. `##` apzīmē aizpildītu šūnu, `..` — tukšu. `--delay` nosaka pauzi sekundēs starp kadriem. Tiek parādīts sākuma stāvoklis, pārstartējumi un pieņemtie gājieni. Animācija attēlo pašreizējo stāvokli, gala izvade attēlos labāko atrasto. Animācijas pauzes pagarina izpildes laiku; ātruma testiem izmantojiet `benchmark`, kur animācija ir izslēgta.

## Visu piemēru testēšana

PowerShell komandas četriem režīmiem. Rezultāti tiek rakstīti mapē `new_results/`, saglabājot jau iegūtos gala CSV projekta pamatmapē. Ja norādītais izvades CSV jau eksistē, programma to pārraksta; jaunam eksperimentam izvēlieties jaunu faila vai mapes nosaukumu.

```powershell
$inputs = Get-ChildItem examples/*.txt | ForEach-Object { $_.FullName }
python nonogram.py benchmark $inputs --runs 10 --seed 0 --move mixed --shift-probability 0 --iterations 100000 --restart-every 100000 --csv new_results/results_all_iter100000_shift0.csv
python nonogram.py benchmark $inputs --runs 10 --seed 0 --move mixed --shift-probability 0.5 --iterations 100000 --restart-every 100000 --csv new_results/results_all_iter100000_shift50.csv
python nonogram.py benchmark $inputs --runs 10 --seed 0 --move mixed --shift-probability 0.8 --iterations 100000 --restart-every 100000 --csv new_results/results_all_iter100000_shift80.csv
python nonogram.py benchmark $inputs --runs 10 --seed 0 --move mixed --shift-probability 1 --iterations 100000 --restart-every 100000 --csv new_results/results_all_iter100000_shift100.csv
```

`--runs 10` nozīmē 10 neatkarīgas palaišanas katrai matricai ar seed 0–9. `--restart-every 100000` kopā ar `--iterations 100000` izslēdz iekšējos pārstartējumus. Sarežģītie sparse piemēri var prasīt vairākas minūtes vienai palaišanai.

Viena piemēra palaišana ar meklēšanas laika limitu:

```console
python nonogram.py solve examples/sparse_20.txt --move mixed --shift-probability 0.5 --time-limit 15 --seed 0
```

Laika režīmā `--time-limit` aizstāj iterāciju budžetu, izslēdz pārstartējumus un nosaka temperatūras samazināšanos pēc pagājušā laika. Līniju variantu sagatavošana neietilpst meklēšanas laika limitā.

## Galvenie parametri

| Parametrs | Noklusējums | Nozīme |
| --- | --- | --- |
| `--move` | `row` | `row` — rindas aizstāšana; `mixed` — aizstāšanas un bloka nobīdes. |
| `--shift-probability` | `0.8` | Nobīdes mēģinājuma varbūtība jauktajā režīmā, no 0 līdz 1. |
| `--iterations` | `100000` | Maksimālais piedāvāto gājienu skaits vienā palaišanā. |
| `--restart-every` | `10000` | Gājienu skaits līdz jaunam nejaušam sākuma stāvoklim un temperatūras atiestatīšanai. |
| `--time-limit` | Nav | Meklēšanas laika limits sekundēs; aizstāj iterāciju budžetu. |
| `--seed` | `0` | Nejaušo skaitļu ģeneratora sākumvērtība. |
| `--start-temp` / `--end-temp` | `2.5` / `0.05` | Sākuma un beigu temperatūra. |
| `--max-patterns` | `100000` | Lielākais atļautais variantu skaits vienai rindai vai kolonnai. |
| `--animate` / `--delay` | Izslēgts / `0.1` | Animācija un pauze sekundēs; tikai komandai `solve`. |
| `--output` | Nav | Labākās matricas izvades fails; tikai komandai `solve`. |
| `--runs` | `20` | Neatkarīgo palaišanu skaits katram piemēram; tikai `benchmark`. |
| `--csv` | `results.csv` | Eksperimenta rezultātu fails; tikai `benchmark`. |

## Soda funkcija un algoritms

Katrā stāvoklī rindas atbilst savām norādēm. Kolonnas sods ir mazākais Heminga attālums līdz pieļaujamam kolonnas variantam; kopējais sods ir kolonnu sodu summa. Sods 0 nozīmē pareizu risinājumu. Tas ir zināmais optimums visiem testa piemēriem. Sods, kas nav 0, nav precīzs labojamo šūnu skaits līdz pilnam risinājumam un nav attālums līdz sākotnējam attēlam.

Ja `delta = jaunais sods - pašreizējais sods` nav pozitīvs, gājiens tiek pieņemts. Pretējā gadījumā to pieņem ar varbūtību `exp(-delta / T)`. Temperatūra samazinās ģeometriski. Labākais stāvoklis tiek saglabāts atsevišķi; meklēšana beidzas pie soda 0 vai budžeta beigās.

Pārrēķina tikai izmainītās kolonnas. Katram kolonnas novērtētājam ir LRU kešatmiņa ar 4096 ierakstiem. Variantu pārbaudi var pārtraukt, sasniedzot apakšējo robežu — aizpildīto šūnu skaita starpību. Ja pirms vienas šūnas maiņas kolonnas sods bija 0, jaunais sods ir 1. Neiespējams nobīdes mēģinājums nemaina stāvokli, bet patērē iterāciju.

Komandas `solve` iziešanas kodi: `0` — atrasts risinājums, `2` — budžets izsmelts, `1` — ievades vai parametru kļūda. `benchmark` atgriež `0`, ja eksperiments pabeigts, arī tad, ja dažas palaišanas neatrada risinājumu.

## Gala rezultātu faili

Gala rezultāti atrodas projekta pamatmapē:

- [results_all_iter100000_shift0.csv](../results_all_iter100000_shift0.csv) — 0% nobīdes mēģinājumu.
- [results_all_iter100000_shift50.csv](../results_all_iter100000_shift50.csv) — 50% nobīdes mēģinājumu.
- [results_all_iter100000_shift80.csv](../results_all_iter100000_shift80.csv) — 80% nobīdes mēģinājumu.
- [results_all_iter100000_shift100.csv](../results_all_iter100000_shift100.csv) — 100% nobīdes mēģinājumu.

Katrā failā ir 350 unikālas pabeigtas palaišanas: 35 matricas × 10 seed. Papildu palaišanu dati jau apvienoti ar sākotnējiem rezultātiem. Iepriekšējie CSV, papildinājumu faili, 15 sekunžu eksperimenta salīdzinājums, žurnāls un rezerves kopijas pārvietoti uz [old test results/](old%20test%20results/README.md). Papildu palaišanu CSV nav jāpievieno gala failiem atkārtoti.

CSV kolonnas ietver ievades failu, izmērus, seed, atrisināšanas faktu, labāko sodu, optimumu, iterācijas, pārstartējumus, sagatavošanas, meklēšanas un kopējo laiku, parametrus un apstāšanās iemeslu. `stop_reason=solved` apzīmē risinājumu, `iteration_limit` — izsmeltu iterāciju budžetu.

## Gala statistika

Eksperiments: 35 piemēri, katram 10 seed (0–9) četros režīmos, kopā 1400 palaišanas. Budžets — līdz 100 000 iterācijām, bez pārstartējumiem un laika limita; temperatūra 2,5 → 0,05, `max_patterns=100000`. Animācija bija izslēgta. Ja atrasts risinājums, palaišana beidzas agrāk.

Vidējais sods un laiks aprēķināts arī neveiksmīgajām palaišanām. Kopējais laiks ietver variantu sagatavošanu un meklēšanu, bet ne ievades lasīšanu un norāžu iegūšanu.

| Rādītājs | 0% | 50% | 80% | 100% |
| --- | --- | --- | --- | --- |
| Atrasti risinājumi | 304/350 | 313/350 | 310/350 | 282/350 |
| Veiksmīgo palaišanu īpatsvars | 86,86% | 89,43% | 88,57% | 80,57% |
| Vidējais sods | 6,35 | 4,31 | 5,37 | 9,27 |
| Vidējais kopējais laiks, s | 22,656 | 13,758 | 8,602 | 1,367 |

50% režīmam ir visvairāk risinājumu un mazākais vidējais sods. 80% režīms ir vidēji par 37,5% ātrāks nekā 50%, bet ar lielāku vidējo sodu. Starp tiem ir tikai trīs atrasto risinājumu atšķirība. 100% režīms ir vidēji visātrākais, taču ar zemāko kvalitāti. Šie secinājumi attiecas uz izmantoto testa kopu, nevis visām nonogrammām.

### Atrastie risinājumi visām matricām

Katras šūnas vērtība: atrasto risinājumu skaits no 10 palaišanām.

| Matrica | 0% | 50% | 80% | 100% |
| --- | --- | --- | --- | --- |
| [boat_5.txt](../examples/boat_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [cross_5.txt](../examples/cross_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [dense_5.txt](../examples/dense_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [fish_5.txt](../examples/fish_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [house_5.txt](../examples/house_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [ring_5.txt](../examples/ring_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [sparse_5.txt](../examples/sparse_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [tree_5.txt](../examples/tree_5.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [boat_10.txt](../examples/boat_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [dense_10.txt](../examples/dense_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [fish_10.txt](../examples/fish_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [heart_10.txt](../examples/heart_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [house_10.txt](../examples/house_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [ring_10.txt](../examples/ring_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [sparse_10.txt](../examples/sparse_10.txt) | 10/10 | 10/10 | 10/10 | 5/10 |
| [tree_10.txt](../examples/tree_10.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [boat_15.txt](../examples/boat_15.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [dense_15.txt](../examples/dense_15.txt) | 10/10 | 10/10 | 10/10 | 3/10 |
| [diamond_15.txt](../examples/diamond_15.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [fish_15.txt](../examples/fish_15.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [house_15.txt](../examples/house_15.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [ring_15.txt](../examples/ring_15.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [sparse_15.txt](../examples/sparse_15.txt) | 0/10 | 4/10 | 2/10 | 2/10 |
| [tree_15.txt](../examples/tree_15.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [boat_20.txt](../examples/boat_20.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [dense_20.txt](../examples/dense_20.txt) | 7/10 | 10/10 | 7/10 | 0/10 |
| [fish_20.txt](../examples/fish_20.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [house_20.txt](../examples/house_20.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [ring_20.txt](../examples/ring_20.txt) | 8/10 | 9/10 | 10/10 | 9/10 |
| [sparse_20.txt](../examples/sparse_20.txt) | 0/10 | 0/10 | 1/10 | 0/10 |
| [tree_20.txt](../examples/tree_20.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [house_30.txt](../examples/house_30.txt) | 10/10 | 10/10 | 10/10 | 10/10 |
| [sparse_30.txt](../examples/sparse_30.txt) | 0/10 | 0/10 | 0/10 | 0/10 |
| [house_50.txt](../examples/house_50.txt) | 9/10 | 10/10 | 10/10 | 3/10 |
| [sparse_50.txt](../examples/sparse_50.txt) | 0/10 | 0/10 | 0/10 | 0/10 |

### Vidējais gala sods visām matricām

| Matrica | 0% | 50% | 80% | 100% |
| --- | --- | --- | --- | --- |
| boat_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| cross_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| dense_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| fish_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| house_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| ring_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| sparse_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| tree_5.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| boat_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| dense_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| fish_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| heart_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| house_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| ring_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| sparse_10.txt | 0,00 | 0,00 | 0,00 | 1,00 |
| tree_10.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| boat_15.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| dense_15.txt | 0,00 | 0,00 | 0,00 | 2,00 |
| diamond_15.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| fish_15.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| house_15.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| ring_15.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| sparse_15.txt | 2,40 | 1,20 | 1,60 | 2,80 |
| tree_15.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| boat_20.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| dense_20.txt | 0,60 | 0,00 | 0,80 | 10,80 |
| fish_20.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| house_20.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| ring_20.txt | 0,60 | 0,40 | 0,00 | 0,40 |
| sparse_20.txt | 6,60 | 4,00 | 4,20 | 7,20 |
| tree_20.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| house_30.txt | 0,00 | 0,00 | 0,00 | 0,00 |
| sparse_30.txt | 62,80 | 45,60 | 49,20 | 65,20 |
| house_50.txt | 0,20 | 0,00 | 0,00 | 22,20 |
| sparse_50.txt | 149,20 | 99,80 | 132,20 | 212,80 |

### Vidējais kopējais laiks visām matricām, sekundēs

| Matrica | 0% | 50% | 80% | 100% |
| --- | --- | --- | --- | --- |
| boat_5.txt | 0,000090 | 0,000103 | 0,000127 | 0,000128 |
| cross_5.txt | 0,000125 | 0,000180 | 0,000211 | 0,000210 |
| dense_5.txt | 0,000140 | 0,000162 | 0,000202 | 0,000181 |
| fish_5.txt | 0,000079 | 0,000111 | 0,000107 | 0,000118 |
| house_5.txt | 0,000161 | 0,000142 | 0,000164 | 0,000210 |
| ring_5.txt | 0,000103 | 0,000079 | 0,000090 | 0,000110 |
| sparse_5.txt | 0,000199 | 0,000220 | 0,000386 | 0,000266 |
| tree_5.txt | 0,000166 | 0,000259 | 0,000238 | 0,000204 |
| boat_10.txt | 0,0061 | 0,0051 | 0,0081 | 0,0057 |
| dense_10.txt | 0,0477 | 0,0527 | 0,0570 | 0,0588 |
| fish_10.txt | 0,0022 | 0,0025 | 0,0042 | 0,0039 |
| heart_10.txt | 0,0036 | 0,0027 | 0,0033 | 0,0053 |
| house_10.txt | 0,0182 | 0,0151 | 0,0173 | 0,0181 |
| ring_10.txt | 0,0155 | 0,0130 | 0,0089 | 0,0160 |
| sparse_10.txt | 0,0478 | 0,0535 | 0,0535 | 0,1165 |
| tree_10.txt | 0,0187 | 0,0165 | 0,0209 | 0,0190 |
| boat_15.txt | 0,0423 | 0,0419 | 0,0454 | 0,0442 |
| dense_15.txt | 0,1142 | 0,1083 | 0,1004 | 0,1673 |
| diamond_15.txt | 0,0535 | 0,0577 | 0,0620 | 0,0559 |
| fish_15.txt | 0,0275 | 0,0305 | 0,0235 | 0,0298 |
| house_15.txt | 0,0528 | 0,0529 | 0,0511 | 0,0467 |
| ring_15.txt | 0,0466 | 0,0489 | 0,0466 | 0,0498 |
| sparse_15.txt | 0,4528 | 0,3680 | 0,3297 | 0,2796 |
| tree_15.txt | 0,0572 | 0,0541 | 0,0516 | 0,0538 |
| boat_20.txt | 0,0733 | 0,0748 | 0,0685 | 0,0717 |
| dense_20.txt | 0,9364 | 0,5713 | 0,4236 | 0,3274 |
| fish_20.txt | 0,0459 | 0,0502 | 0,0530 | 0,0504 |
| house_20.txt | 0,0793 | 0,0761 | 0,0706 | 0,0718 |
| ring_20.txt | 0,1089 | 0,0962 | 0,0783 | 0,1103 |
| sparse_20.txt | 6,196 | 4,096 | 2,635 | 1,370 |
| tree_20.txt | 0,1759 | 0,1498 | 0,1234 | 0,1122 |
| house_30.txt | 0,1343 | 0,1164 | 0,1079 | 0,0998 |
| sparse_30.txt | 55,906 | 35,139 | 19,440 | 5,265 |
| house_50.txt | 0,4027 | 0,2478 | 0,2185 | 0,3556 |
| sparse_50.txt | 727,908 | 439,973 | 276,979 | 39,039 |

Sparse_30 un sparse_50 netika atrisināti nevienā no 40 palaišanām katram piemēram. House_50 abos jauktajos režīmos atrisināts 10/10. Tātad grūtību nosaka arī norāžu struktūra. Sparse_50 vienai līnijai ir līdz 65 780 variantiem; atkārtots kolonnu soda aprēķins būtiski pagarina meklēšanu. Lielajiem sparse piemēriem ir liela ietekme uz kopējo vidējo laiku. Desmit palaišanas vienai matricai neļauj noteikt universāli labāko gājienu proporciju.

## Salīdzinājums ar pilno pārlasi

| Testa piemērs | Matricu kombināciju skaits | Pilnas pārlases laiks* | SA vidējais kopējais laiks (50%) | SA atrisināts |
| --- | ---: | ---: | ---: | ---: |
| [house_5](examples/house_5.txt) | 90 | 0,000098 s | 0,000142 s | 10/10 |
| [house_10](examples/house_10.txt) | 1,04 × 10^7 | 11,61 s | 0,015125 s | 10/10 |
| [house_15](examples/house_15.txt) | 6,34 × 10^13 | 2,92 g. | 0,052911 s | 10/10 |
| [house_20](examples/house_20.txt) | 5,66 × 10^21 | 2,60 × 10^8 g. | 0,076060 s | 10/10 |
| [house_30](examples/house_30.txt) | 2,05 × 10^37 | 1,40 × 10^24 g. | 0,116431 s | 10/10 |
| [house_50](examples/house_50.txt) | 4,82 × 10^75 | 6,03 × 10^62 g. | 0,247835 s | 10/10 |

*Pilna pārlase `house_5` un `house_10` faktiski veikta piecas reizes; tabulā norādīts vidējais laiks. Pārējiem piemēriem laiks ir aptuvena ekstrapolācija: katrā no piecām palaišanām pārbaudītas 100 000 kombinācijas nejauši izvēlētā secīgā intervālā. Vienā gadā pieņemtas 365,25 dienas.

Matricu kombināciju skaits ir visu rindu pieļaujamo variantu skaitu reizinājums: `M = R_1 * R_2 * ... * R_h`. Laika prognoze ir `t = M / v`, kur `v` ir kopējais pārbaudīto kombināciju skaits, dalīts ar to pārbaudes kopējo laiku. Pieņemts, ka izmērītais vidējais ātrums saglabājas visā kombināciju telpā.


### Pārlases rezultātu faili

- [Sešu house piemēru mērījumi](bruteforce_results/benchmark_house_sizes_20261010.csv) un [metadati](bruteforce_results/benchmark_house_sizes_20261010.json).
- [house_10 faktiskās pilnās pārlases mērījumi](bruteforce_results/benchmark_house10_full_20261010.csv) un [metadati](bruteforce_results/benchmark_house10_full_20261010.json).
- [SA rezultāti, 50% režīms](results_all_iter100000_shift50.csv).

Mērījumu atkārtošana PowerShell vidē. Ja izvades CSV vai tā JSON metadati jau eksistē, izvēlieties jaunu faila nosaukumu.

```powershell
$inputs = 5,10,15,20,30,50 | ForEach-Object { "examples/house_$_.txt" }
python benchmark_bruteforce.py $inputs --samples 100000 --runs 5 --seed 0 --csv bruteforce_results/house_sizes_repeat.csv
python benchmark_bruteforce.py examples/house_10.txt --samples 10418625 --runs 5 --seed 0 --csv bruteforce_results/house10_full_repeat.csv
```
