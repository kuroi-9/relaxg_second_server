import re
from ..models import Book

def sort_key(book: Book):
    name = book.name if hasattr(book, 'name') else book

    num_match = re.search(r'\b(v(\d+)|(\d+))\b', name)
    year_match = re.search(r'\((\d{4})\)', name)
    is_extra = bool(re.search(r'extra', name, re.IGNORECASE))

    year = int(year_match.group(1)) if year_match else 9999

    # Volumes : toujours en premier, triés par numéro
    if num_match and num_match.group(2) is not None:
        number = int(num_match.group(2))
        return (0, 0, number)

    # Chapitres et extras : triés par date
    if year == 9999:
        # Pas de date → à la fin
        return (2, 0, 0)

    if num_match:
        # Chapitre numéroté
        number = int(num_match.group(3))
        return (1, year, number)
    else:
        # Extra avec date
        return (1, year, 0)
