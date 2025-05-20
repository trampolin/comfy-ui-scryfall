import urllib.parse
import requests
import logging

class ScryfallSearchNode:
    """
    ComfyUI node for searching Magic cards via the Scryfall API.
    Returns a data object that can be used by other nodes.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "card_name": ("STRING", {"default": "Black Lotus"}),
                "exact_match": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "edition": ("STRING", {"default": ""}),  # Optional input for Magic edition
            }
        }
    
    RETURN_TYPES = ("SCRYFALL_DATA",)
    RETURN_NAMES = ("card_data",)
    FUNCTION = "search_card"
    CATEGORY = "Scryfall"
    
    def _build_search_url(self, card_name, edition, exact_match):
        if exact_match:
            encoded_name = urllib.parse.quote(f'!"{card_name}"')
        else:
            encoded_name = urllib.parse.quote(card_name)
        url = f"https://api.scryfall.com/cards/search?q={encoded_name}"
        if edition:
            encoded_edition = urllib.parse.quote(edition)
            url += f"+set:{encoded_edition}"
        return url

    def search_card(self, card_name, edition, exact_match=True):
        logger = logging.getLogger("ScryfallSearchNode")
        search_url = self._build_search_url(card_name, edition, exact_match)
        try:
            response = requests.get(search_url)
            
            # On error with exact search, try a less strict search
            if exact_match and response.status_code == 404:
                logger.info(f"No exact match for '{card_name}', trying normal search...")
                search_url = self._build_search_url(card_name, edition, False)
                response = requests.get(search_url)
                exact_match = False  # Set to False since we are now doing a fuzzy search
            
            # Check if fuzzy search also fails
            if response.status_code == 404:
                logger.warning(f"No card found with the name '{card_name}'.")
                # Return empty data object with error message
                return ({"error": f"No card found: {card_name}", "found": False},)
            
            response.raise_for_status()  # Raise error for other HTTP errors
            data = response.json()
            
            # Check if any cards were found
            if not data.get("data"):
                logger.warning(f"No cards found for: {card_name}")
                return ({"error": f"No card found: {card_name}", "found": False},)
            
            # Take the first card (best match)
            card = data["data"][0]
            
            # Check the name of the found card and warn if it does not match exactly
            found_card_name = card.get("name", "")
            if found_card_name.lower() != card_name.lower():
                logger.warning(f"Exact name '{card_name}' not found. Found instead: '{found_card_name}'")
            
            # Successful search
            return ({"card": card, "found": True},)
            
        except Exception as e:
            logger.error(f"Error fetching card '{card_name}': {str(e)}")
            return ({"error": str(e), "found": False},)

# Define custom type for passing the search result
# This is used by ComfyUI to identify valid connections
SCRYFALL_DATA_TYPE = {"SCRYFALL_DATA": ["SCRYFALL_DATA"]}

