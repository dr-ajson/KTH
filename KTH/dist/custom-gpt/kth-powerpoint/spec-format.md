# Specifikation för bygg_presentation.py

```json
{
  "titel": "Presentationens titel (dokumentegenskaper)",
  "sidfot": "Text i sidfoten, t.ex. enhet eller evenemang",
  "bildnummer": true,
  "sprak": "sv-SE",
  "bilder": [ { "layout": "...", "rubrik": "...", ... } ]
}
```

Sidfot och bildnummer läggs på alla bilder utom titel- och logobilder.

## Layouter och fält

| layout | Används till | Fält |
|---|---|---|
| `titel`, `titel-marin`, `titel-bild` | Första bilden | rubrik, underrubrik |
| `kapitel`, `kapitel-sand`, `kapitel-kthbla`, `kapitel-marin` | Avsnittsbrytning | rubrik, text |
| `kapitel-bild`, `kapitel-bild-sand`, `kapitel-bild-kthbla`, `kapitel-bild-marin` | Avsnitt med bild till höger | rubrik, text, bild |
| `innehall` (standard), `innehall-bla-linjer`, `innehall-sand-linjer`, `innehall-ljusbla`, `innehall-sand`, `innehall-topp` | Rubrik och punkter | rubrik, text |
| `tva-delar` | Två spalter | rubrik, vanster, hoger |
| `tva-delar-underrubrik` | Två spalter med egna rubriker | rubrik, vanster_rubrik, vanster, hoger_rubrik, hoger |
| `jamforelse`, `-sand`, `-kthbla`, `-marin`, `-gron`, `-turkos`, `-rod`, `-gul` | Före/efter, två alternativ. Högra halvan har färgad bakgrund | rubrik (vänster), vanster, hoger_rubrik, hoger |
| `text-och-bild` | Text vänster, bild höger | rubrik, text, bild |
| `bild`, `tva-bilder`, `tre-bilder`, `fyra-bilder` | Bildsidor | rubrik, bilder (lista), bildtexter (lista, för layouterna "..., text") |
| `rubrik`, `rubrik-ljusbla`, `rubrik-sand` | Bara rubrik (t.ex. innan du lägger in diagram) | rubrik |
| `logga`, `logga-marin` | Avslutande bild | – |
| `tom` | Helt tom | – |

Alla layoutnamn i mallen går också att ange direkt (t.ex. `"Headline and 2 images, text"`). Kör `--layouter` för listan.

Vanliga fält på alla bilder: `anteckningar` (talarmanus).

## Text

`text`, `vanster` och `hoger` tar antingen en sträng eller en lista. I strängar blir rader som börjar med `- ` punkter (två mellanslag in = nivå 2), och övriga rader blir löptext utan punkt. `**fet**` och `*kursiv*` fungerar.

## Bilder

`bild` är en sökväg eller `{"fil": "foto.jpg", "alt": "Beskrivning för skärmläsare"}`. Ange alltid `alt` för bilder som bär information. Bilden beskärs automatiskt för att fylla platshållaren; justera beskärningen i PowerPoint vid behov.
