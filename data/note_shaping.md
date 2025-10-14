## Characters and Glyphs

### Letters

ka kha ga (gha) nga
ca cha ja (jha) nya
tta ttha dda (ddha) nna
ta tha da (dha) na
pa pha ba (bha) ma
tsa tsha dza (dzha) wa
zha za xa ya ra la
sha ssa sa ha qa (kssa)
(rha) kka rra

aa i ii u uu r rr l ll e ee o oo
imir iimir

### Forms

gha -> ga.Ga.base ha.Ha.mark
jha -> ja.Ja.base ha.Ha.mark
ddha -> dda.Dda.base ha.Ha.mark
dha -> da.Da.base ha.Ha.mark
bha -> ba.Ba.base ha.Ha.mark
dzha -> dza.Dza.base ha.Ha.mark
kssa -> ka.Ka.base ssa.Ssa.mark
rha -> ra.Ra.base

ka.Ka.base ka.Ka.mark
kha.Kha.base kha.Kha.mark
ga.Ga.base ga.Ga.mark
nga.Nga.base nga.Nga.mark
ca.Ca.base ca.Ca.mark
cha.Cha.base cha.Cha.mark
ja.Ja.base ja.Ja.mark
nya.Nya.base nya.Nya.mark
tta.Tta.base tta.Tta.mark
ttha.Ttha.base ttha.Ttha.mark
dda.Dda.base dda.Dda.mark
nna.Nna.base nna.Nna.mark
ta.Ta.base ta.Ta.mark
tha.Tha.base tha.Tha.mark
da.Da.base da.Da.mark
na.Na.base na.Na.mark
pa.Pa.base pa.Pa.mark
pha.Pha.base pha.Pha.mark
ba.Ba.base ba.Ba.mark
ma.Ma.base ma.Ma.mark
tsa.Tsa.base tsa.Tsa.mark
tsha.Tsha.base tsha.Tsha.mark
dza.Dza.base dza.Dza.mark
zha.Zha.base zha.Zha.mark
za.Za.base za.Za.mark
xa.Xa.base xa.Xa.mark
wa.Wa.base wa.Wa.mark wa.Wamark.mark wa.Wamarkmirror.mark
ya.Ya.base ya.Ya.mark ya.Yamark.mark ya.Yamarkmirror.mark
ra.Ra.base ra.Ra.mark ra.Rahalf.base ra.Ramark.mark ra.Ramarkmirror.mark
la.La.base la.La.mark
sha.Sha.base sha.Sha.mark
ssa.Ssa.base ssa.Ssa.mark
sa.Sa.base sa.Sa.mark
ha.Ha.base ha.Ha.mark
qa.Qa.base qa.Qa.mark

## Features

- GSUB
  - `ccmp`: TibGlyphCompositionDecomposition
    - TibMultipleSubstitution1
  - `abvs`: TibAboveBaseSubstitutions
    - TibLigature2
    - TibChainingContext3
    - TibChainingContext4
    - TibChainingContext5
  - `blws`: TibBelowBaseSubstitutions
    - TibChainingContext6
    - TibSingleSubstitution6
    - TibChainingContext7
    - TibChainingContext8
    - TibChainingContext9
    - TibChainingContext10
    - TibLigature3
    - TibLigature4
    - TibChainingContext11
  - `psts`: TibPostBaseSubstitutions
    - TibChainingContext1
    - TibChainingContext2
- GPOS
  - `kern`: TibKerning
  - `dist`: TibDistance
  - `abvm`: TibAboveBaseMarkPositioning
  - `blwm`: TibBelowBaseMarkPositioning

### `ccmp`

**TibMultipleSubstitution1: NFKD decomposition**. Such as `gha.base` -> `ga.Ga.base` `ha.Ha.mark`, `gha.mark` -> `ga.Ga.mark` `ha.Ha.mark`.

### `abvs`

**TibLigature2: NFKC composition**. Such as `e.mark` `e.mark` -> `ee.mark`.

TibChainingContext3: Mark stacking. Such as adjusting the relative position of `i` and `camdrabindu`.

TibChainingContext4: Add dotted circle. Add dotted circle between `tsaxphru` / above-base mark (so use mark filtering set) and `tsaxphru`.

TibChainingContext5: Mark stacking. Such as adjusting the relative position of `tsaxphru` and `i`.

### `blws`

**TibChainingContext6: Ra and Rahalf**. When precedes all consonants besides nya, la, ra, wa or ya, `ra.Ra.base` -> `ra.Rahalf.base`. Note that it seems that only ra_nya situation is confirmed in the encoding document.

(Non-standard) When precedes nya, la, `rha.Ra.base` -> `ra.Rahalf.base`.

(Non-standard) `ra.Ra.base` `zwj` -> `ra.Rahalf.base`.

**TibSingleSubstitution6: rha -> ra**. `rha` completes all tasks.

TibChainingContext7: add dotted circle. Add dotted circle between below-base sign and below-base consonant (only when CCC=0, thus not for u / aa). Add dotted circle between u / aa and halanta.

**TibChainingContext8: Mirror wa and ra**. When following tta / ttha / dda / nna / ssa / kka / rra, `wa.Wamark.mark` -> `wa.Wamarkmirror.mark`, `ra.Ramark.mark` -> `ra.Ramarkmirror.mark`. Note that `ya.Yamark.mark` will not mirror, because it will not affect the mirroring of the following mark.

TibChainingContext9: Reduce the height of the glyph.

TibChainingContext10: Adjust the design of wa / ya / u. When following Wamarkmirror and Ramarkmirror, `ya.Yamark.mark` will change its start stroke to the left.

TibLigature3: Compose the glyph for aspirated consonants. Such as `ga.Ga.base` `ha.Ha.mark` -> `gha.GaHa.base`.

TibLigature4: Compose the glyph for consonants and vowels. Such as `ka.Ka.base` `aa` -> `ka_aa.KaAa.base`.

TibChainingContext11: Compose the glyph for `Rahalf`. Adjust the design of `Yamark`.

### `psts`

TibChainingContext1: Reduce dotted circle when preceding uni0F19.

TibChainingContext2: Adjust uni0F18 when following dotted circle.
