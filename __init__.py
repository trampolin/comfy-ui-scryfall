from .scryfall_search_node import ScryfallSearchNode, SCRYFALL_DATA_TYPE
from .scryfall_image_extractor_node import ScryfallImageExtractorNode
from .scryfall_card_info_node import ScryfallCardInfoNode

# Node-Klassen für die Registrierung verfügbar machen
NODE_CLASS_MAPPINGS = {
    "ScryfallSearchNode": ScryfallSearchNode,
    "ScryfallImageExtractorNode": ScryfallImageExtractorNode,
    "ScryfallCardInfoNode": ScryfallCardInfoNode,
}

# Kategorie für die Nodes definieren
NODE_DISPLAY_NAME_MAPPINGS = {
    "ScryfallSearchNode": "Scryfall Card Search",
    "ScryfallImageExtractorNode": "Scryfall Image Extractor",
    "ScryfallCardInfoNode": "Scryfall Card Info",
}

# Benutzerdefinierte Typen registrieren
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'SCRYFALL_DATA_TYPE']


