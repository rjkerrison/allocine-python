import json

from allocine import Allocine
from app.formatting import dumper


def get_cinemas(format="json"):
    allocine = Allocine()
    # Get cinemas in Paris
    codes = allocine.get_cinema_ids(83165)
    print(codes)
    result = [allocine.get_cinema(allocine_cinema_id=code) for code in codes]

    if format == "json":
        return json.dumps(result, default=dumper, indent=2)
    return result


if __name__ == "__main__":
    result = get_cinemas(format=None)

    with open("cinemas.json", "w") as f:
        json.dump({"cinemas": result}, f, default=dumper, indent=2)
