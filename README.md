# Bundestagstwitter

<img width="1440" alt="bundestwitter" src="https://user-images.githubusercontent.com/77919093/136674639-422c6804-b70c-4361-a38e-deab798e3b25.png">

Eine Web-App, die alle bekannten Twitter-Konten von Bundestagsabgeordneten des Bundestags 2017-2021 visualisiert und vergleichbar macht.
. 
Fragen am besten den [Post](https://skriptum.github.io/blog/projects/2021/02/16/bundestwitter.html) oder eine [Mail](mailto:kkx@protonmail.com). 

## Funktionsweise

Die App baut auf den wunderbar von [pollytix](pollytix.de) angesammelten twitter listen auf, die alle Mitglieder des Bundestages (MdBs) nach Parteien sortiert hat. 

Diese Listen habe ich kopiert und alle Twitter-Handles nach Parteien gesammelt. Das Skript fetch.py nutzt dann diese Sammlung, um mit der Twitter-API zu interagieren und die letzten 50 Tweets jedes MdBs zu sammeln und einige Berechnungen damit anzufangen. 

Die Daten werden alle in einem *pandas*-DataFrame gesammelt und als simple CSV an die Dash-App weitergegeben.

*DASH*: Ein Python-Webframework, basierend auf *Flask* . [Überblick über Dash](https://plotly.com/dash/) 

Die Dash-App visualisert daraufhin alle gesammelten Daten je nach Profil und baut verschiedene Graphen, wie zum Beispiel die *Treemap* oder die Vergleiche. 

Außerdem habe ich per Hand soviele MdBs wie möglich ihren Wahlkreisen zugeordnet (hat lange gedauert) und diese daraufhin auf eine Karte projeziert

## Datengrundlage

[Geometrien der Wahlkreise](https://bundeswahlleiter.de/bundestagswahlen/2017/wahlkreiseinteilung/downloads.html) 

[Wahlergebnisse nach Wahlkreisen](https://www.bundeswahlleiter.de/bundestagswahlen/2017/ergebnisse.html)

[Twitter-Listen](https://twitter.com/pollytix_gmbh/lists)

## Nachbauen

Einfach das Repo klonen (ich nehme jetzt an, dass du mit *git* und *python* einigermaßen vertraut bist). 

```bash
git clone https://github.com/skriptum/bundestag
cd bundestag
```

Das Programm benötigt einen Zugang zur Twitter-API (über einen Developer-Account, [hier nachlesen](https://help.twitter.com/de/rules-and-policies/twitter-api)), abgelegt in einer Datei namens *config.ini* in der Form

```ini
[Twitter]
con_key = Consumer Key
con_secret = Consumer Secret
```

Diese Datei erstellen und dann in die Dash App wechseln und starten

```bash
cd dash
python app.py
```

Viel Spaß :)

