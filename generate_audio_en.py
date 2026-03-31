#!/usr/bin/env python3
"""
TraceTour Audio Generator (English) -- ElevenLabs TTS
v1 -- 17 stations, 1869 story, full audio

Generates all audio files for the 17 stations:
  Puzzle stations (0,2,4,6,9,11,14,16):
    - story_X.mp3   (narrator voice)
    - diary_X.mp3   (Heinrich's voice)
    - fact_X.mp3    (fact voice)
    - riddle_X.mp3  (narrator voice, riddle text)
  Anecdote stations (1,3,5,7,8,10,12,13,15):
    - anecdote_X.mp3 (fact voice)

Usage:
  1. pip3 install elevenlabs
  2. python3 generate_audio_en.py
     python3 generate_audio_en.py --station 0,1,2
     python3 generate_audio_en.py --only story,diary
     python3 generate_audio_en.py --list-voices
"""

import os
import sys
import time
from pathlib import Path

try:
    from elevenlabs import ElevenLabs
except ImportError:
    print("ElevenLabs SDK not installed!")
    print("   pip3 install elevenlabs")
    sys.exit(1)

# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_18df17d38593a50a53362f37c86f9527c02d4c21ec495fc7")

# TODO: Florian picks English voices from ElevenLabs
NARRATOR_VOICE_EN = "PICK_NARRATOR_VOICE"   # English narrator (story, riddle)
HEINRICH_VOICE_EN = "PICK_HEINRICH_VOICE"   # Heinrich's diary (slightly accented English?)
FACT_VOICE_EN     = "PICK_FACT_VOICE"       # Guide/fact voice
EPILOG_VOICE_EN   = "PICK_EPILOG_VOICE"     # Jessica equivalent - bright, warm

MODEL_ID = "eleven_multilingual_v2"
OUTPUT_DIR = Path(__file__).parent / "audio" / "en"

# ============================================================
# ALL TEXTS FOR 17 STATIONS (ENGLISH)
# ============================================================

