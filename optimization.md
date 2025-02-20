# Wartezeit der Kunden minimieren

- Anzahl der Service Agents: Je mehr, desto schneller wird der Kunde bedient
- Zubereitungszeit der Speisen: Je kürzer, desto schneller kann gegessen werden
- Sortierung der Service-Agent-Reihenfolge (Gewichtung Profit, Anzahl der Personen, übrige Zeit)

# Gewinn des Restaurants maximieren

- Anzahl der Service Agents: Je weniger, desto mehr Profit
- Preis der Speisen: Je höher, desto mehr Gewinn -> skaliert unendlich
- Reduktion der Wartezeit: Je weniger Wartzeit, desto bessere Bewertung, desto mehr Kunden, desto mehr Gewinn


# Optimizer

## Entscheidungsvariablen
- sind die immer änderbar oder können das auch aus "nur auslesbare" Werte sein (Zahl der letzten Bewertungen)?

### Minimierung Wartezeit durch Anpassung der Kundenreihenfolge im Service Agent
- Gewichtung Profit
- Gewichtung Anzahl der Personen
- Gewichtung verbleibende Zeit

<!-- ### Maximierung Gewinn im Manager Agent ?
- Preise
- Anzahl der Service Agents  
  &rarr; Skalierbar im Manager via Prognose + aktueller Profit -->


## Zielfunktion
- global (übergreifend) vs. nach x Steps
  - global: 1 kompletter Run der Simulation
  - nach x Steps: 1 Gesamt-Run, nach x Steps Anpassung der Konfiguration