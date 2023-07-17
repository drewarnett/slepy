# slepy

Fast log entry for SOTA implemented in python using pyparsing.

Input:  slepy style SOTA log

Output:

* file for SOTA data base import
* file for printing and pasting in paper logbook

## Paper logging

The device logging solutions (VK port-a-log etc) are quite nifty and worth
a look.  I prefer paper logging for SOTA.  Before heading out, I fold a letter
sized piece of paper to quarter size.  I write the summit reference and the
name of the summit on top of one page.  I don't write down the date, but that
might be a good idea.

When I find a frequency to CQ, I'll jot down the frequency and mode and then
call CQ.  When a station answers, I jot down the callsign.  I may jot down
the RS(T) I'll send before sending my report or after I send it.  Then I jot
down the report they give me.  If it's summit-to-summmit (S2S), I'll jot
that down as well.  Stations will often send their state or province, and
I'll jot that down as well, as it's useful to see what the propagation is
doing.  Once I've worked them, I'll write down the time either local or UTC
depending on which clock I'm using.  (Phone is local; rig is UTC.)  Anything
else is just notes.

I try to remember to jot down the time after each QSO to let me know which
ones were successful QSOs.  (Sometimes, after jotting callsign or even some
of the reports, a QSO may not complete.)  But I do forget sometimes; it's easy
to interpolate in that case, if it's just a missed span of time.

Search and pounce (say for S2S) is logged the same way.

Here's an example log after unfolding the sheet of paper:

![example paper SOTA log.png](<example paper SOTA log.png>)

Scribbles.  There's also some extra notes about my hiking time.

## SOTA log upload

For SOTA data base import in V2 .csv format, the following fields are needed
for each QSO:

