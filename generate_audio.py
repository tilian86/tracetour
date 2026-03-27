#!/usr/bin/env python3
"""
TraceTour Audio Generator -- ElevenLabs TTS
v5 -- 16 Stationen, 1869 Story, Vollvertonung

Generiert alle Audio-Dateien fuer die 16 Stationen:
  Raetsel-Stationen (0,2,4,6,9,10,13,15):
    - story_X.mp3   (Erzaehler-Stimme)
    - diary_X.mp3   (Heinrichs Stimme)
    - fact_X.mp3    (Fakten-Stimme)
  Anekdoten-Stationen (1,3,5,7,8,11,12,14):
    - anecdote_X.mp3 (Fakten-Stimme)

Verwendung:
  1. pip3 install elevenlabs
  2. python3 generate_audio.py
     python3 generate_audio.py --station 0,1,2
     python3 generate_audio.py --only story,diary
     python3 generate_audio.py --list-voices
"""

import os
import sys
import time
from pathlib import Path

try:
    from elevenlabs import ElevenLabs
except ImportError:
    print("ElevenLabs SDK nicht installiert!")
    print("   pip3 install elevenlabs")
    sys.exit(1)

# ============================================================
# KONFIGURATION
# ============================================================

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_b3fb3495ab6b2c2a3a9959d20e6a4ae0a29dce88a442c410")

NARRATOR_VOICE = "WHaUUVTDq47Yqc9aDbkH"   # Story-Stimme (gleich wie vorher)
HEINRICH_VOICE = "2OcnG4mH3jIMtWz3vKus"   # Tagebuch-Stimme (gleich wie vorher)
FACT_VOICE     = "PhufIH7nYh2Up1uej6aY"   # Stadtfuehrer-Stimme (gleich wie vorher)

MODEL_ID = "eleven_multilingual_v2"
OUTPUT_DIR = Path(__file__).parent / "audio"

# ============================================================
# ALLE TEXTE DER 16 STATIONEN
# ============================================================