STATIONS = [
    # 0 - Castle Hohentübingen (Puzzle)
    {
        "name": "Station 0 - Castle Hohentuebingen",
        "type": "puzzle",
        "story": (
            "Castle Hohentuebingen — your starting point, high on a ridge above the old town. "
            "From up here you overlook the Neckar valley and the alleys below. It is November "
            "eighteen sixty-nine, just before nightfall.\n\n"
            "The castle was first mentioned in ten seventy-eight as castrum Tuibingensis, "
            "when troops of King Henry the Fourth besieged it in vain. In the sixteenth "
            "century, Duke Ulrich had the medieval fortress rebuilt as a Renaissance palace. "
            "The magnificent Lower Gate of sixteen oh seven — designed by master builder "
            "Heinrich Schickhardt — is styled as a triumphal arch. During the Thirty Years' "
            "War, French besiegers blew up the southeastern corner tower in sixteen forty-seven. "
            "It was never rebuilt — instead, the shorter pentagonal tower was constructed in "
            "sixteen sixty-seven.\n\n"
            "Since eighteen sixteen the castle has belonged to the university. In the cellar "
            "vaults, Professor Heinrich von Calw had his laboratory — the very place where, in "
            "eighteen sixty-nine, Friedrich Miescher actually discovered DNA. Heinrich had been "
            "conducting research here for three years, officially working on chemical foundations "
            "for the Royal Ministry. In truth, he had been working on a formula that could "
            "change everything.\n\n"
            "An hour ago, a telegram reached him: 'Gendarmes on their way. Leave the laboratory. "
            "Immediately.' Heinrich set his notes on fire, stuffed his manuscript into his coat, "
            "and fled down the steep Burgsteige. You are standing now where it all began."
        ),
        "diary": (
            "This is my last entry in this laboratory. The smell of burned paper still hangs "
            "in the air. Three years of research — and all that remains is a single manuscript "
            "beneath my coat.\n\n"
            "The Ministry wants my formula for weapons. I have lied, stalled, and misdirected "
            "for three years. Now time has run out. The gendarmes are on their way. I will hide "
            "coded fragments of my research at various locations throughout the city — in case "
            "someone worthy finds my trail. The first clue stays here, at the gate."
        ),
        "fact": (
            "The enormous wine barrel in the cellar was built in fifteen forty-eight and holds "
            "eighty-four thousand liters — the second largest in the world after Heidelberg. It "
            "can no longer be visited due to the bats living there.\n\n"
            "In the northeast tower, an astronomical observatory was established in seventeen "
            "fifty-two. Professor Bohnenberger built the state survey of Wuerttemberg from here "
            "starting in seventeen ninety-eight — the castle tower is the cartographic center of "
            "the state! All coordinates are measured from this point. He also invented the "
            "gyroscope.\n\n"
            "The Alte Kulturen museum displays Ice Age finds from caves of the Swabian Jura: "
            "forty-thousand-year-old ivory figurines — mammoths, the little wild horse, lions — "
            "the oldest artworks in human history. Plus an ancient Egyptian burial chamber. "
            "Since twenty twenty-three there is the Cafe Musee on the eastern bastion."
        ),
        "riddle": (
            "At the entrance gate of the castle you can see the Wuerttemberg coat of arms "
            "carved in stone. Which animal is the largest and most prominent on the coat of "
            "arms? One word."
        ),
    },

    # 1 - Student Prison (Anecdote)
    {
        "name": "Station 1 - Student Prison (Studentenkarzer)",
        "type": "anecdote",
        "anecdote": (
            "On your way downhill you pass the Studentenkarzer at Muenzgasse twenty — the "
            "university prison where Tuebingen students were locked up since fifteen fifteen. "
            "The oldest surviving university prison in Germany. The university held its own "
            "judicial authority since its founding in fourteen seventy-seven — it was permitted "
            "to punish its students itself.\n\n"
            "Heinrich knew the prison well. As a student, he spent two nights here for "
            "night wandering — he had secretly stayed in the laboratory overnight. The cells "
            "are tiny: two connected vaulted rooms totaling just fifteen square meters with "
            "small window openings. The walls are covered with inscriptions and drawings by "
            "the inmates. In seventeen thirty-six, the painter Johann Gottfried Schreiber "
            "painted the walls with religious and classical motifs — a kind of prison art.\n\n"
            "Offenses that led to the prison: walking around at night without a lamp, "
            "skipping sermons, gambling, and wearing deliberately fashionably slashed clothing. "
            "The prison was in operation until eighteen forty-five — just within Heinrich's "
            "student years. The building is now a protected cultural monument.\n\n"
            "Heinrich hurried past without stopping. The gendarmes would search the castle "
            "first, then head down the Muenzgasse. He had maybe twenty minutes left."
        ),
    },

    # 2 - Old Assembly Hall (Puzzle)
    {
        "name": "Station 2 - Old Assembly Hall (Alte Aula)",
        "type": "puzzle",
        "story": (
            "The Alte Aula at Muenzgasse thirty — right next to the Stiftskirche, one of the "
            "oldest university buildings in Germany. The predecessor was built in fourteen "
            "seventy-seven, the same year the university was founded. In the attic, grain was "
            "stored as part of the professors' salaries — academics were paid in kind back "
            "then.\n\n"
            "After the fire of fifteen thirty-four, the current building was constructed in "
            "fifteen forty-seven. During the renovation of seventeen seventy-seven for the "
            "university's three hundredth anniversary, the north side received its classicist "
            "facade. Due to the height difference to Bursagasse, the building has four stories "
            "on one side and seven on the other. The Clinicumsgasse leads through a small "
            "tunnel right through the middle of the building.\n\n"
            "In twenty twelve the Alte Aula underwent extensive renovation — during which "
            "original ceiling paintings from fifteen forty-seven were uncovered. Sixty thousand "
            "books from the education library moved back across four levels.\n\n"
            "Heinrich ducked through the side entrance that he knew as a professor. In the "
            "great hall, behind the lectern, he slid the first coded fragment of his research "
            "behind a loose wooden panel. Useless without the other fragments."
        ),
        "diary": (
            "In the library of the Alte Aula, behind the theological treatises, I once found "
            "the Arabic manuscript that changed everything. Today I am hiding my own work in "
            "this place. I hope it has better luck than I do."
        ),
        "fact": (
            "The University of Tuebingen is the fifth-oldest in the German-speaking world. "
            "Eberhard im Bart founded it in fourteen seventy-seven with just eleven professors "
            "and three hundred students. Philipp Melanchthon studied here and later taught "
            "Greek grammar at Wittenberg — at just twenty-one years old! And the young Kepler "
            "was nearly expelled for his astronomical ideas.\n\n"
            "From sixteen sixty-three to eighteen oh four, the Hortus Medicus — the university's "
            "botanical garden where the botanist Camerarius conducted his research — was located "
            "right next to the Alte Aula. Today it is a parking lot.\n\n"
            "By the way: This building has only been called the Old Aula since the New Aula "
            "was built in eighteen forty-five. Before that, it was simply the Aula."
        ),
        "riddle": (
            "On the information board of the Alte Aula you will find two years: the year of "
            "construction and the year of the renovation for the three hundredth university "
            "anniversary. Subtract three hundred from the renovation year — in what year was "
            "the University of Tuebingen founded?"
        ),
    },

    # 3 - Martinianum (Anecdote)
    {
        "name": "Station 3 - Martinianum, Muenzgasse 13",
        "type": "anecdote",
        "anecdote": (
            "Heinrich hurried down the Muenzgasse. In passing, his gaze caught a small sign "
            "on a house wall — the most famous sign in Tuebingen. Hier kotzte Goethe. Goethe "
            "threw up here.\n\n"
            "Johann Wolfgang von Goethe arrived in Tuebingen on September seventh, seventeen "
            "ninety-seven, and stayed until September sixteenth — he departed at four in the "
            "morning. Schiller had recommended the publisher Cotta to him, and Goethe stayed "
            "next door at Muenzgasse fifteen. On his first evening, the pharmacist Doctor "
            "Christian Gmelin invited him to dinner. His verdict on the city: The town itself "
            "is abominable, but one only needs to take a few steps to see the most beautiful "
            "countryside. He praised the Stiftskirche windows as magnificent splendor, but "
            "harshly criticized the university — and made dismissive remarks about Hoelderlin "
            "to Schiller.\n\n"
            "The sign Hier kotzte Goethe at Muenzgasse thirteen is a cheeky counter-comment "
            "to the distinguished marble plaque on the neighboring Cottahaus — not a historical "
            "event, but satirical protest against the excessive Goethe cult.\n\n"
            "Heinrich had lived here for a time before moving to his laboratory at the castle. "
            "The room on the second floor, sparse but quiet. From his window he could survey "
            "the narrow Muenzgasse — and see anyone coming up. A useful trait that he could "
            "have used today."
        ),
    },

    # 4 - Stiftskirche (Puzzle)
    {
        "name": "Station 4 - Stiftskirche (Collegiate Church)",
        "type": "puzzle",
        "story": (
            "The Stiftskirche Saint Georg — the spiritual heart of the old town. Heinrich "
            "reached the church breathless. The old sexton, a friend from his student days, "
            "let him in through the side entrance.\n\n"
            "Five minutes, whispered Heinrich. The sexton nodded. In a confessional in the "
            "back left corner, there is a loose stone. Heinrich pushed the second fragment "
            "behind it.\n\n"
            "The Stiftskirche with its distinctive tower is one of the most significant Late "
            "Gothic buildings in Wuerttemberg. When the Gothic church was built starting in "
            "fourteen seventy, the old Romanesque predecessor remained in operation — the new "
            "church was literally built around the old one, which was only demolished afterward. "
            "In the choir area there are fourteen stone tomb monuments of Wuerttemberg rulers "
            "and their families — including Duke Eberhard im Bart, the university's founder.\n\n"
            "By the way: The tower leans eight centimeters to the northwest — not because of "
            "its age, but because of construction work in the twentieth century that disturbed "
            "the ground. And the Dominica bell from fourteen eleven, weighing three thousand "
            "three hundred kilograms, still rings today. On Sundays at eight thirty in the "
            "morning, a brass ensemble plays Bach from the tower."
        ),
        "diary": (
            "The sexton recognized me and asked no questions. There are still good people in "
            "this city. I hid the fragment behind the third stone on the left in the rear "
            "confessional. May it remain safe there for a long time."
        ),
        "fact": (
            "Eberhard im Bart was initially buried elsewhere and only transferred to the "
            "Stiftskirche around fifteen thirty-five. His tomb shows him praying with his "
            "favorite motto: Attempto — I dare. This motto is still the official motto of "
            "the University of Tuebingen today.\n\n"
            "The medieval rood screen — an elaborate partition between choir and nave — survived "
            "only because Duke Ulrich relocated the burial site to the choir in fifteen "
            "thirty-four. Without that decision, it would have been torn down as in most other "
            "churches. It is considered one of the finest Gothic rood screens in Swabia.\n\n"
            "The choir windows date from fourteen seventy-five — created by Peter Hemmel von "
            "Andlau, one of the most important glass painters of his time, who also worked for "
            "Ulm, Augsburg, and Strasbourg Cathedral. The high altar of fifteen thirty-six was "
            "less fortunate: it fell victim to the Protestant iconoclasm.\n\n"
            "Look up at the tower: The four evangelist figures on the tower pinnacles — Luke as "
            "a bull, Matthew as an angel, Mark as a lion, John as an eagle — date only from "
            "nineteen thirty-two, created by the sculptor Fritz von Graevenitz.\n\n"
            "The tower warden's apartment halfway up was inhabited until nineteen forty-eight! "
            "The last tower warden was Karl Weihenmaier, who lived there with his entire "
            "family — one hundred sixty-nine steps above the city."
        ),
        "riddle": (
            "Look closely at the church tower of the Stiftskirche. How tall is it? During "
            "construction, the money ran out — the tower ended up shorter than planned!"
        ),
    },

    # 5 - Holzmarkt & St. George's Fountain (Anecdote)
    {
        "name": "Station 5 - Holzmarkt & St. George's Fountain",
        "type": "anecdote",
        "anecdote": (
            "Heinrich left the Stiftskirche through the north exit and stood on the Holzmarkt — "
            "the elongated square north of the church. It used to be called Hafenmarkt because "
            "pottery from the nearby Hafengasse was sold here — Hafen is Swabian for pot. The "
            "old name still appears on the cadastral map of eighteen nineteen.\n\n"
            "The square used to be noticeably narrower and steeper. Only around eighteen thirty, "
            "when the Gasthaus Adler that jutted far into the square was demolished, did it gain "
            "its current width. And after the city fire of seventeen eighty-nine, the crest at "
            "the eastern end was significantly lowered.\n\n"
            "The Georgsbrunnen — actually called Joergenbrunnen — depicts Saint George slaying "
            "the dragon. The fifteen twenty-three original was removed in eighteen forty-one, "
            "replaced by a neo-Gothic cast-iron version in eighteen forty-two — and that one "
            "was removed in nineteen sixty-one. For parking spaces. Seriously. In nineteen "
            "seventy-six the fountain returned when the Holzmarkt became a pedestrian zone. "
            "The original fifteen twenty-three George figure ended up in the Neckar at some "
            "point — in nineteen eleven the art historian Konrad Lange fished out the upper "
            "body. It now stands in the city museum. In nineteen seventy-nine, vandals broke "
            "off the new George's lance and arm.\n\n"
            "At the corner to the Muenzgasse lies the Heckenhauer antiquarian bookshop, "
            "Holzmarkt five — where the young Hermann Hesse worked as an apprentice. Inside "
            "the shop there is a small Hermann Hesse cabinet.\n\n"
            "Heinrich crossed the Holzmarkt hastily. The wide steps in front of the "
            "Stiftskirche — which still serve today as a bench for tourists, school classes, "
            "and demonstrators — were empty. He lowered his head and moved on."
        ),
    },

    # 6 - Town Hall & Astronomical Clock (Puzzle)
    {
        "name": "Station 6 - Town Hall & Astronomical Clock",
        "type": "puzzle",
        "story": (
            "The Marktplatz — the heart of the city, barely changed for over a hundred years. "
            "The small cobblestones, the little shop windows, the restored half-timbered "
            "houses — all original. On Mondays, Wednesdays, and Fridays there is a weekly "
            "market with around forty stalls of regional produce. On summer evenings the square "
            "belongs to the students, who gather at the Neptune Fountain with drinks they "
            "brought — and occasionally cool off in it.\n\n"
            "The Neptune Fountain was designed in sixteen seventeen by Heinrich Schickhardt — "
            "inspired by the famous Neptune Fountain in Bologna, which Schickhardt had seen on "
            "his Italian travels. The Neptune figure itself was cast by WMF — yes, the "
            "kitchenware company — from melted-down Wehrmacht weapons released by the French "
            "occupation. If you look closely, you will discover hidden silhouette portraits "
            "of the craftsmen in the water spouts — with cigars in their mouths.\n\n"
            "The magnificent Town Hall stands at the head of the square, its facade richly "
            "painted. The astronomical clock on the side shows not only the time but also moon "
            "phases, zodiac signs, and the orbits of the planets. The staircase next to the "
            "Town Hall is deliberately crooked — it follows the old drainage channel that once "
            "ran through the middle of the square.\n\n"
            "The square has a turbulent history: fires in fourteen seventy-six and fifteen "
            "forty destroyed the surrounding houses. Each time the square was rebuilt a little "
            "larger — beneath the pavement, remnants of old cellars remain as proof. In "
            "nineteen thirty-six, Ferry Porsche drove a prototype of his Volkswagen right past "
            "the Neptune Fountain — one of the earliest photos of the later Beetle. And in "
            "nineteen sixty-three, circus elephants stood in the middle of the square.\n\n"
            "Heinrich blended in with the last visitors and hid a fragment in a wall niche "
            "beneath the Town Hall."
        ),
        "diary": (
            "The Marktplatz was still bustling. Too bustling. I ducked behind the Neptune "
            "Fountain and waited until a group of students had passed. My heart was pounding "
            "in my throat.\n\n"
            "I hid the fragment in a wall niche beneath the Town Hall. My hands were trembling. "
            "How much time do I have left? The gendarmes cannot be far. I must reach the Neckar "
            "before they seal off the Marktplatz."
        ),
        "fact": (
            "The astronomical clock was designed in fifteen eleven by the astronomer Johannes "
            "Stoeffler. The dragon hand marks the lunar nodes and predicts eclipses. Stoeffler "
            "predicted a great flood for February fifteen twenty-four — all of Europe panicked, "
            "people built arks. It rained a little. Stoeffler died in fifteen thirty-one of "
            "the plague, not a flood.\n\n"
            "The Cafe Ranitzky on the square looks like old half-timbering — but it is a modern "
            "reconstruction. The original, the Cafe Pfuderer, burned down in the nineteen "
            "seventies. The building was rebuilt in the same exterior style, hence the "
            "suspiciously precise timber framing.\n\n"
            "The Mayersche Apotheke at the market, number thirteen, was founded in fifteen "
            "sixty-nine — one of the oldest pharmacies in Wuerttemberg. It closed at the end "
            "of twenty seventeen after nearly four hundred fifty years."
        ),
        "riddle": (
            "Stand in front of the Town Hall facade and count the painted names of famous "
            "figures. How many are there? Tip: One is hiding near the very top — easy to miss!"
        ),
    },

    # 7 - City Museum in the Kornhaus (Anecdote)
    {
        "name": "Station 7 - City Museum in the Kornhaus",
        "type": "anecdote",
        "anecdote": (
            "From the Marktplatz, Heinrich passed the Kornhaus — the building that today houses "
            "the City Museum. Built in fourteen fifty-three as a covered grain market, it has "
            "served many purposes over the centuries: banquet hall for dances and theater, boys' "
            "and girls' school, fire station, and Red Cross station — before it opened as the "
            "City Museum in nineteen ninety-one.\n\n"
            "What awaits you inside: a working replica of Wilhelm Schickard's mechanical "
            "calculator from sixteen twenty-three — the first calculating machine in the world, "
            "decades before Pascal's famous model. Reconstructed between nineteen fifty-seven "
            "and nineteen sixty by Tuebingen professor Bruno von Freytag-Loeringhoff based on "
            "Schickard's correspondence with Kepler. And it still calculates!\n\n"
            "Also worth seeing: the permanent exhibition on Lotte Reiniger, the pioneer of "
            "silhouette animation film. The exposed timber framing of the Kornhaus defines the "
            "rooms — though during the nineteen eighties renovation, cement-based mortar was "
            "used, which actually destroys timber framing. A Tuebingen master carpenter "
            "remarked: More damage was done here than in the last hundred years of wind and "
            "weather.\n\n"
            "Curious story: In two thousand two, it was discovered that a museum employee had "
            "stolen one hundred thirteen objects. One hundred three of them were recovered.\n\n"
            "Admission has been free since April twenty eighteen. Sundays at three in the "
            "afternoon there is a guided tour — five euros for adults, children free.\n\n"
            "Heinrich had no time for museums. He turned into Kornhausstrasse and hurried "
            "downhill toward Ammergasse."
        ),
    },

    # 8 - Ammerschlag (Anecdote)
    {
        "name": "Station 8 - Ammerschlag",
        "type": "anecdote",
        "anecdote": (
            "Heinrich needed a break. And a plan. He ducked into the Ammerschlag — one of the "
            "oldest pubs in Tuebingen at Ammergasse thirteen.\n\n"
            "Legend has it that the Ammerschlag goes back to a goatherd who built his house "
            "here before the castle even existed. Over the centuries, the Ziegenschlag — goat "
            "pen — became the Ammerschlag. Napoleon supposedly stopped here on his campaigns "
            "to rest. Whether that is true? The pub claims it, at any rate.\n\n"
            "A peculiarity: The Ammerschlag is one of the few restaurants in Germany where "
            "smoking is still allowed everywhere — completely. No non-smoking area.\n\n"
            "Heinrich ordered a quarter-liter of Trollinger, drank it in one go, laid two "
            "Kreuzer on the bar, and disappeared through the back door. The barkeeper shrugged. "
            "In this pub, nobody asked questions.\n\n"
            "Open: Sunday to Thursday three in the afternoon to one in the morning, Friday and "
            "Saturday ten in the morning to three in the morning."
        ),
    },

    # 9 - Haagtorplatz (Puzzle)
    {
        "name": "Station 9 - Haagtorplatz",
        "type": "puzzle",
        "story": (
            "Heinrich hurried westward through the Ammergasse and reached the Haagtorplatz — "
            "officially called Vor dem Haagtor, Before the Haag Gate. Here stood the Haagtor "
            "until eighteen thirty-one, one of five city gates of the medieval fortifications. "
            "The gate led westward toward Herrenberg, along the Ammer river.\n\n"
            "The square was much smaller until nineteen sixty-three. Only when the Schweickhardt "
            "mill on the Ammer canal was demolished did the current open area emerge. In "
            "nineteen ninety-two the square was redesigned and the Ammer canal uncovered — "
            "celebrated with an open-air screening of Die Feuerzangenbowle. Since then, the "
            "winter cinema screening of this film classic on the Friday before the third Sunday "
            "of Advent has become tradition.\n\n"
            "In summer, part of the square transforms into Haagtor-Space: Hollywood swings, "
            "sandbox, flower boxes — where parking spaces used to be. A project born from a "
            "citizens' initiative in twenty twenty-two.\n\n"
            "Heinrich still remembered the square with its gate. He hid a fragment in a wall "
            "niche and continued toward Froschgasse."
        ),
        "diary": (
            "The Haagtor is gone. Demolished. Eighteen thirty-one, they say. The foundations "
            "are still there, beneath the pavement. Just as my formulas will soon lie beneath "
            "the dust of this city. Invisible, but not lost."
        ),
        "fact": (
            "Tuebingen's five city gates were called: Lustnauer Tor in the east, Haagtor in "
            "the west, Schmiedtor in the north, Neckartor in the south, and the Hirschauer "
            "Tor. They were all demolished between eighteen oh five and eighteen thirty-one.\n\n"
            "The marker in the pavement next to the Ammer canal commemorates the Schweickhardt "
            "Mill, formerly the Lower Haagtor Mill, demolished in nineteen sixty-three. Through "
            "the bicycle tunnel at the square, you can reach the Neckar, the Anlagensee, and "
            "the train station directly.\n\n"
            "Fun fact: When the Haagtor was demolished in eighteen thirty-one, citizens "
            "protested — not because of the history, but because the gatekeeper lost his job. "
            "He received a severance of fifty Gulden."
        ),
        "riddle": (
            "Look around the Haagtorplatz. On a building wall there is a bird as street art — "
            "colorful and detailed. Which bird is it? One word."
        ),
    },

    # 10 - Frog King Fountain (Anecdote)
    {
        "name": "Station 10 - Frog King Fountain",
        "type": "anecdote",
        "anecdote": (
            "On his way from the Haagtorplatz to the Affenfelsen, Heinrich passed the fountain "
            "in front of Cafe Hirsch. An inconspicuous well shaft, seven meters deep.\n\n"
            "Today this fountain has a special story: For years it was stuffed with a meter of "
            "garbage. School children visiting it during a city quiz looked in with disgust. In "
            "twenty twenty-four, Petra Wenzel, a dedicated citizen from Cafe Hirsch, took "
            "matters into her own hands. The city helped with heavy equipment — gas masks, "
            "industrial hoses, the full works.\n\n"
            "In spring twenty twenty-five, a handmade Frog King made of clay was installed — "
            "forty by forty centimeters, colorfully painted, and illuminated at night by a "
            "solar lamp. He looks directly at Tuebingen's Froschgasse — Frog Lane. A glass "
            "plate protected him from the weather.\n\n"
            "But in October twenty twenty-five the Frog King was stolen — someone pushed the "
            "glass plate aside and hoisted him out. It is so sad for all the children, said "
            "Wenzel. She immediately ordered a new one. Check whether he is back yet!\n\n"
            "Heinrich did not notice the fountain. He had other worries."
        ),
    },

    # 11 - Affenfelsen (Puzzle)
    {
        "name": "Station 11 - Affenfelsen (Monkey Rock)",
        "type": "puzzle",
        "story": (
            "From the Haagtorplatz, Heinrich continued to the Affenfelsen — a remnant of the "
            "city wall at the edge of the old town, where the Ammer canal flows through a gate "
            "beneath the old wall.\n\n"
            "The name sounds odd: Affenfelsen — Monkey Rock. It probably comes from children "
            "climbing on the wall remnants and young people hanging out here in summer.\n\n"
            "At the Affenfelsen, something special happens: the Ammer canal splits. One branch "
            "flows culverted beneath Muehlstrasse to the Neckar — on this downhill stretch it "
            "once powered the mills. The other branch flows beneath the Old Botanical Garden "
            "back to the Ammer. A still-functioning sluice regulates water flow during floods. "
            "Medieval water management that still works today.\n\n"
            "In summer, the area around the Affenfelsen transforms into a lively cafe terrace — "
            "San Marco, Tre Pi, and Piccolo Sole d'Oro in Metzgergasse invite you to linger.\n\n"
            "Heinrich watched the water and briefly considered following the canal. But no — "
            "his path led onward."
        ),
        "diary": (
            "At the Affenfelsen. The water of the Ammer flows beneath the old wall — calm, "
            "steady, without caring about gendarmes or formulas. At the sluice, the canal "
            "splits into two branches. I wish I could split myself too — one Heinrich who "
            "flees, and one who stays."
        ),
        "fact": (
            "The Tuebingen city wall was built in the thirteenth century and was about one and "
            "a half kilometers long. At the Affenfelsen you can see particularly well how thick "
            "the walls were — over one meter.\n\n"
            "The artwork Radfahrerkoenig — Cycling King — is by Tuebingen artist Suse "
            "Mueller-Diefenbach. At the Affenfelsen, the Ammer canal splits: one branch flows "
            "via Muehlstrasse to the Neckar, the other back to the Ammer. The historic sluice "
            "is still preserved and functional.\n\n"
            "The restaurant terraces at the Affenfelsen — San Marco, Tre Pi, Piccolo Sole "
            "d'Oro — make the square one of the most popular meeting spots in the old town "
            "in summer."
        ),
        "riddle": (
            "At the Affenfelsen there is an artwork by a Tuebingen artist. It shows a figure "
            "on an unusual vehicle. What kind of king is it? One compound word including "
            "the vehicle."
        ),
    },

    # 12 - Old Botanical Garden (Anecdote)
    {
        "name": "Station 12 - Old Botanical Garden",
        "type": "anecdote",
        "anecdote": (
            "Heinrich made a detour eastward and cut through the Old Botanical Garden — the "
            "Bota, as the locals call it. Laid out between eighteen oh five and eighteen oh "
            "nine, it is today a popular park. From its original use, rare exotic trees still "
            "stand — including mature ginkgos that are protected as natural monuments.\n\n"
            "What most people do not know: Before the garden, this was a university sports "
            "field — with a crossbow shooting range and tournament ground. And the area north "
            "of the Ammer was a cemetery until eighteen twenty-nine, the Ammerkirchof. After "
            "its dissolution around eighteen fifty, the grounds became an arboretum.\n\n"
            "Heinrich paused briefly. In the eastern part of the garden stood a marble "
            "monument — Friedrich Hoelderlin, in a Hellenically idealized pose, erected in "
            "eighteen eighty-one by the sculptor Emmerich Andresen. Heinrich knew Hoelderlin's "
            "verses by heart. On this night, they held a special meaning for him. He lowered "
            "his head and walked on.\n\n"
            "Until nineteen seventy, a beautiful palm house in the Neo-Renaissance style stood "
            "at the northern edge — a jewel of cast iron and glass, built in eighteen "
            "eighty-six. It was demolished despite fierce citizen protests when the Botanical "
            "Garden moved to the Morgenstelle. The cast-iron door wings were saved and are to "
            "be re-erected one day.\n\n"
            "Heinrich crossed the garden and emerged at Wilhelmstrasse — directly opposite the "
            "New Aula."
        ),
    },

    # 13 - New Aula (Anecdote)
    {
        "name": "Station 13 - New Aula (Neue Aula)",
        "type": "anecdote",
        "anecdote": (
            "The Neue Aula — the imposing main building of the university, built from eighteen "
            "forty to eighteen forty-five by court architect Gottlob Georg Barth in the "
            "classicist style. Temple-like, the building represents the self-confidence of the "
            "nineteenth century. On the pediment, Attempto gleams in gold letters — I dare — "
            "the university's motto since its founding in fourteen seventy-seven.\n\n"
            "Inside, a labyrinth of corridors and staircases, halls and columns, adorned with "
            "busts of Schiller, Goethe, and Duke Eberhard im Bart. The extension toward "
            "Hoelderlinstrasse was added from nineteen twenty-eight to nineteen thirty-two — "
            "with a festival hall and the main auditorium. Right at the entrance from "
            "Wilhelmstrasse hang memorial plaques for resistance fighters of July twentieth, "
            "nineteen forty-four, who once studied here.\n\n"
            "In front of the Aula lies the Geschwister-Scholl-Platz with two bronze fountains "
            "from eighteen seventy-seven, recast in two thousand one. In twenty eighteen, "
            "someone dyed the fountain water neon green — Tuebingen humor.\n\n"
            "Heinrich had given his last lecture here before the Ministry placed him under "
            "surveillance. He glanced briefly at the illuminated windows. Farewell, university, "
            "he murmured. Then he turned away and headed downhill toward the Ammer quarter."
        ),
    },

    # 14 - Nonnenhaus (Puzzle)
    {
        "name": "Station 14 - Nonnenhaus (Nuns' House)",
        "type": "puzzle",
        "story": (
            "The Nonnenhaus — at thirty meters in length, one of the largest half-timbered "
            "houses in Tuebingen's old town, built in fourteen eighty-eight. The name is "
            "misleading: first Dominican nuns lived here, then Beguines — women of a lay "
            "Christian community without monastic vows. After the Reformation in fifteen "
            "thirty-four, the convent was dissolved.\n\n"
            "Afterward, the medical professor and botanist Leonhard Fuchs moved in — born "
            "fifteen oh one, died fifteen sixty-six — with his wife and ten children! He "
            "established one of the oldest botanical gardens in Europe next to the house and "
            "wrote his famous New Kreuterbuch here in fifteen forty-three. The fuchsia was "
            "named after him, although he never saw the plant. In front of the house today "
            "there is a small memorial garden with plants from his book.\n\n"
            "Heinrich hid his second-to-last fragment in the Nonnenhaus — in a cavity behind "
            "the old wooden paneling.\n\n"
            "And then there is the back of the house. On the first floor, a wooden bay "
            "protrudes far out over the Ammer canal. Why this elaborate construction directly "
            "over the water? The answer is practical, medievally efficient — and quite funny."
        ),
        "diary": (
            "The Nonnenhaus. Fourteen eighty-eight. The beams creak under my steps as if in "
            "protest. I have hidden my second-to-last fragment here — where the Beguines once "
            "committed their earthly needs directly to the water. Nobody searches in such "
            "places."
        ),
        "fact": (
            "The Sprachhaus at the Nonnenhaus is one of the best-preserved examples of "
            "medieval sanitation in southern Germany. The principle was simple: gravity did "
            "the rest, and the Ammer canal flushed everything away.\n\n"
            "The building was exemplarily restored in twenty oh seven and twenty oh eight and "
            "received the twenty oh eight Baden-Wuerttemberg Heritage Conservation Award. On "
            "the ground floor of today's bookshop, a viewing window is set into the floor — "
            "showing the original brick screed from fourteen eighty-eight!\n\n"
            "Leonhard Fuchs described over four hundred plants in his New Kreuterbuch of "
            "fifteen forty-three — with hand-colored woodcuts. His botanical garden next to "
            "the house was one of the oldest in all of Europe."
        ),
        "riddle": (
            "Look at the back of the Nonnenhaus. On the first floor, a wooden oriel extends "
            "across the alley all the way over the Ammer canal. Why was it built to extend so "
            "far over the water? What was its function? One word."
        ),
    },

    # 15 - Neckar Island & Plane Tree Avenue (Anecdote)
    {
        "name": "Station 15 - Neckar Island & Plane Tree Avenue",
        "type": "anecdote",
        "anecdote": (
            "Heinrich reached the Neckarinsel — the narrow island in the middle of the river. "
            "He was almost at his destination now.\n\n"
            "The Platanenallee is three hundred eighty meters long, with forty-two plane trees "
            "on each side. It is the oldest surviving plane tree avenue in Germany. For a long "
            "time, city guides told the story that the last executioner planted the trees. In "
            "twenty thirteen, a dendrochronological study proved otherwise: the trees germinated "
            "between eighteen twenty-two and eighteen twenty-four. In the city archives, a "
            "receipt from January twenty-eighth, eighteen twenty-eight was found — ninety-six "
            "plane trees from the Hohenheim state nursery, for thirty-two Gulden. They were "
            "planted by the city warden Philipp Jakob Hornung.\n\n"
            "A twenty twenty-two expert assessment found that the trees will last approximately "
            "another fifty years. Some support each other via inconspicuous wire cables.\n\n"
            "From here you can see the Hoelderlin Tower at the eastern end — and at the western "
            "end the Silcher monument, where the path continues into the Seufzerwaeldchen, the "
            "Little Sighing Forest. At the Nadeloehr — the Needle's Eye — leading to the Neckar "
            "bridge stands a pigeon tower — for organized egg theft to control the pigeon "
            "population.\n\n"
            "Heinrich stood still for a moment beneath the bare plane trees. The Neckar rushed "
            "on both sides. Punting boats lay moored at the shore. Just a few hundred meters "
            "more. One more bridge."
        ),
    },

    # 16 - Indianersteg (Puzzle / Finale)
    {
        "name": "Station 16 - Indianersteg (Finale)",
        "type": "puzzle",
        "story": (
            "The Indianersteg — a narrow pedestrian bridge from the Uhland monument at the "
            "Platz der Stadt Monthey to the Neckar Island. Heinrich's last hurdle.\n\n"
            "The first wooden bridge was built here in eighteen sixty-three. It owes its name "
            "to children who played Indians on the wobbly construction — an accident report "
            "from eighteen seventy-one is the first documented mention of the name.\n\n"
            "What you see today is already the fourth bridge at this location: wood, eighteen "
            "sixty-three. Iron truss, around nineteen hundred. Concrete arch bridge, nineteen "
            "eleven, with a wider span due to the Neckar regulation — and that one was destroyed "
            "shortly before the war's end in nineteen forty-five by the retreating Wehrmacht, "
            "like all Tuebingen Neckar bridges except the Eberhardsbruecke. The reconstruction "
            "was done in simpler form. The emerald-green railings remain its trademark to this "
            "day.\n\n"
            "Starting in twenty twenty-six, the bridge will be renovated for three hundred "
            "seventy-five thousand euros.\n\n"
            "Heinrich crossed the wobbly wooden bridge on that November night in eighteen "
            "sixty-nine. On the other side: darkness, fields, freedom. He could still hear "
            "the shouts of the gendarmes from the far bank. But it was too late. The researcher "
            "had vanished.\n\n"
            "He hid the last fragment of his formula under a loose stone at the bridge railing. "
            "You are standing now where Heinrich von Calw walked into freedom."
        ),
        "diary": (
            "The bridge sways under my steps. The Neckar is black and still. On the other side "
            "begins the night in which I will disappear. Via Rottenburg to the south. The Swiss "
            "border.\n\n"
            "My formula is distributed — fragments at various locations throughout this city, "
            "hidden in wall niches, behind loose stones, under old timber. Whoever finds them "
            "all will understand: the most dangerous weapon is not the formula itself. It is "
            "the fear of the powerful in the face of free knowledge.\n\n"
            "Farewell, Tuebingen."
        ),
        "fact": (
            "In eighteen sixty-nine, beyond the bridge there were only wet meadows and fields — "
            "the Neckar floodplains. The southern part of the city only emerged from the "
            "eighteen eighties onward, after the Neckar was regulated and straightened. The "
            "main train station had stood since eighteen sixty-one as a solitary building on "
            "the plain.\n\n"
            "All Tuebingen Neckar bridges except the Eberhardsbruecke were blown up by the "
            "Wehrmacht in nineteen forty-five. Including the nineteen eleven concrete arch "
            "bridge at the Indianersteg. What we see today is the fourth bridge at this "
            "location.\n\n"
            "The Pons Ilonae renaming of twenty sixteen was actually a hoax on a local internet "
            "portal that went unnoticed for years. And whether the name Indianersteg itself "
            "will come under discussion remains to be seen — the Tagblatt cautiously called it "
            "the bridge whose name must not be spoken in twenty twenty-five."
        ),
        "riddle": (
            "The first wooden bridge was built in eighteen sixty-three. Which children's game "
            "gave the bridge its name? One word."
        ),
    },
]

