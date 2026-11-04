# A házi feladatokról

A laborok programozásos része (házi feladatok) során egy komplexebb szoftvert kell elkészíteni.

Az eheti feladat egy determinisztikus véges automata (DFA) szimulációjának megvalósításáról szól. A későbbiekben további funkciókkal bővítjük az automata képességeit. Minden feladat parancssori paraméterekkel lesz konfigurálható, így a program működése rugalmasan szabályozható.

A feladatok kiértékelése egy automatikus rendszerrel történik, amely **minden egyes** pusholás után lefut. Ezért kiemelten fontos a pontos megvalósítás és a megfelelő kimenetek biztosítása. A legkisebb eltérés is hibás teszteredményekhez vezethet!

A projekt indulópontja a kötelezően használandó `project` modul vagy `main.cpp` fájl lesz (érdemes az elején eldönteni és utána abban dolgozni, az esetleges menet közbeni nyelvváltás nem ajánlott, mivel a feladatok egymásra épülnek, ezért újra kell implementálni az addigi feladatokat - amennyiben mégis erre kerülne sor, ezt jelezd). A létrehozott starter projektet szabadon ki lehet bővíteni, de a főfájl megnevezése nem változtatható. Minden egyes pusholáskor az automatikus tesztek lefutnak, így többször is ellenőrizheted a program helyes működését. Az összesítő eredmények a GitHub felületén, a
commitok mellett jelennek meg: zöld pipa jelzi a sikeres tesztelést, piros X pedig a hibát. Hibás teszt esetén a részletes logokban megtalálható, hogy pontosan mi okozta a problémát, így a visszajelzés alapján könnyen javítható a kód.

A feladatok manuális átvizsgáláson is átesnek, hogy kiszűrjük az esetleges csalásokat vagy másolásokat.

# Nulladik lépések

1. Forkold le a repositoryt.
2. Github weboldalon --> `Actions` tab --> `I understand my workflows, go ahead and enable them`

Alapvetően amikor egy workflow-t tartalmazó repositoryt leforkolsz, az actionök ki vannak kapcsolva, újra kell őket aktiválni. Ezek segítségével fogjuk tudni megcsinálni az automatikus tesztelést.

# Starter projektek

Starter projektre azért van szükség, hogy egységes struktúrájú projektje legyen mindenkinek, ezzel lehetővé téve az azonnali automatikus tesztelést. Jelenleg két nyelv (template) közül lehet válaszani: C++ vagy Python.

A projekt leklónozása után töröljük ki az összes starter projektet, kivéve azt, amit választottunk. Ha például Pythonra esik a választás, töröljük ki az összes olyan mappát, amely nem a `python-starter` mappa.

## Python nyelv esetén

Python esetén a `python-starter` nevű mappa tartalmaz egy kiinduló projektet, ami használható a feladatok megoldására.

A repository tartalmaz egy `project` nevű modult, amelyben van egy `problems` nevű almodul. Mindenképp tartsuk meg ezt a mappaszerkezetet, hogy az automatikus tesztek lefussanak.

Amennyiben a saját kódunkat akarjuk hozzáadni a projekthez, szükséges egy újabb fájl létrehozása a `problems` mappában tetszőleges néven. Ahhoz, hogy a rendszerbe beintegrálódjon a megoldásunk, fontos, hogy az új fájl taralmazzon egy osztályt, amelyet a `Problems` osztályból származtatunk. Az almodul tartalmaz egy példa fájlt (feladatot) erre, amely bemutatja hogyan lehet ezt kivitelezni: ez lesz a `sum.py`, amely beolvassa az argumentumokat, majd összeadja azokat (a számok vesszővel vannak elválasztva). A **bemeneti fájlok** a `python-starter` mappába kell kerüljenek.

A program és a teljes start projekt el van látva kommentekkel, amelyek segítenek a megértésében és a benne való eligazodásában.

Ha nem szeretnénk használni a megadott sablont, helyettesíthetjük bármivel. A fontos az, hogy maradjon meg a `project` nevű modul, és futtatható legyen a következő paranccsal:

```bash
python -m project
```

## 2. feladat: véges automata determinizálása

A Python-megoldás a `python-starter` mappából futtatható:

```bash
cd python-starter
python -m project --input input_file1.txt --output output_file1.txt --det
```

A bemeneti fájl első négy sora rendre az állapotokat, az ábécét, a kezdőállapotot
és a végállapotokat tartalmazza. Ezek után soronként az átmenetek következnek
`forrásállapot szimbólum célállapot` formában. Minden sorban az elemeket
szóköz választja el. Például:

```text
q0 q1 q2
0 1
q0
q2
q0 0 q1
q0 0 q2
q1 1 q2
```

A program a kezdőállapotból elérhető állapothalmazokat determinizálja, `s0`,
`s1`, ... jelölést használ, és az eredményt a `--output` fájlba írja. A hiányzó
átmenetek nem eredményeznek új, üres állapotot.

## 3. feladat: véges automata minimalizálása

A minimalizálás a `python-starter` mappából futtatható:

```bash
python -m project --input input_file1.txt --output output_file1.txt --mini
```

A bemeneti fájl követi a 2. feladatban leírt automataformátumot. A program
minimalizálja a kezdőállapotból elérhető állapotokat, az összevont állapotokat
az eredeti állapotok sorrendje szerinti legkisebb sorszámukkal nevezi el
(`s0`, `s1`, ...), és a hiányzó átmeneteket nem írja ki.
A PDF három példájának bemenete a `python-starter/mini_input1.txt`,
`mini_input2.txt` és `mini_input3.txt` fájlokban található; a hozzájuk tartozó
elvárt kimenetek rendre a `mini_output1.txt`, `mini_output2.txt` és
`mini_output3.txt` fájlokban vannak.

## C++ nyelv esetén

C++ esetén a `cpp-starter` nevű mappa tartalmaz egy kiinduló projektet, ami használható a feladatok megoldására.

Mindenképp tartsuk meg a `CMakeLists.txt` állományt, hogy az automatikus tesztek lefussanak.

Amennyiben a saját kódunkat akarjuk hozzáadni a projekthez, szükséges egy új cpp/hpp pár létrehozása a `problems` mappában tetszőleges néven. Ahhoz, hogy a rendszerbe beintegrálódjon a megoldásunk, fontos, hogy az új fájl taralmazzon egy osztályt, amelyet a `Problem` osztályból származtatunk (`problem.hpp` headerből). Az osztályunkat be kell helyezni a `main.cpp`-ben a `problems` nevű vektorba. A kiinduló projekt tartalmaz egy példa feladatot erre, amely bemutatja hogyan lehet ezt kivitelezni: ez lesz a `sum.cpp` és a `sum.hpp` állomány, amely beolvassa az argumentumokat, majd összeadja azokat (a számok szóközzel vagy új sorral vannak elválasztva). A **bemeneti fájlok** a `build` mappába kell kerüljenek.

A program és a teljes start projekt el van látva kommentekkel, amelyek segítenek a megértésében és a benne való eligazodásában.

Ha nem szeretnénk használni a megadott sablont, helyettesíthetjük bármivel. A fontos az, hogy maradjon meg a `CMakeLists.txt` állomány, és futtatható legyen a projekt a következő parancssorozattal:

```bash
mkdir build
cd build
cmake ..
make -j$(nproc)
./project
```
