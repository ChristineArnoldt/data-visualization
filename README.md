Flight Data Analysis and Visualization for DSVS-2021-Eichin

# Aufgabenstellung
Sie finden unter in der folgenden Tabelle verschiedene Datensets.

| Name | Größe (Rows x Cols) | URL |
| --- | --- | --- |
| Alle Flüge | 13447 x 20 | https://gist.githubusercontent.com/florianeichin/cfa1705e12ebd75ff4c321427126ccee/raw/c86301a0e5d0c1757d325424b8deec04cc5c5ca9/flights_all_cleaned.csv 
| Subset der Flüge | 15 x 20 | https://gist.githubusercontent.com/florianeichin/b877d354d6bc52e6ce840572e40b0497/raw/19759410471073756a388dada5fcb40109f0d13e/flights_subset_cleaned.csv
| Originaldaten | 5819079 x 31 | https://www.kaggle.com/usdot/flight-delays#flights.csv

Es handelt sich dabei um das Datenset der Airlines, das Sie bereits aus den Übungen zur Vorlesung kennen.
Ihre Aufgabe ist es, Visualisierungen der Daten zu erstellen. 
Das Datenset bietet Einblicke in die Verspätungen und Flugzeiten aller Flüge eines Tages des Jahres 2015 in den USA inklusive Daten zu den Abflug- und Zielflughäfen, Airlines und Flugnummern.

## Inspiration
Zur Inspiration können folgende Fragestellungen dienen:
- Gibt es Flughäfen, die besonders viel oder wenig Verspätungen beim Abflug aufbauen?
- Gibt es Airlines, die besonders viel oder wenig Verspätungen beim Abflug aufbauen?
- Gibt es Flüge, die besonders viel oder wenig Verspätungen beim Abflug aufbauen?
- Gibt es Flüge oder Airlines, die besonders viel Zeit in der Luft aufholen?
- Gibt es Wochentage mit starker Verspätung?

Außerdem ist hier das Video [36C3 - BahnMining - Pünktlichkeit ist eine Zier von David Kriesel auf dem 36c3](https://www.youtube.com/watch?v=0rb9CfOvojk) zu empfehlen.

Sie können diese und ähnliche Fragestellungen beantworten, oder aber auch selbst kreativ werden und eigene interessante Einblicke des Datensets aufzeigen, denn besonders spannend ist die Data Science immer, wenn unvorhersehbare Einblicke zu Tage treten.

## Aufgaben
Erstellen Sie 3-5 Visualisierungen vom Datenset. 
Gehen hierbei nach den 4 Phasen der Data Visualization vor, die wir in der Vorlesung behandelt haben.
Neben den Visualisierungen selbst, beschreiben Sie, was Sie warum gemacht haben. Also beispielsweise:
- Was sind die Rahmenbedingungen des Projekts?
- Was wollen Sie mit den Visualisierungen ausdrücken?
- Warum haben Sie sich für diese Art der Visualisierung entschieden und nicht für eine andere? 
- Wieso haben Sie die Visualisierungen so gestaltet? 
    - Farbe
    - Interaktivität
    - Darstellung

Um die Aufgabe zu lösen sollten Sie also einerseits mittels Pandas interessante Daten aggregieren und diese darüber hinaus mit Plotly, D3 oder einem anderen Visualisierungstool ihrer Wahl darstellen. Sie können sowohl einfache als auch interaktive Grafiken entwickeln. Mindestens eine der Grafiken sollte etwas aufwendiger sein. Aufwendige Grafiken aus der Vorlesung waren beispielsweise:
- Animierte Flugzeuge in D3
- Kindernamen mit interaktiven Features in D3
- Kartenmaterial mit Overlays der AirBnB Daten mit Plotly

Oberstes Bewertungskriterium ist nicht die perfekte Visualisierung, sondern das Konzept dahinter.

Die Bewertungskriterien sind unter anderem: 
- Inhalt der Dokumentation (Begründung der Designentscheidung)
- Formalia & Struktur der Dokumentation
- Qualität der Visualisierung
- Code Struktur
- Schwierigkeits- & Kommentierungsgrad


## Form
- Umfang: 3-5 Seiten Text
- 3-5 Visualisierungen, je nach Komplexität
- Abgabe: PDF und Code in Moodle hochladen
- Falls interaktive Grafiken erzeugt werden, laden Sie diese als HTML Dokumente in Moodle hoch und referenziert das auch im Text. Die interaktiven Grafiken müssen sofort funktionieren. Ich werde keine Manipulationen an den Dateien vornehmen, um diese lauffähig zu bekommen. Es sollten also beispielweise keine lokalen Daten verwendet werden. Um sich abzusichern können Sie auch mehrere Screenshots beilegen, damit eine Bewertung stattfinden kann, auch wenn die Grafik nicht funktionieren sollte.
- Abgabetermin: 16.05.2021