* my call
* my reference
* date
* time
* frequency
* mode
* their reference (optional, but automatically logs S2S!)
* comments (I don't upload comments, but may put in my own personal log.)

FLE is great idea for log data entry.  (FLEcli for command line FLE is, too.)

Note that my style above differs a bit from the format specified by FLE
especially regarding the timestamps.  Also, my style is fast for a touch-typist
and may not be optimum for someone wanting to minimize keystrokes.

The example paper log above can be transcribed to a text file with a few bits
of extra information like so:

    2023-06-21
    my_call n7da
    my_reference W6/CC-002
    utc-7
    N6MLW 146.52 332p FM
    KC6DSH 335p
    NT6E 338p
    KN6DMO 342p s2s W6/CT-029
    14.0635
    CW
    WA5SNL 599 579 2253z # IN
    W0MNA 599 599 2255z
    W0ERI 599 599 2255z
    AB0BM 599 569 2257z # IA
    W9MRH 559 559 2258z
    N7EDK 599 539 2259z # UT

'utc-7' shows my local time as UTC minus seven hours.  This is only needed for
local time entries.  (Integer ending in `a` or `p` or `l`.)

Frequency and/or mode can be entered on each QSO line.  Frequency is MHz and
contains a decimal point.  Mode can be one of `CW`, `SSB`, `FM`, or `AM`.

Save the text file as `filename.sle`.

`sle.py -i filename.sle` or `python3 -i sle.py filename.sle` or
`py -3 sle.py -i filename.sle` or similar should work to process this file
depending on your system.

`filename.csv` is ready to upload to the SOTA database.

For the example above:

    V2,N7DA,W6/CC-002,21/06/2023,2232,146.52MHz,FM,N6MLW,
    V2,N7DA,W6/CC-002,21/06/2023,2235,146.52MHz,FM,KC6DSH,
    V2,N7DA,W6/CC-002,21/06/2023,2238,146.52MHz,FM,NT6E,
    V2,N7DA,W6/CC-002,21/06/2023,2242,146.52MHz,FM,KN6DMO,W6/CT-029
    V2,N7DA,W6/CC-002,21/06/2023,2253,14.0635MHz,CW,WA5SNL,
    V2,N7DA,W6/CC-002,21/06/2023,2255,14.0635MHz,CW,W0MNA,
    V2,N7DA,W6/CC-002,21/06/2023,2255,14.0635MHz,CW,W0ERI,
    V2,N7DA,W6/CC-002,21/06/2023,2257,14.0635MHz,CW,AB0BM,
    V2,N7DA,W6/CC-002,21/06/2023,2258,14.0635MHz,CW,W9MRH,
    V2,N7DA,W6/CC-002,21/06/2023,2259,14.0635MHz,CW,N7EDK,

## Logbook print

Someday I'll go electronic, maybe when I finish the paper logbook I started as
a novice.  The `filename.txt` format is similar to how I would enter an
activation log.  I print and glue it in.

RS(T) reports and comments are written to this file, but left out of the SOTA
database upload file.

For the example above:

    SOTA activation on W6/CC-002
    2023-06-21 2232 N6MLW --- --- 146.52 FM
    2023-06-21 2235 KC6DSH --- --- 146.52 FM
    2023-06-21 2238 NT6E --- --- 146.52 FM
    2023-06-21 2242 KN6DMO --- --- 146.52 FM S2S W6/CT-029
    2023-06-21 2253 WA5SNL 599 579 14.0635 CW IN
    2023-06-21 2255 W0MNA 599 599 14.0635 CW
    2023-06-21 2255 W0ERI 599 599 14.0635 CW
    2023-06-21 2257 AB0BM 599 569 14.0635 CW IA
    2023-06-21 2258 W9MRH 559 559 14.0635 CW
    2023-06-21 2259 N7EDK 599 539 14.0635 CW UT
    end of activation

## Time interpolation

[onyx.sle](onyx.sle) is a good example where a log needs QSO times
interpolated.  sle.py will do that for you.

## Grammar/input file format

Use your preferred text file program to write your slepy format log text file.
Each line of the file is a statement.

The slepy log file has 2 parts:

* preamble
* body

The preamble contains:

* **my callsign statement**
* **my SOTA summit reference statement**
* **date statement**
* **timezone statement**

**my callsign statement** :=  'my_call' **callsign**

**my SOTA summit reference statement** :=  'my_reference' **SOTA summit reference**

**date statement** :=  YYYY-MM-DD

**timezone statement** :=  'UTC' signed_integer

>    No space between UTC and the value.

>    Only required if using 'a', 'p', or 'l' local timestamps.

>    Hours your local timezone differ from UTC.  For example use 'UTC-7' for PDT.

The body contains any number of:

* **frequency and/or mode statement**
* **QSO statement**

**frequency and/or mode statement** :=  **frequency** | **mode** | **frequency** **mode** | **mode** **frequency**

**frequency** :=  decimal number containing a decimal point, in MHz

**mode** :=  'cw' | 'ssb' | 'fm' | 'am'

>    Case insensitive.

**QSO statement** := **callsign** (optionally **reports** optionally **timestamp** optionally **frequency** optionally **mode** optionally ('s2s' **SOTA summit reference**)) optionally **comments**

>    Where reports, timestamp, frequency, mode, s2s may be in any order.

**reports** :=  RS(T) RS(T)

**timestamp** :=  **zulu time** | **local time** | **AM time** | **PM time**

>    1 to 4 digit integer followed, with no space, by 'z', 'l', 'a', or 'p'.

**comments** :=  '#' any text to end of line

Notes:

* Timestamp must be provided for first and last QSOs.  Missing timestamps will
  be patched in by interpolation.
* Frequency will use last given if not in QSO statement.
* Mode will use last given if not in QSO statement.

The grammar as a railroad diagram (produced by pyparsing):
[slepy_railroad.html](slepy_railroad.html).

## Customization and possible enhancements

You have the source, so you can customize this to your liking.  Perhaps
hardcode my call to remove the need to enter it?  Some ideas I have:

* validate summit references or at least association and region
* make input more case insensitive
* verbosely use current date if not given
