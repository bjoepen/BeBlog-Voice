# BeBlog Voice – Proof History

## 001 – Voice & Pronunciation Contract

**Status:** FROZEN

Festgelegt wurden insbesondere:

- Thorsten High als Referenz- und Default-Stimme
- Thorsten Hessisch als auswählbare Special-/Produktionsstimme
- unveränderliches Manuskript
- getrenntes Rendertext-Modell
- geprüfte Rewrites vor IPA
- IPA ausschließlich als gezielter Fallback
- keine automatische Vollphonemisierung
- keine automatische Compound-Zerlegung

---

## 002 – Piper Proof of Contract

**Status:** PASS / FROZEN

Praktisch bewiesen:

Manuskript → Absatz → Normalizer → Pronunciation Dictionary →
Rendertext → Thorsten High → WAV

Acceptance:

- Manuskript blieb unverändert
- drei Render Units reproduzierbar
- Original- und Rendertexte getrennt
- WAV-Ausgabe erfolgreich
- Thorsten High hörgeprüft

---

## 003 – Voice-aware Render Model

**Status:** PASS / FROZEN

Praktisch bewiesen:

- stabile Voice IDs
- Voice Registry
- Voice-Auswahl als Produktionsmetadaten
- Multi-Voice-Rendering
- Thorsten High und Thorsten Hessisch innerhalb eines Manuskripts
- Rewrite und IPA im selben Workflow

Golden Audio Fixtures:

- `Linearführung` → Rewrite → `lineare Führung`
- `Montage` → IPA → `mɔnˈtaːʒə`
- `Ei verbibbsch!` → Thorsten Hessisch
- `Des werd schon widder!` → Thorsten Hessisch

Manuell hörgeprüfte Voice-Folge:

Thorsten High → Thorsten Hessisch → Thorsten Hessisch → Thorsten High

---

Die Proof-Umgebung ist experimentelle Evidenz und kein Bestandteil des
Produktcodes. BeBlog Voice 004 übernimmt ausschließlich die daraus
bestätigten Contracts.