STATIONS = [
    # 0 - Schloss Hohentuebingen (Raetsel)
    {
        "name": "Station 0 - Schloss Hohentuebingen",
        "type": "raetsel",
        "story": (
            "Das Schloss Hohentübingen - dein Ausgangspunkt. Von hier oben überblickst du "
            "die gesamte Altstadt. Gaslaternen flackern in den Gassen unter dir. "
            "Es ist November 1869, kurz vor Einbruch der Nacht.\n\n"
            "In den Kellergewölben des Schlosses hatte Professor Heinrich von Calw sein Labor. "
            "Drei Jahre lang forschte er hier offiziell an 'chemischen Grundlagen' für das "
            "Königliche Ministerium unter König Karl dem Ersten. In Wahrheit arbeitete er an einer "
            "Energie-Formel, die alles verändern könnte - Industrie, Kriegsführung, die gesamte "
            "Ordnung der Macht.\n\n"
            "Vor einer Stunde erreichte ihn ein Telegramm: 'Gendarmen unterwegs. Verlassen Sie "
            "das Labor. Sofort.' Heinrich zündete seine Notizen an, stopfte das Manuskript in "
            "seinen Mantel und floh die steile Burgsteige hinab. Du stehst jetzt dort, wo alles begann."
        ),
        "diary": (
            "Dies ist mein letzter Eintrag in diesem Labor. Der Geruch verbrannten Papiers hängt "
            "noch in der Luft. Drei Jahre Forschung - und alles, was bleibt, ist ein einziges "
            "Manuskript unter meinem Mantel.\n\n"
            "Das Ministerium will meine Formel für Waffen. Ich habe drei Jahre gelogen, verzögert, "
            "abgelenkt. Jetzt ist die Zeit abgelaufen. Die Gendarmen sind unterwegs. "
            "Ich werde Fragmente meiner Forschung an verschiedenen Orten der Stadt verstecken - "
            "für den Fall, dass jemand Würdiges sie findet. Der erste Hinweis bleibt hier, am Tor."
        ),
        "fact": (
            "Wusstest du? Im Keller des Schlosses befindet sich das aelteste Weinfass der Welt von "
            "1549 mit 84.000 Litern Fassungsvermoegen. Die Universitaet nutzte das Schloss bis ins "
            "20. Jahrhundert als Laborgebaeude - Friedrich Miescher entdeckte hier 1869 die DNA! "
            "Ausserdem fand man in den Gewoelben die Vogelherd-Figuren: 40.000 Jahre alte "
            "Elfenbeinschnitzereien, die aeltesten bekannten Kunstwerke der Menschheit."
        ),
    },

    # 1 - Studentenkarzer (Anekdote)
    {
        "name": "Station 1 - Studentenkarzer",
        "type": "anekdote",
        "anecdote": (
            "Auf dem Weg bergab passierst du den Studentenkarzer in der Münzgasse 20 - "
            "das Universitätsgefängnis, in das Tübinger Studenten seit 1515 gesperrt wurden. "
            "Der älteste erhaltene Uni-Karzer Deutschlands.\n\n"
            "Heinrich kannte den Karzer gut. Als Student saß er hier zwei Nächte wegen 'Nachtwandeln' - "
            "er war nachts heimlich im Labor geblieben. Die Zellen sind winzig: zwei verbundene Räume "
            "mit zusammen 15 Quadratmetern und kleinen Fensteröffnungen. Die Wände sind übersät "
            "mit Inschriften und Zeichnungen der Insassen seit dem 16. Jahrhundert.\n\n"
            "Vergehen, die zum Karzer führten: Nachtwandeln, das Tragen 'absichtlich neumodisch "
            "geschlitzter Kleidung', unautorisierte Eheschließungen und Glücksspiel. Der Karzer "
            "war bis 1845 in Betrieb - also gerade noch zu Heinrichs Studentenzeit.\n\n"
            "Heinrich eilte hier vorbei, ohne stehenzubleiben. Die Gendarmen würden zuerst am "
            "Schloss suchen, dann die Münzgasse hinunter. Er hatte vielleicht noch zwanzig Minuten."
        ),
    },

    # 2 - Alte Aula (Raetsel)
    {
        "name": "Station 2 - Alte Aula der Universitaet",
        "type": "raetsel",
        "story": (
            "Die Alte Aula - das Festgebäude der Universität Tübingen. Heinrich duckte sich durch "
            "den Seiteneingang, den er als Professor kannte. Der Hausmeister schlief um diese Zeit.\n\n"
            "Im großen Saal, hinter dem Rednerpult, gibt es eine lose Holzvertäfelung. Heinrich "
            "schob das erste codierte Fragment seiner Forschung dahinter. Wenn jemand diese Tafel "
            "jemals abheben sollte, würde er einen Zettel mit einer kryptischen Formel finden - "
            "nutzlos ohne die anderen Fragmente.\n\n"
            "Die Alte Aula war der Ort, an dem Heinrich vor drei Jahren seine Antrittsvorlesung "
            "gehalten hatte. 'Über die unsichtbaren Kräfte der Materie.' Der Dekan hatte skeptisch "
            "gelächelt. Das Ministerium hatte aufmerksam zugehört."
        ),
        "diary": (
            "In der Bibliothek der Alten Aula, hinter den theologischen Abhandlungen, fand ich "
            "damals das arabische Manuskript, das alles veränderte. Heute verstecke ich mein "
            "eigenes Werk an diesem Ort. Ich hoffe, es hat mehr Glück als ich."
        ),
        "fact": (
            "Die Universitaet Tuebingen ist die fuenftaelteste im deutschen Sprachraum. In der "
            "Alten Aula haengt noch heute das Portraet von Herzog Eberhard im Bart, der 1477 die "
            "Uni gruendete - mit nur 11 Professoren und 300 Studenten.\n\n"
            "Philipp Melanchthon lehrte hier griechische Grammatik - mit nur 21 Jahren! Und der "
            "junge Kepler wurde hier fuer seine astronomischen Ideen fast von der Uni geworfen."
        ),
    },

    # 3 - Martinianum (Anekdote)
    {
        "name": "Station 3 - Martinianum, Muenzgasse 13",
        "type": "anekdote",
        "anecdote": (
            "Heinrich hastete die Münzgasse hinunter. Im Vorbeigehen streifte sein Blick ein kleines "
            "Schild an der Hauswand - das berühmteste Schild Tübingens. 'Hier kotzte Goethe.'\n\n"
            "Johann Wolfgang von Goethe besuchte Tübingen 1797 auf seiner Schweizerreise und war "
            "offenbar nicht begeistert - vom Wein, vom Essen, oder von der Gesellschaft. "
            "Das Martinianum in der Münzgasse 13 ist eines der ältesten Privathäuser der Stadt. "
            "Das Schild wurde auf Betreiben des Tübinger Verschönerungsvereins angebracht.\n\n"
            "Heinrich hatte hier zeitweise gewohnt, bevor er sein Labor im Schloss bezog. "
            "Das Zimmer im zweiten Stock, karg aber ruhig. Von seinem Fenster aus konnte er den "
            "Eingang des Collegiums sehen - und jeden, der die Münzgasse heraufkam. "
            "Eine nützliche Eigenschaft, die er heute hätte gebrauchen können."
        ),
    },

    # 4 - Stiftskirche (Raetsel)
    {
        "name": "Station 4 - Stiftskirche",
        "type": "raetsel",
        "story": (
            "Die Stiftskirche Sankt Georg - das spirituelle Herz der Altstadt. Heinrich erreichte "
            "die Kirche atemlos. Der alte Mesner, ein Freund seiner Studentenzeit, ließ ihn durch "
            "den Seiteneingang.\n\n"
            "'Fünf Minuten', flüsterte Heinrich. Der Mesner nickte. In einem Beichtstuhl in der "
            "hinteren linken Ecke gibt es einen losen Stein. Heinrich schob das zweite Fragment "
            "dahinter.\n\n"
            "Die Stiftskirche mit ihrem markanten Kirchturm ist eines der bedeutendsten Bauwerke "
            "der Spätgotik in Württemberg. In der Fürstengruft im Chorbereich sind württembergische "
            "Herzöge und Universitätsprofessoren begraben - die Gelehrten, die im Leben so viel "
            "stritten, ruhen im Tod friedlich nebeneinander."
        ),
        "diary": (
            "Der Mesner hat mich erkannt und nichts gefragt. Es gibt noch gute Menschen in dieser "
            "Stadt. Ich habe das Fragment hinter dem dritten Stein links im hinteren Beichtstuhl "
            "versteckt. Möge es dort lange sicher sein."
        ),
        "fact": (
            "In der Fuerstengruft der Stiftskirche liegen 15 Mitglieder des Hauses Wuerttemberg "
            "begraben - darunter der Universitaetsgruender Eberhard im Bart. Seine Grabplatte zeigt "
            "ihn betend mit seinem Lieblingsspruch: 'Attempto' (Ich wag's).\n\n"
            "Der Turm hat eine Besonderheit: Die Turmwaechterwohnung auf halber Hoehe war bis 1948 "
            "bewohnt! Der letzte Turmwaechter hiess Karl Weihenmaier und lebte dort mit seiner Familie."
        ),
    },

    # 5 - Holzmarkt & Georgsbrunnen (Anekdote)
    {
        "name": "Station 5 - Holzmarkt & Georgsbrunnen",
        "type": "anekdote",
        "anecdote": (
            "Heinrich verließ die Stiftskirche durch den Nordausgang und stand auf dem Holzmarkt - "
            "dem langgezogenen Platz nördlich der Kirche. Früher hieß er 'Hafenmarkt', so steht es "
            "noch auf der Katasterkarte von 1819.\n\n"
            "Der Georgsbrunnen in der Mitte zeigt den Heiligen Georg beim Drachentöten - "
            "den Schutzpatron der Stiftskirche. Das Original wurde 1523 vom Steinmetz Andreas Lang "
            "geschaffen. Es wurde 1841 abgebaut, 1842 durch eine neugotische Gusseisen-Version "
            "ersetzt - und die wurde 1961 entfernt. Für Parkplätze. Ernsthaft. 1976 kam der "
            "Brunnen zurück, als der Holzmarkt Fußgängerzone wurde.\n\n"
            "Ein paar Schritte weiter, vor dem Café Hirsch, gibt es den Froschkönigbrunnen. "
            "Der Brunnen war jahrelang vermüllt - ein Meter Müll in sieben Metern Tiefe. "
            "2024 initiierte eine engagierte Bürgerin die Reinigung, und 2025 wurde ein "
            "handgefertigter Froschkönig aus Ton als neue Figur eingesetzt. Er schaut direkt "
            "auf die Tübinger Froschgasse und wird nachts von einer Solarlampe angestrahlt.\n\n"
            "Heinrich überquerte den Holzmarkt hastig. Unter den Gaslaternen waren noch einige "
            "Bürger unterwegs. Er senkte den Kopf und ging weiter."
        ),
    },

    # 6 - Rathaus & Astronomische Uhr (Raetsel)
    {
        "name": "Station 6 - Rathaus & Astronomische Uhr",
        "type": "raetsel",
        "story": (
            "Der Marktplatz - das Herz der Stadt. Das prächtige Rathaus thront vor dir, seine "
            "Fassade reich bemalt. Die große astronomische Uhr an der Seite zeigt nicht nur die "
            "Zeit, sondern auch Mondphasen, Tierkreiszeichen und den Lauf der Planeten.\n\n"
            "Heinrich mischte sich unter die letzten Marktbesucher. Der Neptunbrunnen auf dem Platz "
            "plätscherte leise. Die Treppe neben dem Rathaus ist übrigens absichtlich schief gebaut - "
            "sie folgt dem alten Abwasserkanal, der einst mitten durch den Marktplatz floss. "
            "Elegante Lösung eines uneleganten Problems.\n\n"
            "Unter dem Rathaus, in einer Mauernische, versteckte Heinrich das dritte Fragment. "
            "Der Telegrafenbote hatte gerade das Amt verlassen - Heinrich wusste, dass sein Telegramm "
            "aus Stuttgart längst angekommen war. Die Gendarmen konnten jeden Moment erscheinen."
        ),
        "diary": (
            "Die Uhr am Rathaus fasziniert mich noch immer. 1511 gebaut, von Professor Stöffler "
            "entworfen - und sie läuft noch. Der Drachenzeiger sagt Finsternisse voraus. Manchmal "
            "wünschte ich, er könnte auch meine Zukunft vorhersagen.\n\n"
            "Ich habe das Fragment unter dem Rathaus versteckt. Der Neptunbrunnen hat zugesehen. "
            "Stumm, wie immer. Weiter. Ich muss den Neckar erreichen."
        ),
        "fact": (
            "Die astronomische Uhr am Tübinger Rathaus stammt aus dem Jahr 1511 und wurde vom "
            "Astronomen Johannes Stöffler entworfen. Der berühmte Drachenzeiger markiert die "
            "Mondknoten und sagt Finsternisse voraus.\n\n"
            "Die sieben Namen an der Fassade ehren bedeutende Persönlichkeiten der Stadtgeschichte. "
            "Graf Eberhard im Bart, der Universitätsgründer, thront ganz oben am Giebel - "
            "leicht zu übersehen, aber der wichtigste von allen.\n\n"
            "Der Neptunbrunnen auf dem Marktplatz und die schiefe Treppe, die einem alten "
            "Abwasserkanal folgt, gehören ebenfalls zu den Besonderheiten des Platzes."
        ),
    },

    # 7 - Stadtmuseum im Kornhaus (Anekdote)
    {
        "name": "Station 7 - Stadtmuseum im Kornhaus",
        "type": "anekdote",
        "anecdote": (
            "Vom Marktplatz aus passierte Heinrich das Kornhaus - das Gebäude, das heute das "
            "Stadtmuseum beherbergt. Erbaut 1453 als überdachter Getreidemarkt, zwischen 1512 und "
            "1564 erweitert und aufgestockt.\n\n"
            "Was dich drinnen erwartet, falls du reingehst: eine funktionierende Nachbildung von "
            "Wilhelm Schickards mechanischem Rechner von 1623 - die erste Rechenmaschine der Welt, "
            "Jahrzehnte vor Pascals berühmtem Modell. Rekonstruiert zwischen 1957 und 1960. "
            "Und sie rechnet tatsächlich noch.\n\n"
            "Der Eintritt ist seit April 2018 frei. Sonntags um 15 Uhr gibt es eine Führung - "
            "5 Euro für Erwachsene, Kinder kostenlos.\n\n"
            "Heinrich hatte keine Zeit für Museen. Er bog in die Kornhausstraße ein und eilte "
            "bergab Richtung Ammergasse."
        ),
    },

    # 8 - Ammerschlag (Anekdote)
    {
        "name": "Station 8 - Ammerschlag",
        "type": "anekdote",
        "anecdote": (
            "Heinrich brauchte eine Pause. Und einen Plan. Er duckte sich in den Ammerschlag - "
            "eine der ältesten Kneipen Tübingens in der Ammergasse 13.\n\n"
            "Der Legende nach geht der Ammerschlag auf einen Ziegenhirten zurück, der hier sein "
            "Haus baute, noch bevor das Schloss stand. Aus dem 'Ziegenschlag' wurde über die "
            "Jahrhunderte der 'Ammerschlag'. Napoleon soll auf seinen Feldzügen hier eingekehrt "
            "sein, um sich auszuruhen. Ob das stimmt? Die Kneipe behauptet es jedenfalls.\n\n"
            "Eine Besonderheit: Der Ammerschlag ist eine der wenigen Gaststätten in Deutschland, "
            "in der noch überall geraucht werden darf - komplett. Kein Nichtraucherbereich.\n\n"
            "Heinrich bestellte einen Viertele Trollinger, trank ihn in einem Zug, legte zwei "
            "Kreuzer auf den Tresen und verschwand durch die Hintertür. Der Wirt zuckte mit den "
            "Schultern. In dieser Kneipe stellte man keine Fragen.\n\n"
            "Geöffnet: Sonntag bis Donnerstag 15 bis 1 Uhr, Freitag und Samstag 10 bis 3 Uhr."
        ),
    },

    # 9 - Haagtorplatz (Raetsel)
    {
        "name": "Station 9 - Haagtorplatz",
        "type": "raetsel",
        "story": (
            "Heinrich eilte westwärts durch die Ammergasse und erreichte den Haagtorplatz. "
            "Hier stand einmal das Haagtor - eines von fünf Stadttoren der mittelalterlichen "
            "Befestigung.\n\n"
            "Der Name kommt von 'Haag' - der Schutzhecke am Nordhang des Schlossbergs. "
            "Das Tor führte nach Westen Richtung Herrenberg, entlang der Ammer. Es wurde 1831 "
            "abgerissen, als die Stadt sich ausdehnte und die alten Mauern hinderlich wurden.\n\n"
            "Schau auf den Boden: Die Pflasterung zeigt noch die Umrisse der alten Fundamente. "
            "Eine Gedenktafel wurde 2009 angebracht. Heinrich kannte das Tor noch aus Zeichnungen "
            "seines Großvaters - für ihn war es ein Symbol dafür, wie schnell eine Stadt ihre "
            "Geschichte vergisst.\n\n"
            "Er versteckte ein Fragment in einer Mauernische nahe der alten Fundamente und ging weiter."
        ),
        "diary": (
            "Das Haagtor ist weg. Abgerissen. 1831, sagen sie. Aber die Fundamente sind noch da, "
            "unter dem Pflaster. Genau wie meine Formeln bald unter dem Staub dieser Stadt liegen "
            "werden. Unsichtbar, aber nicht verloren."
        ),
        "fact": (
            "Tuebingens fuenf Stadttore hiessen: Lustnauer Tor (Osten), Haagtor (Westen), "
            "Schmiedtor (Norden), Neckartor (Sueden) und das Wurmlinger Tor. Sie wurden alle "
            "zwischen 1804 und 1831 abgerissen.\n\n"
            "Fun Fact: Als das Haagtor 1831 fiel, protestierten Buerger - nicht wegen der Geschichte, "
            "sondern weil der Torwaechter seinen Job verlor. Er bekam eine Abfindung von 50 Gulden."
        ),
    },

    # 10 - Affenfelsen (Raetsel)
    {
        "name": "Station 10 - Affenfelsen",
        "type": "raetsel",
        "story": (
            "Vom Haagtorplatz ging Heinrich weiter zum Affenfelsen - einem Stadtmauerrest am Rand "
            "der Altstadt, wo der Ammerkanal durch ein Tor unter der alten Mauer hindurchfließt.\n\n"
            "Der Name klingt seltsam: 'Affenfelsen'. Er kommt wahrscheinlich daher, dass Kinder "
            "auf den Mauerresten herumkletterten wie kleine Affen. Andere sagen, es liegt daran, "
            "dass sich hier im Sommer junge Leute trafen - und sich dabei, nun ja, affig benahmen.\n\n"
            "Der Ammerkanal fließt hier durch einen kleinen Bogen in der Stadtmauer - ein "
            "faszinierendes Bild: mittelalterliche Steine über lebendigem Wasser. Heinrich "
            "beobachtete das Wasser und überlegte kurz, ob er dem Kanal folgen sollte. "
            "Aber nein - sein Weg führte weiter."
        ),
        "diary": (
            "Am Affenfelsen. Das Wasser der Ammer fließt unter der alten Mauer hindurch - ruhig, "
            "gleichmäßig, ohne sich um Gendarmen oder Formeln zu scheren. Ich beneide den Bach."
        ),
        "fact": (
            "Die Tuebinger Stadtmauer wurde im 13. Jahrhundert errichtet und war etwa 1,5 Kilometer "
            "lang. Am Affenfelsen sieht man besonders gut, wie dick die Mauern waren - ueber einen Meter.\n\n"
            "Der Ammerkanal, der hier durchfliesst, trieb frueher mehrere Muehlen in der Altstadt an. "
            "Das Wasser wurde so geschickt gelenkt, dass Gerber, Faerber und Mueller es nacheinander "
            "nutzen konnten - ein mittelalterliches Recyclingsystem."
        ),
    },

    # 11 - Alter Botanischer Garten (Anekdote)
    {
        "name": "Station 11 - Alter Botanischer Garten",
        "type": "anekdote",
        "anecdote": (
            "Heinrich schlug einen Bogen nach Osten und schnitt durch den Alten Botanischen Garten - "
            "eine grüne Oase inmitten der Stadt. Der Garten wurde 1535 als einer der ersten "
            "botanischen Gärten Deutschlands angelegt.\n\n"
            "Hier wuchsen exotische Pflanzen aus aller Welt - Geschenke von Forschungsreisenden, "
            "Botanikern und Missionaren. Riesige Mammutbäume, die heute noch stehen. Im Gewächshaus "
            "tropische Palmen und Orchideen.\n\n"
            "Für Heinrich war der Garten ein vertrauter Ort. Er hatte hier oft Proben gesammelt "
            "für seine Experimente. Jetzt, in der Novemberdunkelheit, waren die Wege leer. "
            "Die kahlen Äste der Platanen warfen bizarre Schatten im Licht der fernen Gaslaternen.\n\n"
            "Er durchquerte den Garten in wenigen Minuten und kam an der Wilhelmstraße heraus - "
            "direkt gegenüber der Neuen Aula."
        ),
    },

    # 12 - Neue Aula (Anekdote)
    {
        "name": "Station 12 - Neue Aula",
        "type": "anekdote",
        "anecdote": (
            "Die Neue Aula - das imposante Hauptgebäude der Universität, 1845 im klassizistischen "
            "Stil erbaut. Hier hielt Heinrich seine letzten Vorlesungen, bevor das Ministerium ihn "
            "unter Beobachtung stellte.\n\n"
            "Die Neue Aula war ein Statement: Tübingen als moderne, weltoffene Universität. "
            "Große Fenster, helle Säle, ein Hauch von Aufklärung in Stein. Für Heinrich war sie "
            "ein Symbol dessen, was die Universität sein könnte - und was sie unter dem Druck der "
            "Politik nicht sein durfte.\n\n"
            "Er blickte kurz auf die erleuchteten Fenster des Erdgeschosses. Irgendwo da drin saß "
            "vielleicht noch ein Student über seinen Büchern, nichts ahnend von der Jagd, die sich "
            "gerade durch die Stadt wand.\n\n"
            "'Leb wohl, Universität', murmelte Heinrich. Dann wandte er sich ab und ging bergab "
            "Richtung Ammerviertel."
        ),
    },

    # 13 - Nonnenhaus (Raetsel)
    {
        "name": "Station 13 - Nonnenhaus",
        "type": "raetsel",
        "story": (
            "Das Nonnenhaus - eines der ältesten Fachwerkhäuser der Altstadt, erbaut 1488. "
            "Der Name täuscht: Hier lebten keine Nonnen, sondern Beginen - Frauen einer "
            "christlichen Laiengemeinschaft ohne Klostergelübde.\n\n"
            "Später wohnte hier der Botaniker Leonhard Fuchs, nach dem die Fuchsie benannt ist. "
            "Heinrich versteckte sein vorletztes Fragment im Nonnenhaus - in einem Hohlraum hinter "
            "der alten Holzverkleidung.\n\n"
            "Und dann ist da die Rückseite des Hauses. Im ersten Stock ragt ein hölzerner Erker "
            "weit über den Ammerkanal hinaus - über die Gasse hinweg bis direkt übers Wasser gebaut. "
            "Warum dieser aufwändige Bau? Die Antwort ist praktisch, mittelalterlich effizient - "
            "und ziemlich lustig."
        ),
        "diary": (
            "Das Nonnenhaus. 1488. Die Balken knarren unter meinen Schritten, als wollten sie "
            "protestieren. Ich habe mein vorletztes Fragment hier versteckt - dort, wo die Beginen "
            "einst ihre irdischen Bedürfnisse direkt dem Wasser überantworteten. "
            "Niemand sucht an solchen Orten."
        ),
        "fact": (
            "Der Erker-Abort des Nonnenhauses ist eines der besterhaltenen Beispiele mittelalterlicher "
            "Sanitaeranlagen in Sueddeutschland. Das Prinzip war einfach: Die Schwerkraft erledigte "
            "den Rest, der Ammerkanal spuelte alles weg.\n\n"
            "Leonhard Fuchs (1501-1566), der hier lebte, beschrieb ueber 400 Pflanzen in seinem "
            "'New Kreuterbuch' von 1543 - mit handkolorierten Holzschnitten. Das Buch war so "
            "erfolgreich, dass die Fuchsie nach ihm benannt wurde, obwohl er die Pflanze nie gesehen hat."
        ),
    },

    # 14 - Neckarinsel & Platanenallee (Anekdote)
    {
        "name": "Station 14 - Neckarinsel & Platanenallee",
        "type": "anekdote",
        "anecdote": (
            "Heinrich erreichte die Neckarinsel - das schmale Eiland mitten im Fluss, verbunden "
            "durch zwei Brücken mit der Stadt. Er war jetzt fast am Ziel.\n\n"
            "Die Platanenallee auf der Insel wurde in den 1820er Jahren angelegt. Die mächtigen "
            "Bäume sind heute über 190 Jahre alt und Naturdenkmäler. In den Zweigen über dir "
            "verschränken sich die Äste zu einem natürlichen Gewölbe.\n\n"
            "Von der Insel aus siehst du auch den Indianersteg - eine schmale Fußgängerbrücke, "
            "die die Insel mit dem anderen Ufer verbindet. Sie wurde 1863 als Holzbrücke gebaut. "
            "Ihren Namen verdankt sie spielenden Kindern, die auf der wackeligen Holzbrücke "
            "'Indianer' spielten.\n\n"
            "Heinrich stand einen Moment still unter den kahlen Platanen. Der Neckar rauschte "
            "auf beiden Seiten. Stocherkähne lagen vertäut am Ufer. Noch ein paar hundert Meter. "
            "Noch eine Brücke."
        ),
    },

    # 15 - Indianersteg (Raetsel / Finale)
    {
        "name": "Station 15 - Indianersteg (Finale)",
        "type": "raetsel",
        "story": (
            "Der Indianersteg - eine schmale Fußgängerbrücke über den Neckar. "
            "Heinrichs letzte Hürde.\n\n"
            "Die erste Holzbrücke wurde hier 1863 errichtet. Ihren Namen verdankt sie spielenden "
            "Kindern, die auf der wackeligen Konstruktion 'Indianer' spielten - ein Unfallbericht "
            "von 1871 ist das erste dokumentierte Zeugnis des Namens.\n\n"
            "Die Holzbrücke wurde um 1900 durch eine Eisenträgerbrücke ersetzt, dann 1911 durch "
            "eine Betonbogenbrücke - die gegen Ende des Zweiten Weltkriegs zerstört und danach "
            "einfacher wiederaufgebaut wurde. Heute hat sie smaragdgrüne Geländer.\n\n"
            "Heinrich überquerte die wackelige Holzbrücke in jener Novembernacht 1869. "
            "Auf der anderen Seite: Dunkelheit, Felder, Freiheit. Er hörte noch die Rufe der "
            "Gendarmen vom anderen Ufer. Aber es war zu spät. Der Forscher war verschwunden.\n\n"
            "Das letzte Fragment seiner Formel versteckte er unter einem losen Stein am "
            "Brückengeländer. Du stehst jetzt dort, wo Heinrich von Calw in die Freiheit ging."
        ),
        "diary": (
            "Der Steg wackelt unter meinen Schritten. Der Neckar ist schwarz und still. "
            "Auf der anderen Seite beginnt die Nacht, in der ich verschwinden werde. "
            "Über Rottenburg nach Süden. Die Schweizer Grenze.\n\n"
            "Meine Formel ist verteilt - sechzehn Fragmente an sechzehn Orten. "
            "Wer sie alle findet, wird verstehen: Die gefährlichste Waffe ist nicht die "
            "Formel selbst. Es ist die Angst der Mächtigen vor dem freien Wissen.\n\n"
            "Lebe wohl, Tübingen."
        ),
        "fact": (
            "1869 waren jenseits des Stegs nur nasse Wiesen und Felder - die Neckarauen. Die "
            "Suedstadt entstand erst ab den 1880er Jahren, nachdem der Neckar reguliert wurde.\n\n"
            "Der Hauptbahnhof stand seit 1861 als einsames Gebaeude in der Ebene. Die Kaserne kam "
            "erst 1873. Wer 1869 ueber den Steg ging, verschwand buchstaeblich in der Dunkelheit - "
            "genau wie Heinrich.\n\n"
            "Fun Fact: Der Name 'Indianersteg' taucht erstmals 1871 in einem Unfallbericht auf. "
            "Kinder spielten auf der wackeligen Bruecke Karl-May-Spiele."
        ),
    },
]

