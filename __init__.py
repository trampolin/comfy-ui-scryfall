from .scryfall_search_node import ScryfallSearchNode, SCRYFALL_DATA_TYPE
from .scryfall_image_extractor_node import ScryfallImageExtractorNode
from .scryfall_card_info_node import ScryfallCardInfoNode
from .scryfall_decklist_parser_node import ScryfallDecklistParserNode
# Node-Klassen für die Registrierung verfügbar machen
NODE_CLASS_MAPPINGS = {
    "ScryfallSearchNode": ScryfallSearchNode,
    "ScryfallImageExtractorNode": ScryfallImageExtractorNode,
    "ScryfallCardInfoNode": ScryfallCardInfoNode,
    "ScryfallDecklistParserNode": ScryfallDecklistParserNode,
}

# Kategorie für die Nodes definieren
NODE_DISPLAY_NAME_MAPPINGS = {
    "ScryfallSearchNode": "Scryfall Card Search",
    "ScryfallImageExtractorNode": "Scryfall Image Extractor",
    "ScryfallCardInfoNode": "Scryfall Card Info",
    "ScryfallDecklistParserNode": "Decklist Parser",
}

# Benutzerdefinierte Typen registrieren
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'SCRYFALL_DATA_TYPE']
