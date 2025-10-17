## Characters and Glyphs

aa i ii u uu r rr l ll e ee o oo
iMir iiMir

(gha = ga haSub, ghaSub = gaSub haSub)
(jha = ja haSub, jhaSub = jaSub haSub)
(ddha = dda haSub, ddhaSub = ddaSub haSub)
(dha = da haSub, dhaSub = daSub haSub)
(bha = ba haSub, bhaSub = baSub haSub)
(dzha = dza haSub, dzhaSub = dzaSub haSub)
(kssa = ksa haSub, kssaSub = ksaSub haSub)

(rha) kka rra

ka kaSub kha khaSub ga gaSub nga ngaSub
ca caSub cha chaSub ja jaSub nya nyaSub
tta ttaSub ttha tthaSub dda ddaSub nna nnaSub
ta taSub tha thaSub da daSub na naSub
pa paSub pha phaSub ba baSub ma maSub
tsa tsaSub tsha tshaSub dza dzaSub
zha zhaSub za zaSub xa xaSub la laSub
sha shaSub ssa ssaSub sa saSub ha haSub qa qaSub

wa waSub wataSub wataSubMir
ya yaSub yataSub yataSubMir
ra rago raSub rataSub rataSubMir

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

**TibMultipleSubstitution1: NFKD decomposition**. Such as `gha` -> `ga` `haSub`, `ghaSub` -> `gaSub` `haSub`.

### `abvs`

**TibLigature2: NFKC composition**. Such as `e` `e` -> `ee`.

TibChainingContext3: Mark stacking. Such as adjusting the relative position of `i` and `camdrabindu`.

TibChainingContext4: Add dotted circle. Add dotted circle between `tsaxphru` / above-base mark (so use mark filtering set) and `tsaxphru`.

TibChainingContext5: Mark stacking. Such as adjusting the relative position of `tsaxphru` and `i`.

### `blws`

**TibChainingContext6: Ra and Rago**. When precedes all consonants besides nya, la, ra, wa or ya, `ra` -> `rago`. Note that it seems that only ra_nya situation is confirmed in the encoding document.

(Non-standard) When precedes nya, la, `rha` -> `rago`.

(Non-standard) `ra` `zwj` -> `rago`.

**TibSingleSubstitution6: rha -> ra**. `rha` completes all tasks.

TibChainingContext7: add dotted circle. Add dotted circle between below-base sign and below-base consonant (only when CCC=0, thus not for `u` / `aa`). Add dotted circle between `u` / `aa` and `halanta`.

**TibChainingContext8: Mirror wa and ra**. When following tta / ttha / dda / nna / ssa / kka / rra, `wataSub` -> `wataSubMir`, `rataSub` -> `rataSubMir`. Note that `yataSub` will not mirror, because it will not affect the mirroring of the following mark.

TibChainingContext9: Reduce the height of the glyph.

TibChainingContext10: Adjust the design of `wa` / `ya` / `u`. When following `wataSubMir` and `rataSubMir`, `yataSub` will change its start stroke to the left.

TibLigature3: Compose the glyph for aspirated consonants. Such as `ga` `haSub` -> `ghaSub`.

TibLigature4: Compose the glyph for consonants and vowels. Such as `ka` `aa` -> `ka_aa`.

TibChainingContext11: Compose the glyph for `rago`. Adjust the design of `yataSub`.

### `psts`

TibChainingContext1: Reduce dotted circle when preceding uni0F19.

TibChainingContext2: Adjust uni0F18 when following dotted circle.