# ============================================================
# SPECIAL AUDIO (Prologue + Guide + Epilog)
# ============================================================

SPECIAL_AUDIO = {
    "prologue": {
        "voice": NARRATOR_VOICE_EN,
        "text": (
            "Tuebingen, November eighteen sixty-nine. The Kingdom of Wuerttemberg under King "
            "Karl the First is living through turbulent times. Prussia is arming, Europe "
            "teeters on the brink of war, and in the university laboratories, discoveries "
            "are being made that could change everything.\n\n"
            "Professor Heinrich von Calw, a brilliant natural scientist, conducts research "
            "in his laboratory at Castle Hohentuebingen on a revolutionary energy formula. "
            "Officially he works on chemical foundations for the Royal Ministry. In truth, he "
            "has discovered something that could change warfare — and the world — forever.\n\n"
            "But the Ministry has caught wind. Gendarmes are on their way to seal his "
            "laboratory and confiscate his records. Heinrich has perhaps an hour's head start. "
            "He grabs his manuscript, sets fire to the rest of his notes — and flees from the "
            "castle downhill through the alleys of the old town.\n\n"
            "His plan: reach the Neckar and disappear across the bridge at the edge of town "
            "into the darkness. Along the way he hides coded fragments of his work at various "
            "locations — in case someone worthy finds his trail.\n\n"
            "That someone is you.\n\n"
            "From Heinrich's notebook: Whoever possesses the formula possesses the power to "
            "destroy cities or to liberate humanity. I entrust it to no king — only to the "
            "wind and the stones of this city.\n\n"
            "You follow Heinrich's escape route from the castle downhill, through the old town, "
            "to the Neckar. At seventeen locations he left traces. At each puzzle station you "
            "will find a fragment of his formula — eight pieces that come together at the end "
            "to form something unexpected.\n\n"
            "Your investigation begins up at Castle Hohentuebingen."
        ),
    },
    "guide": {
        "voice": NARRATOR_VOICE_EN,
        "text": (
            "How it works.\n\n"
            "Follow the route. The app has a built-in map with your location and the path to "
            "the next station. Tap Map to open it. With each solved station, the next point "
            "appears on the map. Alternatively, you can use the navigation links to open "
            "Google Maps.\n\n"
            "Listen. Each station has audio: story, diary, and after solving a facts track. "
            "At info stations there is a city guide track. You can also read everything.\n\n"
            "Solve puzzles. At puzzle stations you need to find or observe something on "
            "location. After a correct answer, the facts track is unlocked — and a fragment "
            "of Heinrich's secret formula is revealed. Do not worry: if you get stuck, we will "
            "show you the answer after a few tries — nobody gets left behind.\n\n"
            "Decipher the formula. Eight fragments, scattered across the entire route. Only at "
            "the end does everything come together. What did Heinrich really hide?\n\n"
            "Collect Traces. For each solved station you earn experience points. At the end, "
            "your certificate awaits.\n\n"
            "Ask Trace! Your digital companion Trace knows Tuebingen well. Ask for puzzle "
            "hints, but also about history, sights, or anything you would want to know on a "
            "city tour. Trace just will not reveal the answer.\n\n"
            "In a group? Bring a Bluetooth speaker! That way everyone can comfortably listen "
            "to the stories and puzzle together.\n\n"
            "Allow location access. The app needs access to your location for the map to work. "
            "When your browser asks, tap Allow.\n\n"
            "Going offline? Download the tour in advance — then everything works without "
            "internet too. You will find the button in the instructions.\n\n"
            "Your progress is saved automatically. You can pause anytime and continue later."
        ),
    },
    "epilog": {
        "voice": EPILOG_VOICE_EN,
        "text": (
            "Incredible, Investigator! You actually did it — seventeen stations, eight puzzles, "
            "and Heinrich's secret uncovered after more than one hundred fifty years. Not many "
            "manage that.\n\n"
            "The formula that Heinrich von Calw scattered across half the city was never a "
            "physical equation. It was an insight — inspired by Friedrich Hoelderlin, the poet "
            "who lived thirty-six years in the tower on the Neckar. Just a few hundred meters "
            "from your last station.\n\n"
            "But where danger is, grows the saving power also.\n\n"
            "Hoelderlin wrote this line in eighteen oh three in his hymn Patmos. Heinrich knew "
            "his verses and understood: Where knowledge is suppressed, the courage to share it "
            "grows.\n\n"
            "Thank you so much for joining us on this journey! We hope Tuebingen brought you "
            "as much joy as it brings us. Share your certificate with friends — and perhaps "
            "we will see each other again on a new tour soon. Until then: fare well, "
            "Investigator."
        ),
    },
}

