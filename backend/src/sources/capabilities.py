from enum import Enum

class Mode(str, Enum):
    HTTP = "http"
    SELENIUM = "selenium"

SOURCE_PRIORS: dict[str, list[Mode]] = {
    "latam":         [Mode.SELENIUM, Mode.HTTP],
    "azul":          [Mode.SELENIUM, Mode.HTTP],
    "smiles":        [Mode.SELENIUM, Mode.HTTP],
    "skyscanner":    [Mode.HTTP, Mode.SELENIUM],
    "googleflights": [Mode.HTTP, Mode.SELENIUM],
    "azulpelomundo": [Mode.HTTP, Mode.SELENIUM],
    "awardhacker":   [Mode.HTTP],
    "gol":           [Mode.HTTP, Mode.SELENIUM],
    "connectmiles":  [Mode.SELENIUM, Mode.HTTP],
    "copa":          [Mode.HTTP, Mode.SELENIUM],
    "livelo":        [Mode.HTTP, Mode.SELENIUM],
}
