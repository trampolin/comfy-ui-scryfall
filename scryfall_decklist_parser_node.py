import logging
import csv
import io

class ScryfallDecklistParserNode:
    """
    ComfyUI node for parsing a Magic decklist from a text field.
    Expected format: '1 Cardname (SET)' or '1x Cardname [SET]' etc.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "decklist_text": ("STRING", {"multiline": True, "default": ""}),
                "index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("card_name", "edition", "used_index", "list_length")
    FUNCTION = "parse_decklist"
    CATEGORY = "Scryfall"

    def parse_decklist(self, decklist_text, index):
        logger = logging.getLogger("ScryfallDecklistParserNode")
        card_list = []
        csv_reader = csv.reader(io.StringIO(decklist_text.strip()))
        for row in csv_reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                logger.debug(f"Skipping empty row: {row}")
                continue
            if len(row) < 3:
                logger.warning(f"Could not parse row (not enough columns): {row}")
                continue
            try:
                count = int(row[0].strip().replace("x", "").replace("X", ""))
                name = row[1].strip()
                edition = row[2].strip()
                logger.info(f"Parsed row: count={count}, name='{name}', edition='{edition}'")
                # Add the card to the list 'count' times, omit 'count' in the entry
                for _ in range(count):
                    card_list.append({"name": name, "edition": edition})
            except Exception as e:
                logger.warning(f"Could not parse row: {row} ({e})")
        list_length = len(card_list)
        if card_list and 0 <= index < list_length:
            card = card_list[index]
            card_name = card["name"]
            edition = card["edition"]
        else:
            card_name = ""
            edition = ""
        return (card_name, edition, index, list_length)