# ============================================================
# AUDIO GENERATION
# ============================================================

def generate_audio(client, text, voice_id, output_path):
    """Generates an MP3 file from text via ElevenLabs REST API."""
    print(f"  Generating: {output_path.name} ({len(text)} chars)...", end=" ", flush=True)

    try:
        import requests
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            stream=True,
        )
        if resp.status_code != 200:
            print(f"ERROR: HTTP {resp.status_code} - {resp.text[:200]}")
            return False

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=4096):
                f.write(chunk)

        size_kb = output_path.stat().st_size / 1024
        print(f"OK ({size_kb:.0f} KB)")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def list_voices(client):
    """Shows all available voices."""
    print("\nAvailable voices:\n")
    response = client.voices.get_all()
    for v in response.voices:
        labels = ", ".join(f"{k}: {val}" for k, val in (v.labels or {}).items())
        print(f"  {v.name:25s}  ID: {v.voice_id}  [{labels}]")
    print()


def main():
    if API_KEY == "DEIN_API_KEY_HIER":
        print("Please set your ElevenLabs API key!")
        print("   export ELEVENLABS_API_KEY='your-key-here'")
        print("   or enter it directly in generate_audio_en.py.")
        sys.exit(1)

    client = None  # Using REST API directly

    if "--list-voices" in sys.argv:
        list_voices(client)
        sys.exit(0)

    if "--station" in sys.argv:
        idx = sys.argv.index("--station")
        station_nums = [int(x) for x in sys.argv[idx + 1].split(",")]
    else:
        station_nums = list(range(17))

    all_types = ["story", "diary", "fact", "riddle", "anecdote", "prologue", "guide", "epilog"]
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        types_to_gen = sys.argv[idx + 1].split(",")
    else:
        types_to_gen = all_types

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    voice_map = {
        "story": NARRATOR_VOICE_EN,
        "diary": HEINRICH_VOICE_EN,
        "fact": FACT_VOICE_EN,
        "riddle": NARRATOR_VOICE_EN,
        "anecdote": FACT_VOICE_EN,
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
    print("TraceTour Audio Generator EN - v1 (17 stations, 1869)")
    print("=" * 60)
    print(f"Output:    {OUTPUT_DIR}")
    print(f"Stations:  {station_nums}")
    print(f"Types:     {types_to_gen}")
    print(f"Total:     {total} files")
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

    # Generate special audio (prologue, guide, epilog)
    special_types = [t for t in types_to_gen if t in SPECIAL_AUDIO]
    for stype in special_types:
        spec = SPECIAL_AUDIO[stype]
        filename = f"{stype}.mp3"
        output_path = OUTPUT_DIR / filename
        print(f"\nSpecial: {stype}")
        success = generate_audio(client, spec["text"], spec["voice"], output_path)
        done += 1
        if not success:
            errors += 1
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"Done! {done - errors}/{total} files generated.")
    if errors:
        print(f"{errors} errors occurred.")
    print(f"Files in: {OUTPUT_DIR}")
    print("=" * 60)

    print("\nGenerated files:")
    for f in sorted(OUTPUT_DIR.glob("*.mp3")):
        size = f.stat().st_size / 1024
        print(f"   {f.name:20s}  {size:6.0f} KB")


if __name__ == "__main__":
    main()
