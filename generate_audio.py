#!/usr/bin/env python3
"""
TraceTour Audio Generator -- ElevenLabs TTS
v6 -- 17 Stationen, 1869 Story, Vollvertonung

Generiert alle Audio-Dateien fuer die 17 Stationen:
  Raetsel-Stationen (0,2,4,6,9,11,14,16):
    - story_X.mp3   (Erzaehler-Stimme)
    - diary_X.mp3   (Heinrichs Stimme)
    - fact_X.mp3    (Fakten-Stimme)
    - riddle_X.mp3  (Erzaehler-Stimme, Raetseltext)
  Anekdoten-Stationen (1,3,5,7,8,10,12,13,15):
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

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_005ded915f772d5798f850aaac462b572c1ea0905252f50e")

NARRATOR_VOICE = "WHaUUVTDq47Yqc9aDbkH"   # Story-Stimme (gleich wie vorher)
HEINRICH_VOICE = "2OcnG4mH3jIMtWz3vKus"   # Tagebuch-Stimme (gleich wie vorher)
FACT_VOICE     = "PhufIH7nYh2Up1uej6aY"   # Stadtfuehrer-Stimme (gleich wie vorher)

MODEL_ID = "eleven_multilingual_v2"
OUTPUT_DIR = Path(__file__).parent / "audio"

# ============================================================
# ALLE TEXTE DER 17 STATIONEN
# ============================================================

STATIONS = [
    # 0 - Schloss Hohentuebingen (Raetsel)
    {
        "name": "Station 0 - Schloss Hohentuebingen",
        "type": "raetsel",
        "story": (
            "Das Schloss Hohentübingen - dein Ausgangspunkt. Von hier oben überblickst du "
            "die gesamte Altstadt. Gaslaternen flackern in den Gassen unter dir. "
            "Es ist November achtzehnhundertneunundsechzig, kurz vor Einbruch der Nacht.\n\n"
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
            "fünfzehnhundertneunundvierzig mit vierundachtzigtausend Litern Fassungsvermoegen. Die Universitaet nutzte das Schloss bis ins "
            "zwanzigste Jahrhundert als Laborgebaeude - Friedrich Miescher entdeckte hier achtzehnhundertneunundsechzig die DNA! "
            "Ausserdem fand man in den Gewoelben die Vogelherd-Figuren: vierzigtausend Jahre alte "
            "Elfenbeinschnitzereien, die aeltesten bekannten Kunstwerke der Menschheit."
        ),
        "riddle": (
            "Am Eingangstor des Schlosses siehst du das württembergische Wappen in Stein gemeißelt. "
            "Welches Tier ist das größte und auffälligste auf dem Wappen? Ein Wort."
        ),
    },

    # 1 - Studentenkarzer (Anekdote)
    {
        "name": "Station 1 - Studentenkarzer",
        "type": "anekdote",
        "anecdote": (
            "Auf dem Weg bergab passierst du den Studentenkarzer in der Münzgasse zwanzig - "
            "das Universitätsgefängnis, in das Tübinger Studenten seit fünfzehnhundertfünfzehn gesperrt wurden. "
            "Der älteste erhaltene Uni-Karzer Deutschlands.\n\n"
            "Heinrich kannte den Karzer gut. Als Student saß er hier zwei Nächte wegen 'Nachtwandeln' - "
            "er war nachts heimlich im Labor geblieben. Die Zellen sind winzig: zwei verbundene Räume "
            "mit zusammen fünfzehn Quadratmetern und kleinen Fensteröffnungen. Die Wände sind übersät "
            "mit Inschriften und Zeichnungen der Insassen seit dem sechzehnten Jahrhundert.\n\n"
            "Vergehen, die zum Karzer führten: Nachtwandeln, das Tragen 'absichtlich neumodisch "
            "geschlitzter Kleidung', unautorisierte Eheschließungen und Glücksspiel. Der Karzer "
            "war bis achtzehnhundertfünfundvierzig in Betrieb - also gerade noch zu Heinrichs Studentenzeit.\n\n"
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
            "Alten Aula haengt noch heute das Portraet von Herzog Eberhard im Bart, der vierzehnhundertsiebenundsiebzig die "
            "Uni gruendete - mit nur elf Professoren und dreihundert Studenten.\n\n"
            "Philipp Melanchthon lehrte hier griechische Grammatik - mit nur einundzwanzig Jahren! Und der "
            "junge Kepler wurde hier fuer seine astronomischen Ideen fast von der Uni geworfen."
        ),
        "riddle": (
            "Auf der Infotafel der Alten Aula stehen zwei Jahreszahlen: das Baujahr und das Jahr "
            "des Umbaus zum dreihundertjährigen Uni-Jubiläum. Ziehe dreihundert vom Umbaujahr ab - in welchem "
            "Jahr wurde die Universität Tübingen gegründet?"
        ),
    },

    # 3 - Martinianum (Anekdote)
    {
        "name": "Station 3 - Martinianum, Muenzgasse 13",
        "type": "anekdote",
        "anecdote": (
            "Heinrich hastete die Münzgasse hinunter. Im Vorbeigehen streifte sein Blick ein kleines "
            "Schild an der Hauswand - das berühmteste Schild Tübingens. 'Hier kotzte Goethe.'\n\n"
            "Johann Wolfgang von Goethe besuchte Tübingen siebzehnhundertsiebenundneunzig auf seiner Schweizerreise und "
            "wohnte nebenan in der Münzgasse fünfzehn bei seinem Verleger Cotta. Sein Urteil: "
            "'Die Stadt selbst ist abscheulich, allein man darf nur wenige Schritte tun, um die "
            "schönste Gegend zu sehen.' Die Stadt fand er also hässlich - die Landschaft drumherum "
            "aber wunderschön. Das Schild 'Hier kotzte Goethe' am Martinianum ist ein satirischer "
            "Kommentar auf den übertriebenen Goethe-Kult - kein historisches Ereignis.\n\n"
            "Heinrich hatte hier zeitweise gewohnt, bevor er sein Labor im Schloss bezog. "
            "Das Zimmer im zweiten Stock, karg aber ruhig. Von seinem Fenster aus konnte er die "
            "enge Münzgasse überblicken - und jeden sehen, der heraufkam. "
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
            "der Spätgotik in Württemberg. Im Chorbereich befinden sich vierzehn steinerne Grabmale "
            "württembergischer Herrscher und ihrer Angehörigen - darunter Herzog Eberhard im Bart, "
            "der Universitätsgründer."
        ),
        "diary": (
            "Der Mesner hat mich erkannt und nichts gefragt. Es gibt noch gute Menschen in dieser "
            "Stadt. Ich habe das Fragment hinter dem dritten Stein links im hinteren Beichtstuhl "
            "versteckt. Möge es dort lange sicher sein."
        ),
        "fact": (
            "Eberhard im Bart wurde zunächst woanders beigesetzt und erst um fünfzehnhundertfünfunddreißig "
            "in die Stiftskirche überführt. Sein Grabmal zeigt ihn betend mit seinem Lieblingsspruch: "
            "'Attempto' - Ich wag's. Dieses Motto ist heute noch das offizielle Motto der Universität "
            "Tübingen.\n\n"
            "Der mittelalterliche Lettner - eine kunstvolle Trennwand zwischen Chor und Kirchenschiff - "
            "überlebte nur, weil Herzog Ulrich fünfzehnhundertvierunddreißig die Grablege in den Chor verlegte. "
            "Ohne diese Entscheidung wäre er wie in den meisten anderen Kirchen abgerissen worden.\n\n"
            "Die Turmwächterwohnung auf halber Höhe war bis neunzehnhundertachtundvierzig bewohnt! "
            "Der letzte Turmwächter hieß Karl Weihenmaier und lebte dort mit seiner ganzen Familie - "
            "hundertneunundsechzig Stufen über der Stadt."
        ),
        "riddle": (
            "Schau dir den Kirchturm der Stiftskirche genau an. Wie hoch ist er? "
            "Beim Bau ging das Geld aus - der Turm blieb kleiner als geplant!"
        ),
    },

    # 5 - Holzmarkt & Georgsbrunnen (Anekdote)
    {
        "name": "Station 5 - Holzmarkt & Georgsbrunnen",
        "type": "anekdote",
        "anecdote": (
            "Heinrich verließ die Stiftskirche durch den Nordausgang und stand auf dem Holzmarkt - "
            "dem langgezogenen Platz nördlich der Kirche. Früher hieß er 'Hafenmarkt', so steht es "
            "noch auf der Katasterkarte von achtzehnhundertneunzehn.\n\n"
            "Der Georgsbrunnen in der Mitte zeigt den Heiligen Georg beim Drachentöten - "
            "den Schutzpatron der Stiftskirche. Das Original wurde fünfzehnhundertdreiundzwanzig vom Steinmetz Andreas Lang "
            "geschaffen. Es wurde achtzehnhunderteinundvierzig abgebaut, achtzehnhundertzweiundvierzig durch eine neugotische Gusseisen-Version "
            "ersetzt - und die wurde neunzehnhunderteinundsechzig entfernt. Für Parkplätze. Ernsthaft. Neunzehnhundertsechsundsiebzig kam der "
            "Brunnen zurück, als der Holzmarkt Fußgängerzone wurde.\n\n"
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
            "Der Marktplatz war noch belebt. Zu belebt. Ich duckte mich hinter den Neptunbrunnen "
            "und wartete, bis eine Gruppe Studenten vorbeigezogen war. Mein Herz schlug bis zum Hals.\n\n"
            "Ich habe das Fragment in einer Mauernische unter dem Rathaus versteckt. Meine Hände "
            "zitterten. Wie viel Zeit bleibt mir noch? Die Gendarmen können nicht weit sein. "
            "Ich muss den Neckar erreichen, bevor sie den Marktplatz absperren."
        ),
        "fact": (
            "Die astronomische Uhr wurde fünfzehnhundertelf vom Astronomen Johannes Stöffler entworfen - "
            "einem der berühmtesten Wissenschaftler seiner Zeit. Der Drachenzeiger markiert die "
            "Mondknoten und sagt Sonnen- und Mondfinsternisse voraus. Die Uhr blieb trotz mehrerer "
            "Rathausbrände intakt.\n\n"
            "Stöffler sagte übrigens für den zwanzigsten Februar fünfzehnhundertvierundzwanzig eine Sintflut voraus. "
            "Ganz Europa geriet in Panik, Menschen bauten Archen. Es regnete an dem Tag - ein bisschen. "
            "Stöffler starb fünfzehnhunderteinunddreißig an der Pest, nicht an einer Flut.\n\n"
            "Das Rathaus selbst wurde erstmals vierzehnhundertfünfunddreißig erwähnt. Die kunstvolle Bemalung der "
            "Fassade stammt von achtzehnhundertsechsundsiebzig und wurde zuletzt zweitausenddrei restauriert."
        ),
        "riddle": (
            "Stell dich vor die Rathaus-Fassade und zähle die gemalten Namen berühmter "
            "Persönlichkeiten. Wie viele sind es? Tipp: Einer versteckt sich ganz oben - "
            "leicht zu übersehen!"
        ),
    },

    # 7 - Stadtmuseum im Kornhaus (Anekdote)
    {
        "name": "Station 7 - Stadtmuseum im Kornhaus",
        "type": "anekdote",
        "anecdote": (
            "Vom Marktplatz aus passierte Heinrich das Kornhaus - das Gebäude, das heute das "
            "Stadtmuseum beherbergt. Erbaut vierzehnhundertdreiundfünfzig als überdachter Getreidemarkt, war es über die "
            "Jahrhunderte schon alles: Festsaal für Tanz und Theater, Knaben- und Mädchenschule, "
            "Feuerwache und Rotes-Kreuz-Station - bevor es neunzehnhunderteinundneunzig als Stadtmuseum eröffnete.\n\n"
            "Was dich drinnen erwartet: eine funktionierende Nachbildung von Wilhelm Schickards "
            "mechanischem Rechner von sechzehnhundertdreiundzwanzig - die erste Rechenmaschine der Welt, "
            "Jahrzehnte vor Pascals berühmtem Modell. Rekonstruiert zwischen neunzehnhundertsiebenundfünfzig und "
            "neunzehnhundertsechzig vom Tübinger Professor Bruno von Freytag-Löringhoff anhand von "
            "Schickards Briefwechsel mit Kepler. Und sie rechnet tatsächlich noch!\n\n"
            "Außerdem sehenswert: die ständige Ausstellung zu Lotte Reiniger, der Pionierin des "
            "Silhouetten-Animationsfilms. Das Fachwerk des Kornhauses ist freigelegt und prägt die "
            "Räume - allerdings wurde bei der Sanierung in den neunzehnhundertachtziger Jahren zementhaltiger "
            "Mörtel verwendet, der eigentlich Fachwerkhölzer zerstört. Ein Tübinger Zimmermeister: "
            "'Hier wurde mehr kaputt gemacht als in den letzten hundert Jahren durch Wind und Wetter.'\n\n"
            "Kuriose Geschichte: zweitausendzwei stellte sich heraus, dass ein Museumsmitarbeiter "
            "hundertdreizehn Objekte gestohlen hatte. Hundertdrei davon konnten sichergestellt werden.\n\n"
            "Der Eintritt ist seit April zweitausendachtzehn frei. Sonntags um fünfzehn Uhr gibt es eine Führung - "
            "fünf Euro für Erwachsene, Kinder kostenlos.\n\n"
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
            "eine der ältesten Kneipen Tübingens in der Ammergasse dreizehn.\n\n"
            "Der Legende nach geht der Ammerschlag auf einen Ziegenhirten zurück, der hier sein "
            "Haus baute, noch bevor das Schloss stand. Aus dem 'Ziegenschlag' wurde über die "
            "Jahrhunderte der 'Ammerschlag'. Napoleon soll auf seinen Feldzügen hier eingekehrt "
            "sein, um sich auszuruhen. Ob das stimmt? Die Kneipe behauptet es jedenfalls.\n\n"
            "Eine Besonderheit: Der Ammerschlag ist eine der wenigen Gaststätten in Deutschland, "
            "in der noch überall geraucht werden darf - komplett. Kein Nichtraucherbereich.\n\n"
            "Heinrich bestellte einen Viertele Trollinger, trank ihn in einem Zug, legte zwei "
            "Kreuzer auf den Tresen und verschwand durch die Hintertür. Der Wirt zuckte mit den "
            "Schultern. In dieser Kneipe stellte man keine Fragen.\n\n"
            "Geöffnet: Sonntag bis Donnerstag fünfzehn bis ein Uhr, Freitag und Samstag zehn bis drei Uhr."
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
            "Das Tor führte nach Westen Richtung Herrenberg, entlang der Ammer. Es wurde achtzehnhunderteinunddreißig "
            "abgerissen, als die Stadt sich ausdehnte und die alten Mauern hinderlich wurden.\n\n"
            "Schau auf den Boden: Die Pflasterung zeigt noch die Umrisse der alten Fundamente. "
            "Eine Gedenktafel wurde zweitausendneun angebracht. Heinrich kannte das Tor noch aus Zeichnungen "
            "seines Großvaters - für ihn war es ein Symbol dafür, wie schnell eine Stadt ihre "
            "Geschichte vergisst.\n\n"
            "Er versteckte ein Fragment in einer Mauernische nahe der alten Fundamente und ging weiter."
        ),
        "diary": (
            "Das Haagtor ist weg. Abgerissen. Achtzehnhunderteinunddreißig, sagen sie. Aber die Fundamente sind noch da, "
            "unter dem Pflaster. Genau wie meine Formeln bald unter dem Staub dieser Stadt liegen "
            "werden. Unsichtbar, aber nicht verloren."
        ),
        "fact": (
            "Tuebingens fuenf Stadttore hiessen: Lustnauer Tor (Osten), Haagtor (Westen), "
            "Schmiedtor (Norden), Neckartor (Sueden) und das Wurmlinger Tor. Sie wurden alle "
            "zwischen achtzehnhundertvier und achtzehnhunderteinunddreißig abgerissen.\n\n"
            "Fun Fact: Als das Haagtor achtzehnhunderteinunddreißig fiel, protestierten Buerger - nicht wegen der Geschichte, "
            "sondern weil der Torwaechter seinen Job verlor. Er bekam eine Abfindung von fünfzig Gulden."
        ),
        "riddle": (
            "Das Haagtor war eines von wie vielen Stadttoren der mittelalterlichen Befestigung "
            "Tübingens? Eine Zahl. Oder: In welchem Jahr wurde es abgerissen? Das steht auf der Gedenktafel."
        ),
    },

    # 10 - Froschkoenig-Brunnen (Anekdote) [NEU]
    {
        "name": "Station 10 - Froschkoenig-Brunnen",
        "type": "anekdote",
        "anecdote": (
            "Auf dem Weg vom Haagtorplatz zum Affenfelsen kam Heinrich am Brunnen vor dem "
            "Café Hirsch vorbei. Ein unscheinbarer Brunnenschacht, sieben Meter tief.\n\n"
            "Heute hat dieser Brunnen eine besondere Geschichte: Jahrelang war er mit einem "
            "Meter Müll vollgestopft. Schulkinder, die ihn beim Stadtquiz besuchten, schauten "
            "angeekelt hinein. Zweitausendvierundzwanzig nahm sich Petra Wenzel, eine engagierte Bürgerin aus dem "
            "Café Hirsch, der Sache an. Die Stadt half mit schwerem Gerät - Gasmasken, "
            "Industrieschläuche, der volle Einsatz.\n\n"
            "Im Frühling zweitausendundfünfundzwanzig wurde ein handgefertigter Froschkönig aus Ton eingesetzt - "
            "vierzig mal vierzig Zentimeter, bunt bemalt und nachts von einer Solarlampe angestrahlt. "
            "Er guckt direkt auf die Tübinger Froschgasse. Eine Glasplatte schützte ihn "
            "vor der Witterung.\n\n"
            "Doch im Oktober zweitausendundfünfundzwanzig wurde der Froschkönig gestohlen - jemand schob die "
            "Glasplatte zur Seite und hievte ihn heraus. 'Das ist so schade für all die "
            "Kinder', sagte Wenzel. Sie bestellte sofort einen neuen. Schau mal, ob er "
            "schon wieder da ist!\n\n"
            "Heinrich bemerkte den Brunnen nicht. Er hatte andere Sorgen."
        ),
    },

    # 11 - Affenfelsen (Raetsel)
    {
        "name": "Station 11 - Affenfelsen",
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
            "Die Tuebinger Stadtmauer wurde im dreizehnten Jahrhundert errichtet und war etwa eineinhalb Kilometer "
            "lang. Am Affenfelsen sieht man besonders gut, wie dick die Mauern waren - ueber einen Meter.\n\n"
            "Der Ammerkanal, der hier durchfliesst, trieb frueher mehrere Muehlen in der Altstadt an. "
            "Das Wasser wurde so geschickt gelenkt, dass Gerber, Faerber und Mueller es nacheinander "
            "nutzen konnten - ein mittelalterliches Recyclingsystem."
        ),
        "riddle": (
            "Welche Bar in der Nähe des Affenfelsens trägt den Namen eines alkoholischen Getränks? Ein Wort."
        ),
    },

    # 12 - Alter Botanischer Garten (Anekdote)
    {
        "name": "Station 12 - Alter Botanischer Garten",
        "type": "anekdote",
        "anecdote": (
            "Heinrich schlug einen Bogen nach Osten und schnitt durch den Alten Botanischen Garten - "
            "eine grüne Oase inmitten der Stadt. Der Garten wurde fünfzehnhundertfünfunddreißig als einer der ersten "
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

    # 13 - Neue Aula (Anekdote)
    {
        "name": "Station 13 - Neue Aula",
        "type": "anekdote",
        "anecdote": (
            "Die Neue Aula - das imposante Hauptgebäude der Universität, achtzehnhundertfünfundvierzig im klassizistischen "
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

    # 14 - Nonnenhaus (Raetsel)
    {
        "name": "Station 14 - Nonnenhaus",
        "type": "raetsel",
        "story": (
            "Das Nonnenhaus - mit dreißig Metern Länge eines der größten Fachwerkhäuser der "
            "Tübinger Altstadt, erbaut vierzehnhundertachtundachtzig. Der Name täuscht: Hier lebten zunächst "
            "Dominikanerinnen, dann Beginen - Frauen einer christlichen Laiengemeinschaft ohne "
            "Klostergelübde. Nach der Reformation fünfzehnhundertvierunddreißig wurde das Kloster aufgelöst.\n\n"
            "Danach zog der Medizinprofessor und Botaniker Leonhard Fuchs ein - mit seiner Frau "
            "und zehn Kindern! Er legte neben dem Haus einen der ältesten botanischen Gärten "
            "Europas an und schrieb hier fünfzehnhundertdreiundvierzig sein berühmtes 'New Kreüterbuch'. "
            "Die Fuchsie wurde nach ihm benannt, obwohl er die Pflanze nie gesehen hat. Vor dem Haus "
            "gibt es heute einen kleinen Erinnerungsgarten mit Pflanzen aus seinem Buch.\n\n"
            "Heinrich versteckte sein vorletztes Fragment im Nonnenhaus - in einem Hohlraum hinter "
            "der alten Holzverkleidung.\n\n"
            "Und dann ist da die Rückseite des Hauses. Im ersten Stock ragt ein hölzerner Vorbau - "
            "das 'Sprachhaus' - weit über den Ammerkanal hinaus. Warum dieser aufwändige Bau direkt "
            "übers Wasser? Die Antwort ist praktisch, mittelalterlich effizient - und ziemlich lustig."
        ),
        "diary": (
            "Das Nonnenhaus. Vierzehnhundertachtundachtzig. Die Balken knarren unter meinen Schritten, als wollten sie "
            "protestieren. Ich habe mein vorletztes Fragment hier versteckt - dort, wo die Beginen "
            "einst ihre irdischen Bedürfnisse direkt dem Wasser überantworteten. "
            "Niemand sucht an solchen Orten."
        ),
        "fact": (
            "Das 'Sprachhaus' am Nonnenhaus ist eines der besterhaltenen Beispiele mittelalterlicher "
            "Sanitäranlagen in Süddeutschland. Das Prinzip war einfach: Die Schwerkraft erledigte "
            "den Rest, der Ammerkanal spülte alles weg.\n\n"
            "Das Gebäude wurde zweitausendsieben, zweitausendacht vorbildlich saniert und erhielt "
            "zweitausendacht den Denkmalschutzpreis Baden-Württemberg. Im Erdgeschoss der heutigen "
            "Buchhandlung ist im Boden ein Sichtfenster eingelassen - es zeigt den originalen "
            "Ziegel-Estrich von vierzehnhundertachtundachtzig!\n\n"
            "Leonhard Fuchs beschrieb über vierhundert Pflanzen in seinem 'New Kreüterbuch' von "
            "fünfzehnhundertdreiundvierzig - mit handkolorierten Holzschnitten. Sein botanischer Garten neben "
            "dem Haus war einer der ältesten in ganz Europa."
        ),
        "riddle": (
            "Schau dir die Rückseite des Nonnenhauses an. Im ersten Stock ragt ein hölzerner Erker "
            "über die Gasse hinweg bis über den Ammerkanal. Warum wurde er so weit übers Wasser gebaut? "
            "Was war seine Funktion? Ein Wort."
        ),
    },

    # 15 - Neckarinsel & Platanenallee (Anekdote)
    {
        "name": "Station 15 - Neckarinsel & Platanenallee",
        "type": "anekdote",
        "anecdote": (
            "Heinrich erreichte die Neckarinsel - das schmale Eiland mitten im Fluss, verbunden "
            "durch zwei Brücken mit der Stadt. Er war jetzt fast am Ziel.\n\n"
            "Die Platanenallee auf der Insel wurde in den achtzehnhundertzwanziger Jahren angelegt. Die mächtigen "
            "Bäume sind heute über hundertneunzig Jahre alt und Naturdenkmäler. In den Zweigen über dir "
            "verschränken sich die Äste zu einem natürlichen Gewölbe.\n\n"
            "Von der Insel aus siehst du auch den Indianersteg - eine schmale Fußgängerbrücke, "
            "die die Insel mit dem anderen Ufer verbindet. Sie wurde achtzehnhundertdreiundsechzig als Holzbrücke gebaut. "
            "Ihren Namen verdankt sie spielenden Kindern, die auf der wackeligen Holzbrücke "
            "'Indianer' spielten.\n\n"
            "Heinrich stand einen Moment still unter den kahlen Platanen. Der Neckar rauschte "
            "auf beiden Seiten. Stocherkähne lagen vertäut am Ufer. Noch ein paar hundert Meter. "
            "Noch eine Brücke."
        ),
    },

    # 16 - Indianersteg (Raetsel / Finale)
    {
        "name": "Station 16 - Indianersteg (Finale)",
        "type": "raetsel",
        "story": (
            "Der Indianersteg - eine schmale Fußgängerbrücke über den Neckar. "
            "Heinrichs letzte Hürde.\n\n"
            "Die erste Holzbrücke wurde hier achtzehnhundertdreiundsechzig errichtet. Ihren Namen verdankt sie spielenden "
            "Kindern, die auf der wackeligen Konstruktion 'Indianer' spielten - ein Unfallbericht "
            "von achtzehnhunderteinundsiebzig ist das erste dokumentierte Zeugnis des Namens.\n\n"
            "Die Holzbrücke wurde um neunzehnhundert durch eine Eisenträgerbrücke ersetzt, dann neunzehnhundertelf durch "
            "eine Betonbogenbrücke - die gegen Ende des Zweiten Weltkriegs zerstört und danach "
            "einfacher wiederaufgebaut wurde. Heute hat sie smaragdgrüne Geländer.\n\n"
            "Heinrich überquerte die wackelige Holzbrücke in jener Novembernacht achtzehnhundertneunundsechzig. "
            "Auf der anderen Seite: Dunkelheit, Felder, Freiheit. Er hörte noch die Rufe der "
            "Gendarmen vom anderen Ufer. Aber es war zu spät. Der Forscher war verschwunden.\n\n"
            "Das letzte Fragment seiner Formel versteckte er unter einem losen Stein am "
            "Brückengeländer. Du stehst jetzt dort, wo Heinrich von Calw in die Freiheit ging."
        ),
        "diary": (
            "Der Steg wackelt unter meinen Schritten. Der Neckar ist schwarz und still. "
            "Auf der anderen Seite beginnt die Nacht, in der ich verschwinden werde. "
            "Über Rottenburg nach Süden. Die Schweizer Grenze.\n\n"
            "Meine Formel ist verteilt - Fragmente an verschiedenen Orten dieser Stadt, "
            "versteckt in Mauernischen, hinter losen Steinen, unter altem Holz. "
            "Wer sie alle findet, wird verstehen: Die gefährlichste Waffe ist nicht die "
            "Formel selbst. Es ist die Angst der Mächtigen vor dem freien Wissen.\n\n"
            "Lebe wohl, Tübingen."
        ),
        "fact": (
            "Achtzehnhundertneunundsechzig waren jenseits des Stegs nur nasse Wiesen und Felder - die Neckarauen. Die "
            "Südstadt entstand erst ab den achtzehnhundertachtziger Jahren, nachdem der Neckar reguliert "
            "und begradigt wurde.\n\n"
            "Der Hauptbahnhof stand seit achtzehnhunderteinundsechzig als einsames Gebäude in der Ebene. Die Kaserne kam "
            "erst achtzehnhundertdreiundsiebzig. Wer achtzehnhundertneunundsechzig über den Steg ging, verschwand buchstäblich "
            "in der Dunkelheit.\n\n"
            "Übrigens: Die heutige Betonbrücke ist schon die vierte Version. Holz (achtzehnhundertdreiundsechzig), "
            "Eisen (um neunzehnhundert), Betonbogen (neunzehnhundertelf, im Krieg zerstört), Wiederaufbau "
            "(neunzehnhundertsechsundvierzig). Die smaragdgrünen Geländer sind ein Markenzeichen."
        ),
        "riddle": (
            "Die erste Holzbrücke wurde achtzehnhundertdreiundsechzig errichtet. Welches Kinderspiel gab der Brücke "
            "ihren Namen? Ein Wort."
        ),
    },
]

# ============================================================
# SPEZIAL-AUDIO (Prolog + Anleitung)
# ============================================================

SPECIAL_AUDIO = {
    "prologue": {
        "voice": NARRATOR_VOICE,
        "text": (
            "Tübingen, im November des Jahres achtzehnhundertneunundsechzig. "
            "Das Königreich Württemberg unter König Karl dem Ersten erlebt turbulente Zeiten. "
            "Preußen rüstet auf, Europa balanciert am Rand eines Krieges, und in den Laboren "
            "der Universität wird an Entdeckungen gearbeitet, die alles verändern könnten.\n\n"
            "Professor Heinrich von Calw, ein brillanter Naturwissenschaftler, forscht in seinem "
            "Labor im Schloss Hohentübingen an einer revolutionären Energie-Formel. Offiziell "
            "arbeitet er an 'chemischen Grundlagen' für das Königliche Ministerium. In Wahrheit "
            "hat er etwas entdeckt, das die Kriegsführung und die Welt für immer verändern würde.\n\n"
            "Doch das Ministerium hat Wind bekommen. Gendarmen sind unterwegs, um sein Labor zu "
            "versiegeln und seine Aufzeichnungen zu konfiszieren. Heinrich hat vielleicht eine "
            "Stunde Vorsprung. Er greift sein Manuskript, zündet den Rest seiner Notizen an – "
            "und flieht vom Schloss bergab durch die Gassen der Altstadt.\n\n"
            "Sein Plan: den Neckar erreichen und über die Brücke am Stadtrand in die Dunkelheit "
            "verschwinden. Unterwegs versteckt er codierte Fragmente seines Werks an verschiedenen "
            "Orten – für den Fall, dass jemand Würdiges seine Spur findet.\n\n"
            "Dieser Jemand bist du.\n\n"
            "Du folgst Heinrichs Fluchtweg vom Schloss bergab, durch die Altstadt, bis zum Neckar. "
            "An siebzehn Orten hat er Spuren hinterlassen. An jeder Rätsel-Station findest du ein "
            "Fragment seiner Formel – acht Bruchstücke, die sich am Ende zu etwas Unerwartetem "
            "zusammensetzen.\n\n"
            "Deine Ermittlung beginnt oben am Schloss Hohentübingen."
        ),
    },
    "guide": {
        "voice": NARRATOR_VOICE,
        "text": (
            "So funktioniert's.\n\n"
            "Folge der Route. Die App führt dich von Station zu Station. Jede Station hat einen "
            "Maps-Link zur Navigation.\n\n"
            "Höre zu. Jede Station hat Audio: Story, Tagebuch, und nach dem Lösen einen "
            "Fakten-Track. An Info-Stationen gibt es einen Stadtführer-Track. Du kannst alles "
            "auch lesen.\n\n"
            "Löse Rätsel. An Rätsel-Stationen musst du vor Ort etwas finden oder beobachten. "
            "Nach richtiger Antwort wird der Fakten-Track freigeschaltet – und ein Fragment "
            "von Heinrichs geheimer Formel enthüllt.\n\n"
            "Entschlüssle die Formel. Acht Fragmente, verteilt über die ganze Route. Erst am "
            "Ende fügt sich alles zusammen. Was hat Heinrich wirklich versteckt?\n\n"
            "Sammle Traces. Für jede gelöste Station bekommst du Erfahrungspunkte. Am Ende "
            "wartet deine Urkunde.\n\n"
            "Der Ermittler-Assistent. Dein KI-Stadtführer kennt sich in Tübingen aus! Frag ihn "
            "nach Hinweisen zum Rätsel, aber auch nach Geschichte, Sehenswürdigkeiten oder allem, "
            "was du bei einer Stadtführung wissen willst. Er verrät nur nicht die Lösung.\n\n"
            "In der Gruppe? Nehmt einen Bluetooth-Lautsprecher mit! So hören alle entspannt die "
            "Geschichten und ihr könnt gemeinsam rätseln.\n\n"
            "Dein Fortschritt wird automatisch gespeichert. Du kannst jederzeit pausieren und "
            "später weitermachen."
        ),
    },
    "epilog": {
        "voice": "cgSgspJ2msm6clMCkdW9",  # Jessica - Playful, Bright, Warm
        "text": (
            "Herzlichen Glückwunsch! Du hast es geschafft – alle Fragmente gefunden und "
            "Heinrichs Geheimnis gelüftet!\n\n"
            "Die Formel, die Heinrich von Calw über die halbe Stadt verteilt hat, war nie eine "
            "physikalische Gleichung. Es war eine Erkenntnis – inspiriert von Friedrich Hölderlin, "
            "dem Dichter, der sechsunddreißig Jahre lang im Turm am Neckar lebte. Nur wenige "
            "hundert Meter von deiner letzten Station entfernt.\n\n"
            "Wo aber Gefahr ist, wächst das Rettende auch.\n\n"
            "Hölderlin schrieb diese Zeile achtzehnhundertdrei in seiner Hymne Patmos. "
            "Heinrich kannte seine Verse und verstand: Wo Wissen unterdrückt wird, wächst "
            "der Mut, es zu teilen.\n\n"
            "Vielen herzlichen Dank, dass du mit uns unterwegs warst! Wir hoffen, Tübingen "
            "hat dir gefallen. Teile deine Urkunde mit Freunden – und vielleicht sehen wir "
            "uns bald bei einer neuen Tour wieder."
        ),
    },
}

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
        station_nums = list(range(17))

    all_types = ["story", "diary", "fact", "riddle", "anecdote", "prologue", "guide"]
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
        "riddle": NARRATOR_VOICE,
        "anecdote": FACT_VOICE,
    }

    total = 0
    for i in station_nums:
        station = STATIONS[i]
        for audio_type in types_to_gen:
            if audio_type in station:
                total += 1
    total += len([t for t in types_to_gen if t in SPECIAL_AUDIO])

    done = 0
    errors = 0

    print("=" * 60)
    print("TraceTour Audio Generator - v6 (17 Stationen, 1869)")
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

    # Generate special audio (prologue, guide)
    special_types = [t for t in types_to_gen if t in SPECIAL_AUDIO]
    for stype in special_types:
        spec = SPECIAL_AUDIO[stype]
        filename = f"{stype}.mp3"
        output_path = OUTPUT_DIR / filename
        print(f"\nSpezial: {stype}")
        success = generate_audio(client, spec["text"], spec["voice"], output_path)
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