# ============================================================
# AUDIO-GENERIERUNG
# ============================================================

def generate_audio(client, text, voice_id, output_path):
    """Generiert eine MP3-Datei aus Text via ElevenLabs API."""
    print(f"  Generiere: {output_path.name} ({len(text)} Zeichen)...", end=" ", flush=True)

    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=MODEL_ID,
            output_format="mp3_44100_128",
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        size_kb = output_path.stat().st_size / 1024
        print(f"OK ({size_kb:.0f} KB)")
        return True

    except Exception as e:
        print(f"FEHLER: {e}")
        return False


def list_voices(client):
    """Zeigt alle verfuegbaren Stimmen an."""
    print("\nVerfuegbare Stimmen:\n")
    response = client.voices.get_all()
    for v in response.voices:
        labels = ", ".join(f"{k}: {val}" for k, val in (v.labels or {}).items())
        print(f"  {v.name:25s}  ID: {v.voice_id}  [{labels}]")
    print()


def main():
    if API_KEY == "DEIN_API_KEY_HIER":
        print("Bitte setze deinen ElevenLabs API-Key!")
        print("   export ELEVENLABS_API_KEY='dein-key-hier'")
        print("   oder trage ihn direkt in generate_audio.py ein.")
        sys.exit(1)

    client = ElevenLabs(api_key=API_KEY)

    if "--list-voices" in sys.argv:
        list_voices(client)
        sys.exit(0)

    if "--station" in sys.argv:
        idx = sys.argv.index("--station")
        station_nums = [int(x) for x in sys.argv[idx + 1].split(",")]
    else:
        station_nums = list(range(16))

    all_types = ["story", "diary", "fact", "anecdote"]
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        types_to_gen = sys.argv[idx + 1].split(",")
    else:
        types_to_gen = all_types

    OUTPUT_DIR.mkdir(exist_ok=True)

    voice_map = {
        "story": NARRATOR_VOICE,
        "diary": HEINRICH_VOICE,
        "fact": FACT_VOICE,
        "anecdote": FACT_VOICE,
    }

    total = 0
    for i in station_nums:
        station = STATIONS[i]
        for audio_type in types_to_gen:
            if audio_type in station:
                total += 1

    done = 0
    errors = 0

    print("=" * 60)
    print("TraceTour Audio Generator - v5 (16 Stationen, 1869)")
    print("=" * 60)
    print(f"Output:    {OUTPUT_DIR}")
    print(f"Stationen: {station_nums}")
    print(f"Typen:     {types_to_gen}")
    print(f"Gesamt:    {total} Dateien")
    print("=" * 60)

    for i in station_nums:
        station = STATIONS[i]
        print(f"\n{station['name']} ({station['type']})")

        for audio_type in types_to_gen:
            if audio_type not in station:
                continue

            text = station[audio_type]
            voice_id = voice_map[audio_type]
            filename = f"{audio_type}_{i}.mp3"
            output_path = OUTPUT_DIR / filename

            success = generate_audio(client, text, voice_id, output_path)
            done += 1
            if not success:
                errors += 1

            time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"Fertig! {done - errors}/{total} Dateien generiert.")
    if errors:
        print(f"{errors} Fehler aufgetreten.")
    print(f"Dateien in: {OUTPUT_DIR}")
    print("=" * 60)

    print("\nGenerierte Dateien:")
    for f in sorted(OUTPUT_DIR.glob("*.mp3")):
        size = f.stat().st_size / 1024
        print(f"   {f.name:20s}  {size:6.0f} KB")


if __name__ == "__main__":
    main()
