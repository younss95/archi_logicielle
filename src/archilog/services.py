import csv
import dataclasses
import io

from archilog.models import create_entry, get_all_entries, Entry


def export_to_csv() -> io.StringIO:
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # ecriture de l'entete du fichier csv
    csv_writer.writerow(["id", "name", "amount", "category"])

    for todo in get_all_entries():
        #on récupère les attributs manuellement
        csv_writer.writerow([todo.id, todo.name, todo.amount, todo.category])

    return output


def import_from_csv(csv_file) -> None:
    # Convertir le fichier téléchargé en StringIO
    file_stream = io.StringIO(csv_file.read().decode("utf-8"))

    # Lire le fichier CSV
    csv_reader = csv.DictReader(file_stream)
    for row in csv_reader:
        create_entry(
            name=row["name"],
            amount=float(row["amount"]),
            category=row["category"]
        )