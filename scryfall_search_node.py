import os
import json
import urllib.parse
import requests

class ScryfallSearchNode:
    """
    ComfyUI Node für die Suche nach Magic-Karten über die Scryfall API.
    Gibt ein Datenobjekt zurück, das von anderen Nodes verwendet werden kann.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "card_name": ("STRING", {"default": "Black Lotus"}),
                "exact_match": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("SCRYFALL_DATA",)
    RETURN_NAMES = ("card_data",)
    FUNCTION = "search_card"
    CATEGORY = "Scryfall"
    
    def search_card(self, card_name, exact_match=True):
        # URL kodieren für die API-Abfrage - mit optionaler exakter Namensuche
        if exact_match:
            # Verwende die Syntax "!name" für exakte Übereinstimmung
            encoded_name = urllib.parse.quote(f'!"{card_name}"')
        else:
            # Normale Suche ohne Einschränkung auf exakten Namen
            encoded_name = urllib.parse.quote(card_name)
        
        search_url = f"https://api.scryfall.com/cards/search?q={encoded_name}"
        
        try:
            # API-Abfrage senden
            response = requests.get(search_url)
            
            # Bei Fehler mit exakter Suche versuche eine weniger strenge Suche
            if exact_match and response.status_code == 404:
                print(f"Keine exakte Übereinstimmung für '{card_name}', versuche normale Suche...")
                encoded_name = urllib.parse.quote(card_name)
                search_url = f"https://api.scryfall.com/cards/search?q={encoded_name}"
                response = requests.get(search_url)
                exact_match = False  # Setze auf False, da wir jetzt eine ungenaue Suche durchführen
            
            # Prüfen, ob auch die ungenaue Suche fehlschlägt
            if response.status_code == 404:
                print(f"Keine Karte mit dem Namen '{card_name}' gefunden.")
                # Leeres Datenobjekt mit Fehlermeldung zurückgeben
                return ({"error": f"Keine Karte gefunden: {card_name}", "found": False},)
            
            response.raise_for_status()  # Fehler werfen bei anderen HTTP-Fehlern
            data = response.json()
            
            # Überprüfen, ob Karten gefunden wurden
            if data.get("total_cards", 0) == 0:
                print(f"Keine Karten gefunden für: {card_name}")
                return ({"error": f"Keine Karte gefunden: {card_name}", "found": False},)
            
            # Erste Karte nehmen (beste Übereinstimmung)
            card = data["data"][0]
            
            # Namen der gefundenen Karte prüfen und warnen, wenn er nicht exakt übereinstimmt
            found_card_name = card.get("name", "")
            if found_card_name.lower() != card_name.lower():
                print(f"Warnung: Exakter Name '{card_name}' nicht gefunden. Stattdessen gefunden: '{found_card_name}'")
            
            # Erfolgreiche Suche
            return ({"card": card, "found": True},)
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Karte '{card_name}': {str(e)}")
            return ({"error": str(e), "found": False},)

# Definiere eigenen Typ für die Weitergabe des Suchergebnisses
# Dieser wird von ComfyUI verwendet, um gültige Verbindungen zu identifizieren
SCRYFALL_DATA_TYPE = {"SCRYFALL_DATA": ["SCRYFALL_DATA"]}
