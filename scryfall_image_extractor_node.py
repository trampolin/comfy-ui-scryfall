import os
import numpy as np
import torch
import folder_paths
from PIL import Image
from io import BytesIO
import requests

class ScryfallImageExtractorNode:
    """
    ComfyUI Node zum Extrahieren von Bildern aus Scryfall-Kartendaten.
    Nimmt ein SCRYFALL_DATA-Objekt und gibt die Kartenbilder zurück.
    """
    
    def __init__(self):
        self.output_dir = os.path.join(folder_paths.get_output_directory(), "scryfall_card_images")
        os.makedirs(self.output_dir, exist_ok=True)
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "card_data": ("SCRYFALL_DATA",),
                "save_images": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("full_card_image", "art_crop_image", "border_crop_image", "card_name")
    FUNCTION = "extract_images"
    CATEGORY = "Scryfall"
    
    def extract_images(self, card_data, save_images=True):
        # Prüfen, ob eine Karte gefunden wurde
        if not card_data.get("found", False):
            error_message = card_data.get("error", "Unbekannter Fehler")
            # Platzhalterbild für alle drei Outputs erstellen
            placeholder = self.create_placeholder_image(error_message)
            placeholder_tensor = self.pil_to_tensor(placeholder)
            # Rückgabe: Platzhalterbilder und Fehlermeldung als Kartenname
            return (placeholder_tensor, placeholder_tensor, placeholder_tensor, error_message)
        
        # Kartendaten extrahieren
        card = card_data["card"]
        card_name = card.get("name", "Unbekannte Karte")
        
        # Bildnamen für Speicherung vorbereiten
        safe_card_name = card_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        # Prüfen, ob die Karte Bilder hat
        if "image_uris" not in card:
            # Manche Karten haben mehrere Gesichter
            if "card_faces" in card and len(card["card_faces"]) > 0:
                # Nehme das erste Gesicht der Karte
                face = card["card_faces"][0]
                if "image_uris" in face:
                    image_uris = face["image_uris"]
                else:
                    print(f"Keine Bilder für diese Karte gefunden: {card_name}")
                    placeholder = self.create_placeholder_image(f"Keine Bilder für: {card_name}")
                    placeholder_tensor = self.pil_to_tensor(placeholder)
                    return (placeholder_tensor, placeholder_tensor, placeholder_tensor, card_name)
            else:
                print(f"Keine Bilder für diese Karte gefunden: {card_name}")
                placeholder = self.create_placeholder_image(f"Keine Bilder für: {card_name}")
                placeholder_tensor = self.pil_to_tensor(placeholder)
                return (placeholder_tensor, placeholder_tensor, placeholder_tensor, card_name)
        else:
            image_uris = card["image_uris"]
        
        # Bilder-URLs abrufen
        full_image_url = image_uris.get("large")
        art_crop_url = image_uris.get("art_crop")
        border_crop_url = image_uris.get("border_crop")
        
        # Vollbild herunterladen
        full_image = self.download_image(full_image_url)
        if full_image is None:
            print(f"Fehler beim Herunterladen des vollen Bildes für: {card_name}")
            placeholder = self.create_placeholder_image(f"Bild-Download fehlgeschlagen: {card_name}")
            placeholder_tensor = self.pil_to_tensor(placeholder)
            return (placeholder_tensor, placeholder_tensor, placeholder_tensor, card_name)
        
        # Art Crop herunterladen
        art_crop_image = self.download_image(art_crop_url)
        if art_crop_image is None:
            art_crop_image = self.create_placeholder_image(f"Art-Crop nicht verfügbar: {card_name}")
        
        # Border Crop herunterladen
        border_crop_image = self.download_image(border_crop_url)
        if border_crop_image is None:
            border_crop_image = self.create_placeholder_image(f"Border-Crop nicht verfügbar: {card_name}")
        
        # In Tensoren umwandeln
        full_image_tensor = self.pil_to_tensor(full_image)
        art_crop_tensor = self.pil_to_tensor(art_crop_image)
        border_crop_tensor = self.pil_to_tensor(border_crop_image)
        
        # Optional: Bilder speichern
        if save_images:
            full_image_path = os.path.join(self.output_dir, f"{safe_card_name}_full.png")
            art_crop_path = os.path.join(self.output_dir, f"{safe_card_name}_art_crop.png")
            border_crop_path = os.path.join(self.output_dir, f"{safe_card_name}_border_crop.png")
            full_image.save(full_image_path)
            art_crop_image.save(art_crop_path)
            border_crop_image.save(border_crop_path)
            print(f"Bilder für '{card_name}' erfolgreich gespeichert.")
        
        return (full_image_tensor, art_crop_tensor, border_crop_tensor, card_name)
    
    def download_image(self, url):
        """Lädt ein Bild von der gegebenen URL herunter und gibt es als PIL Image zurück."""
        if not url:
            return None
            
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        except Exception as e:
            print(f"Fehler beim Herunterladen des Bildes von {url}: {str(e)}")
            return None
    
    def pil_to_tensor(self, pil_image):
        """Konvertiert ein PIL-Bild in das von ComfyUI erwartete Tensor-Format [1, H, W, 3]."""
        img_array = np.array(pil_image).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array)
        img_tensor = img_tensor.unsqueeze(0)  # Batch-Dimension hinzufügen [1, H, W, 3]
        return img_tensor
    
    def create_placeholder_image(self, text):
        """Erstellt ein Platzhalterbild mit Text."""
        # Bildgröße für Magic-Karten-Verhältnis (63 x 88 mm)
        width, height = 400, 560
        
        # Bild erstellen mit grauem Hintergrund
        image = Image.new('RGB', (width, height), color=(200, 200, 200))
        
        # Text vorbereiten
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        # Versuche, eine Schriftart zu laden oder verwende die Standardschriftart
        try:
            # Versuche zuerst System-Schriftarten
            system_fonts = [
                "arial.ttf", "Arial.ttf",  # Windows
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "/System/Library/Fonts/Helvetica.ttc"  # macOS
            ]
            
            font = None
            for font_path in system_fonts:
                try:
                    font = ImageFont.truetype(font_path, 24)
                    break
                except IOError:
                    continue
                
            if font is None:
                # Fallback auf Standardschriftart
                font = ImageFont.load_default()
                
        except Exception:
            # Bei Problemen mit Schriftarten: Standardschriftart verwenden
            font = ImageFont.load_default()
        
        # Text in mehrere Zeilen aufteilen, wenn er zu lang ist
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Geschätzte Breite für einen einfachen Ansatz
            if len(test_line) > 30:  # ca. 30 Zeichen pro Zeile
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Text zentriert zeichnen
        y_position = height // 2 - len(lines) * 15  # Ungefähre Positionierung
        for line in lines:
            # Textbreite für Zentrierung berechnen
            try:
                text_width = draw.textlength(line, font=font)
            except (AttributeError, TypeError):
                # Fallback für ältere PIL-Versionen
                text_width = font.getsize(line)[0]
                
            x_position = (width - text_width) // 2
            draw.text((x_position, y_position), line, fill=(0, 0, 0), font=font)
            y_position += 30
        
        return image
