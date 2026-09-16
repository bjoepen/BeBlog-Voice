# BeBlog Voice – Voice Contract

## Grundsatz

Die Stimme ist Produktionsmetadatum und kein Bestandteil des Manuskripts.

## Invarianten

1. Jede Render Unit besitzt eine stabile `voiceId`.
2. Genau eine registrierte Stimme besitzt die Rolle `default`.
3. `thorsten-high` ist die Default-Stimme.
4. `thorsten-hessisch` ist eine explizit auswählbare Produktionsstimme.
5. Es gibt keine automatische Humor- oder Dialekterkennung.
6. Das Manuskript enthält keine Voice-Marker.
7. Neue Stimmen müssen über die Voice Registry ergänzt werden können,
   ohne das Render-Unit-Modell zu verändern.
8. Die Voice Registry referenziert Modelle über stabile `modelRef`-Werte.
9. Physische Modellpfade sind Runtime-Konfiguration und kein Bestandteil
   des fachlichen Voice Contracts.
10. Piper-Modelldateien gehören nicht in das Git-Repository.

## Aktuelle Registry

- `thorsten-high`
  - Name: Thorsten High
  - Rolle: default

- `thorsten-hessisch`
  - Name: Thorsten Hessisch
  - Rolle: special

## Nicht Bestandteil

- automatische Voice-Auswahl
- Emotionserkennung
- Humor-Erkennung
- Voice Cloning
- Cloud-TTS
