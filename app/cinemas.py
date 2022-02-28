
import json

from allocine import Allocine
from app.formatting import dumper

def get_cinemas(format='json'):
    allocine = Allocine()
    # Get cinemas in Paris
    codes = allocine.get_cinema_ids(83165)
    result = [allocine.get_cinema(allocine_cinema_id=code) for code in codes]

    if format == 'json':
        return json.dumps(result, default=dumper, indent=2)
    return result
