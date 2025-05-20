import os
import folder_paths

class ScryfallCardInfoNode:
    """
    ComfyUI Node zum Extrahieren verschiedener Informationen aus Scryfall-Kartendaten.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "card_data": ("SCRYFALL_DATA",),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("card_name", "mana_cost", "type_line", "oracle_text", "flavor_text")
    FUNCTION = "extract_card_info"
    CATEGORY = "Scryfall"
    
    def extract_card_info(self, card_data):
        # Prüfen, ob eine Karte gefunden wurde
        if not card_data.get("found", False):
            error_message = card_data.get("error", "Unbekannter Fehler")
            # Rückgabe: Fehlermeldung für alle String-Outputs
            return (error_message, "", "", "", "")
        
        # Kartendaten extrahieren
        card = card_data["card"]
        
        # Basis-Informationen
        card_name = card.get("name", "")
        mana_cost = card.get("mana_cost", "")
        type_line = card.get("type_line", "")
        oracle_text = card.get("oracle_text", "")
        flavor_text = card.get("flavor_text", "")
        
        # Prüfen auf doppelseitige Karten
        if "card_faces" in card and not oracle_text:
            # Bei doppelseitigen Karten Informationen von der ersten Seite nehmen
            face = card["card_faces"][0]
            if not mana_cost:
                mana_cost = face.get("mana_cost", "")
            if not type_line:
                type_line = face.get("type_line", "")
            if not oracle_text:
                oracle_text = face.get("oracle_text", "")
            if not flavor_text:
                flavor_text = face.get("flavor_text", "")
        
        return (card_name, mana_cost, type_line, oracle_text, flavor_text)
