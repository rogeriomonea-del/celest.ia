from enum import Enum

class Mode(str, Enum):
    HTTP = "http"
    SELENIUM = "selenium"

# Priors por fonte (ajuste contínuo via telemetria)
SOURCE_PRIORS: dict[str, list[Mode]] = {
    "latam":         [Mode.SELENIUM, Mode.HTTP],
    "azul":          [Mode.SELENIUM, Mode.HTTP],
    "smiles":        [Mode.SELENIUM, Mode.HTTP],
    "connectmiles":  [Mode.SELENIUM, Mode.HTTP],
    "gol":           [Mode.HTTP, Mode.SELENIUM],
    "livelo":        [Mode.HTTP, Mode.SELENIUM],
    "skyscanner":    [Mode.HTTP, Mode.SELENIUM],
    "googleflights": [Mode.HTTP, Mode.SELENIUM],
    "azulpelomundo": [Mode.HTTP, Mode.SELENIUM],
    "awardhacker":   [Mode.HTTP],
}
