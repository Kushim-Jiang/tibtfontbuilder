from utils import tempDir, testsDir
from ufoLib2 import Font
from src.otl import TibtFeaComposer
from src.lib_.spec import applySpecToFont

input = testsDir / "tibetan.ufo"
output = tempDir / "tibetan.ufo"

font = Font.open(input)
c = TibtFeaComposer(cmap={j: i for i in font.keys() for j in font[i].unicodes}, glyphs=[*font.keys()])
spec = c.compose()
applySpecToFont(spec, font)
font.features.text = c.asFeatureFile().asFea()

output.parent.mkdir(parents=True, exist_ok=True)
font.save(output, overwrite=True)
