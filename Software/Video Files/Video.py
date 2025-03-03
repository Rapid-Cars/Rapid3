import os
import subprocess

def convert_mjpeg_to_mp4(input_folder, output_file):
    """
    Konvertiert alle MJPEG-Dateien im Ordner zu einer MP4-Datei.
    """
    # Alle MJPEG-Dateien im Ordner finden
    mjpeg_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mjpeg', '.mjpg'))]
    mjpeg_files = [os.path.join(input_folder, f) for f in mjpeg_files]

    if not mjpeg_files:
        print("Keine MJPEG-Dateien im angegebenen Ordner gefunden.")
        return

    # Temporäre Datei erstellen, die alle Dateien auflistet
    list_file = os.path.join(input_folder, "file_list.txt")
    with open(list_file, "w") as f:
        for file in mjpeg_files:
            f.write(f"file '{file}'\n")

    # FFmpeg-Befehl zum Zusammenfügen der Dateien
    command = [
        "ffmpeg",
        "-f", "concat",       # Format: Dateiliste
        "-safe", "0",         # Erlaube absolute Pfade in der Dateiliste
        "-i", list_file,      # Eingabedatei (Dateiliste)
        "-c", "copy",         # Codec: Direkt kopieren (keine Neuencodierung)
        output_file           # Ausgabedatei
    ]

    # FFmpeg ausführen
    try:
        subprocess.run(command, check=True)
        print(f"Die Konvertierung wurde abgeschlossen. Die Ausgabedatei ist {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Ausführung von FFmpeg: {e}")
    finally:
        # Temporäre Datei löschen
        if os.path.exists(list_file):
            os.remove(list_file)

if __name__ == "__main__":
    # Pfad zum Ordner mit den MJPEG-Dateien
    input_folder = input("Gib den Pfad zum Ordner mit den MJPEG-Dateien ein: ")

    # Überprüfen, ob der Ordner existiert
    if not os.path.isdir(input_folder):
        print(f"Der angegebene Pfad '{input_folder}' ist kein gültiger Ordner.")
        exit(1)

    # Ausgabe-MP4-Datei
    output_file = os.path.join(input_folder, "output.mp4")

    # Konvertierung durchführen
    convert_mjpeg_to_mp4(input_folder, output_file)