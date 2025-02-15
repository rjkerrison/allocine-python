#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CLI tool for allocine"""
import click
from app.main import get_showings

# Usage : seances.py --help

@click.command()
@click.argument("id_cinema", type=str, required=False)
@click.option(
    "--jour",
    "-j",
    type=str,
    help="jour des séances souhaitées \
(au format DD/MM/YYYY ou +1 pour demain), par défaut : aujourd’hui",
)
@click.option(
    "--semaine",
    "-s",
    is_flag=True,
    help="affiche les séance pour les 7 prochains jours",
)
@click.option(
    "--entrelignes",
    "-e",
    is_flag=True,
    help="ajoute une ligne entre chaque film pour améliorer la lisibilité",
)
@click.option(
    "--card",
    "-c",
    type=str,
    help="check for a specific card pass, e.g. UGC Illimité",
)
@click.option(
    "--earliest-time",
    "-f",
    type=str,
    help="filter to only shows starting after a given time",
)
@click.option(
    "--latest-time",
    "-t",
    type=str,
    help="filter to only shows ending before a given time",
)
@click.option(
    "--format",
    type=str,
    help="default, or json",
)
def main(
    id_cinema,
    entrelignes,
    jour=None,
    semaine=None,
    card=None,
    earliest_time=None,
    latest_time=None,
    format=None
):
    showings = get_showings(
        id_cinema,
        entrelignes,
        jour,
        semaine,
        card,
        earliest_time,
        latest_time,
        format
    )
    for showing in showings:
        print(showing)

if __name__ == "__main__":
    main()
