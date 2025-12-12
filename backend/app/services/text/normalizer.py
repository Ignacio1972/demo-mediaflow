"""
Text Normalizer Service
Normalizes text for TTS pronunciation in Chilean Spanish

Handles:
- Letter sequences (ABC → A. B. C.)
- Numbers to words (45 → cuarenta y cinco)
- Chilean license plates (BBCL-45 → B. B. C. L. cuarenta y cinco)
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Chilean Spanish number words
UNITS = {
    0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro",
    5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve",
    10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce",
    15: "quince", 16: "dieciseis", 17: "diecisiete", 18: "dieciocho",
    19: "diecinueve", 20: "veinte", 21: "veintiuno", 22: "veintidos",
    23: "veintitres", 24: "veinticuatro", 25: "veinticinco",
    26: "veintiseis", 27: "veintisiete", 28: "veintiocho", 29: "veintinueve"
}

TENS = {
    30: "treinta", 40: "cuarenta", 50: "cincuenta",
    60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"
}

HUNDREDS = {
    100: "cien", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos",
    500: "quinientos", 600: "seiscientos", 700: "setecientos",
    800: "ochocientos", 900: "novecientos"
}

# Message templates for vehicle announcements
VEHICLE_TEMPLATES = {
    "default": (
        "Atencion. El vehiculo {marca}, color {color}, "
        "patente {patente}, se encuentra mal estacionado. "
        "Por favor, retirelo de inmediato."
    ),
    "formal": (
        "Estimados usuarios. Se solicita al propietario "
        "del vehiculo {marca}, color {color}, patente {patente}, "
        "que por favor retire su vehiculo del area."
    ),
    "urgente": (
        "Atencion urgente. El vehiculo {marca}, "
        "color {color}, patente {patente}, esta bloqueando el acceso. "
        "Retirelo inmediatamente por favor."
    ),
    "amable": (
        "Estimado cliente. Le informamos que su vehiculo {marca}, "
        "color {color}, patente {patente}, necesita ser reubicado. "
        "Agradecemos su colaboracion."
    ),
}


class TextNormalizer:
    """
    Normalizes text for TTS pronunciation in Chilean Spanish.

    Converts letters, numbers, and license plates to pronunciation-friendly
    formats that TTS engines can correctly vocalize.
    """

    def __init__(self):
        """Initialize the normalizer."""
        self.templates = VEHICLE_TEMPLATES.copy()

    def normalize_letters(self, text: str, separator: str = ". ") -> str:
        """
        Convert letter sequences to TTS-friendly format.

        Args:
            text: String of letters (e.g., "ABC")
            separator: Separator between letters (default: ". ")

        Returns:
            Spaced letters (e.g., "A. B. C.")

        Example:
            >>> normalizer.normalize_letters("BBCL")
            "B. B. C. L."
        """
        if not text:
            return ""

        # Extract only letters and convert to uppercase
        letters = [char.upper() for char in text if char.isalpha()]

        if not letters:
            return ""

        # Join with separator and add final period
        result = separator.join(letters)
        if not result.endswith("."):
            result += "."

        return result

    def _number_to_words_under_100(self, n: int) -> str:
        """Convert number under 100 to Spanish words."""
        if n < 0:
            return "menos " + self._number_to_words_under_100(abs(n))

        if n <= 29:
            return UNITS.get(n, str(n))

        if n < 100:
            tens = (n // 10) * 10
            units = n % 10
            if units == 0:
                return TENS[tens]
            return f"{TENS[tens]} y {UNITS[units]}"

        return str(n)

    def _number_to_words_under_1000(self, n: int) -> str:
        """Convert number under 1000 to Spanish words."""
        if n < 100:
            return self._number_to_words_under_100(n)

        if n == 100:
            return "cien"

        hundreds = (n // 100) * 100
        remainder = n % 100

        if remainder == 0:
            return HUNDREDS[hundreds]

        # "ciento" for 100-199
        hundreds_word = "ciento" if hundreds == 100 else HUNDREDS[hundreds]
        return f"{hundreds_word} {self._number_to_words_under_100(remainder)}"

    def number_to_words(self, n: int) -> str:
        """
        Convert integer to Spanish words.

        Args:
            n: Integer to convert (0-9999 supported)

        Returns:
            Spanish word representation

        Example:
            >>> normalizer.number_to_words(45)
            "cuarenta y cinco"
            >>> normalizer.number_to_words(1234)
            "mil doscientos treinta y cuatro"
        """
        if n < 0:
            return "menos " + self.number_to_words(abs(n))

        if n < 1000:
            return self._number_to_words_under_1000(n)

        if n < 10000:
            thousands = n // 1000
            remainder = n % 1000

            if thousands == 1:
                thousands_word = "mil"
            else:
                thousands_word = f"{UNITS[thousands]} mil"

            if remainder == 0:
                return thousands_word

            return f"{thousands_word} {self._number_to_words_under_1000(remainder)}"

        # For larger numbers, just return the string
        return str(n)

    def normalize_number(self, number_str: str, mode: str = "words") -> str:
        """
        Convert number string to TTS-friendly format.

        Args:
            number_str: Number as string (e.g., "45")
            mode: "words" for full words, "digits" for digit-by-digit

        Returns:
            Normalized number string

        Example:
            >>> normalizer.normalize_number("45", mode="words")
            "cuarenta y cinco"
            >>> normalizer.normalize_number("45", mode="digits")
            "cuatro cinco"
        """
        if not number_str:
            return ""

        # Extract digits only
        digits = "".join(c for c in number_str if c.isdigit())

        if not digits:
            return ""

        if mode == "digits":
            # Digit by digit pronunciation
            return " ".join(UNITS[int(d)] for d in digits)

        # Full word conversion
        try:
            n = int(digits)
            return self.number_to_words(n)
        except ValueError:
            return digits

    def normalize_plate(self, plate: str, number_mode: str = "words") -> str:
        """
        Normalize Chilean license plate for TTS pronunciation.

        Supports formats:
        - New format (2007+): XXXX-YY (4 letters + 2 digits) e.g., "BBCL-45"
        - Old format: XX-YYYY (2 letters + 4 digits) e.g., "AA-1234"

        Args:
            plate: License plate string
            number_mode: "words" for full words (cuarenta y cinco),
                        "digits" for digit-by-digit (cuatro cinco)

        Returns:
            TTS-friendly pronunciation

        Example:
            >>> normalizer.normalize_plate("BBCL-45")
            "B. B. C. L. cuarenta y cinco"
            >>> normalizer.normalize_plate("AA-1234", number_mode="digits")
            "A. A. uno dos tres cuatro"
        """
        if not plate:
            return ""

        # Clean the plate: remove spaces, dashes, convert to uppercase
        clean_plate = plate.upper().replace(" ", "").replace("-", "")

        # Separate letters and numbers
        letters = ""
        numbers = ""

        for char in clean_plate:
            if char.isalpha():
                letters += char
            elif char.isdigit():
                numbers += char

        # Normalize each part
        letters_normalized = self.normalize_letters(letters)
        numbers_normalized = self.normalize_number(numbers, mode=number_mode)

        # Combine parts
        parts = []
        if letters_normalized:
            parts.append(letters_normalized)
        if numbers_normalized:
            parts.append(numbers_normalized)

        return " ".join(parts)

    def validate_plate_format(self, plate: str) -> dict:
        """
        Validate and identify Chilean license plate format.

        Args:
            plate: License plate string

        Returns:
            Dict with format info and validity

        Example:
            >>> normalizer.validate_plate_format("BBCL-45")
            {"valid": True, "format": "new", "letters": "BBCL", "numbers": "45"}
        """
        if not plate:
            return {"valid": False, "error": "Patente vacia"}

        clean_plate = plate.upper().replace(" ", "").replace("-", "")

        # Extract letters and numbers
        letters = "".join(c for c in clean_plate if c.isalpha())
        numbers = "".join(c for c in clean_plate if c.isdigit())

        # Validate new format: 4 letters + 2 digits (most common now)
        if len(letters) == 4 and len(numbers) == 2:
            return {
                "valid": True,
                "format": "new",
                "letters": letters,
                "numbers": numbers,
                "normalized": f"{letters[:2]}{letters[2:]}-{numbers}"
            }

        # Validate old format: 2 letters + 4 digits
        if len(letters) == 2 and len(numbers) == 4:
            return {
                "valid": True,
                "format": "old",
                "letters": letters,
                "numbers": numbers,
                "normalized": f"{letters}-{numbers}"
            }

        # Partial match - still usable
        if letters or numbers:
            return {
                "valid": True,
                "format": "custom",
                "letters": letters,
                "numbers": numbers,
                "warning": "Formato no estandar"
            }

        return {"valid": False, "error": "Formato de patente no reconocido"}

    def normalize_vehicle_announcement(
        self,
        marca: str,
        color: str,
        patente: str,
        template: str = "default",
        number_mode: str = "words"
    ) -> dict:
        """
        Generate normalized vehicle announcement text for TTS.

        Args:
            marca: Vehicle brand (e.g., "Toyota")
            color: Vehicle color (e.g., "rojo")
            patente: License plate (e.g., "BBCL-45")
            template: Template name ("default", "formal", "urgente", "amable")
            number_mode: "words" or "digits" for plate number pronunciation

        Returns:
            Dict with original and normalized text

        Example:
            >>> normalizer.normalize_vehicle_announcement("Toyota", "rojo", "BBCL-45")
            {
                "original": "...patente BBCL-45...",
                "normalized": "...patente B. B. C. L. cuarenta y cinco...",
                "template_used": "default"
            }
        """
        # Get template
        template_text = self.templates.get(template, self.templates["default"])

        # Normalize the license plate
        patente_normalized = self.normalize_plate(patente, number_mode=number_mode)

        # Generate original text (with raw plate)
        original_text = template_text.format(
            marca=marca,
            color=color,
            patente=patente.upper()
        )

        # Generate normalized text (with TTS-friendly plate)
        normalized_text = template_text.format(
            marca=marca,
            color=color,
            patente=patente_normalized
        )

        # Validate plate format
        plate_info = self.validate_plate_format(patente)

        return {
            "original": original_text,
            "normalized": normalized_text,
            "template_used": template,
            "plate_info": plate_info,
            "components": {
                "marca": marca,
                "color": color,
                "patente_original": patente.upper(),
                "patente_normalized": patente_normalized
            }
        }

    def get_available_templates(self) -> list:
        """
        Get list of available message templates.

        Returns:
            List of template info dicts
        """
        return [
            {
                "id": "default",
                "name": "Estandar",
                "description": "Anuncio estandar de vehiculo mal estacionado"
            },
            {
                "id": "formal",
                "name": "Formal",
                "description": "Tono formal y respetuoso"
            },
            {
                "id": "urgente",
                "name": "Urgente",
                "description": "Para situaciones de bloqueo urgente"
            },
            {
                "id": "amable",
                "name": "Amable",
                "description": "Tono amigable y cordial"
            }
        ]


# Singleton instance for easy imports
text_normalizer = TextNormalizer()
