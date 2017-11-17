# podkast.radiorevolt.no

Webserver for å servere podkaster. Se [Confluence](https://confluence.smint.no/display/TEK/podkast.radiorevolt.no) for generell info (intern link).

_This new documentation is written primarily for internal usage and is therefore in Norwegian. The project itself is in English, though, as any code should be, so you may be able to find some details in the embedded documentation._

## Endringer

### v2.0

Hele applikasjonen er reorganisert. Mye av den samme koden er å finne igjen, men med en annen mappe- og filstruktur. Koden fungerer også annerledes, siden informasjon flyter på en måte som kan kalles "trickle down", i den forstand at ingen globale variabler aksesseres direkte, de blir i stedet gitt "ovenfra" gjennom funksjonsparametre. Dette gjør koden mer forutsigbar, lettere å forstå og modulær, man kan f. eks. bytte til en annen måte å hente innstillinger på uten å gjøre store endringer.

Formålet med reorganiseringen er å plassere mye av makta i view-koden som genererer feeden. Dermed kan koden der ta beslutninger som f. eks. hvilken pipeline som skal brukes, som er nødvendig for å lage egen Spotify-feed. Videre er innstillingene endret kraftig, slik at de er mye lettere å handskes med. Mesteparten av innstillingene har vi på Git, så overskriver man det man må lokalt.

For å migrere:
1. oppdater filstiene i SystemD unit-fila (`src` som mappe for `make`),
2. crontab (samme som for SystemD) og
3. Nginx (static-mappa).
4. Lag en ny virtualenv inne i `src`-mappa og 
5. installer avhengighetene i `requirements.txt`-fila.
6. Migrer de lokale innstillingene fra `generator/settings.py` og `webserver/settings.py` til `settings.yaml`, skjønt de fleste er allerede migrert til `settings.default.yaml` (les deg opp på innstillingene først).
7. Gi skrivetilgang til `src/static/images` for brukeren applikasjonen kjører som.

## Oppsett

### Pakker som må installeres

#### CentOS

    sudo yum install libxml2 libxml2-devel postgresql postgresql-server libxslt-devel libjpeg-turbo libjpeg-turbo-devel zlib-devel freetype-devel lcms2-devel libwebp-devel tcl tk postgresql-devel python3-devel

#### Ubuntu/Debian

    
    sudo apt install libxml2 libxml2-dev libxslt1.1 libxslt1-dev python3-lxml libpq-dev python3-dev libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev libwebp-dev tcl8.5-dev tk8.5-dev

#### Andre

Generelt må du bare oppfylle kravene som stilles av pakkene i `requirements-to-freeze.txt`.

### Videre oppsett

1. Sett opp et virtualenv kalt `venv` inne i `src`: `virtualenv -p python3.4 src/venv`
2. Aktiver virtualenv: `. src/venv/bin/activate`
3. Installer avhengigheter: `pip install -r src/requirements.txt`
4. Lag en tom fil kalt `settings.yaml`, og overskriv følgende innstillinger fra
   `settings.default.yaml` (se sistnevnte for format, du trenger ikke spesifisere
   andre innstillinger enn akkurat de du overskriver):
   * rest_api.url
   * rest_api.user
   * rest_api.password
   * db.host
   * db.port
   * db.database
   * db.user
   * db.password
   * redirector.db_file
5. Sett opp uWSGI-innstillingene: Kopier `podkast.radiorevolt.no.template.ini`, endre filstien til `socket`
   så den peker til `data`-mappen og lagre som `podkast.radiorevolt.no.ini`.
6. Sett opp PostgreSQL-server ved hjelp av nyeste backup fra forrige eller
   kjørende instans av podkastapplikasjonen. Det skal også finnes en SQL-fil
   i dette repoet som kan brukes til utvikling, men bruker du det i prod risikerer
   vi at noen URLer som folk bruker slutter å fungere.
7. Sett opp egen bruker for podkastsystemet, som du deretter gir skrivetilgang
   til `data`-mappa og `src/static/images`-mappa.
8. Sett opp en cron-jobb som kjører `make -C sti/til/podkast.radiorevolt.no/src images` hvert 5. til 10. minutt som denne brukeren.
9. Bruk filene i `nginx` og `systemd`-mappene som utgangspunkt til å lage en
   konfigurasjon for Nginx (webserver) og SystemD-tjenesten (automatisk oppstart,
   legges i `/etc/systemd/system`).

For utviklingsformål kan du kjøre `app.py` direkte for å få en
utviklingsserver på port 5000 til vanlig (bruk `--help` for å se tilgjengelige
innstillinger).

Ellers kan du bruker `make` til å kjøre programmene, som aktiverer virtualenv og
kjører programmet i riktig mappe. `make` kjører uWSGI-serveren (som Nginx kan
koble seg til), og `make images` kjører skriptet som laster ned og behandler
programbilder. Bruk `-C sti/til/podkast.radiorevolt.no/src` hvis du kjører `make` fra en annen mappe enn
`src/`.
    
## Funksjon

En stor andel av Radio Revolts lyttere bruker podkaster til å konsumere
innholdet vi lager. Det er derfor viktig for oss å gi dem en god opplevelse når
de bruker podkastene. Samtidig flyttet vi fra et system der teknisk selv måtte
gjøre manuelle endringer i Feedburner for å oppdatere metadata, og ønsket å
tilby lytterne mer oppdaterte metadata.

Denne applikasjonen er skrevet for å kunne være Radio Revolts podkastløsning
fra nå og for alltid. Dette er løst ved å ha en rekke filtre som tilføyer
metadata til podkastene og deres episoder. Å legge til en ny kilde til
metadata er så enkelt som å lage et nytt filter og sette det opp til å bli
brukt. Dette er kanskje det som skiller denne podkastapplikasjonen mest fra alle
andre.

En annen nyttig funksjon er automatisk omdirigering ved bytte av programnavn.
Dette er gjort mulig med en database der alle tidligere URLer ligger inne, slik
at vi kan omdirigere lyttere til den nye URLen. Et program kan dermed bytte
navn uten at teknisk må røre en finger.

Programbilder lastes ned og serveres fra maskinen applikasjonen kjører på. De
får hvit bakgrunn og blir gjort om til kvadrat-format, og skaleres til passende
dimensjoner.

## Teknologi

* Python v3.4
* uWSGI som lag mellom webserver (nginx) og applikasjonen
* sqlite som database for episode-URLer (dette er tenkt å endres)
* PostgreSQL som database for podkast-URLer
* SystemD for å kjøre tjenesten
* Et python-skript må kjøres jevnlig med cron
* Podkaster genereres med biblioteket PodGen


## Innstillinger

Utgangspunktet for innstillingene er fila `settings.default.yaml`. Denne setter
nesten alle innstillingene som man kan sette, og har forklarende kommentarer.
De aller fleste innstillingene ligger her og skal endres gjennom Git.

Private innstillinger, som f. eks. innloggingsdetaljer til databasen, ligger i
`settings.yaml`. Her kan man overskrive individuelle innstillinger fra
`settings.default.yaml`. Det er ytterst få innstillinger som trengs å settes her,
men de som trenger det har som regel en tydelig placeholder-verdi i `settings.default.yaml`
(som f. eks. `hackme` som brukernavn). Denne fila er ekskludert fra Git.

## Pipelines-arkitektur

For å gi metadata til podkastene og deres episoder, benyttes en "pipe and 
filter"-arkitektur. Det innebærer at du har en rekke filtre på rad og rekke,
og resultatet av det ene filteret gis til det neste.

I denne applikasjonen kalles filtrene for `processors`. De prosesserer en
podkast eller en episode, og er arrangert i `pipelines`, som er en rekke
processors arrangert i en rekkefølge. Du kan se for deg at du har rør som
podkastene og episodene går gjennom, og at du har processors som en del av
røret som gjør forandringer på innholdet som går gjennom det.

I innstillingene setter man opp disse pipelinene. Du lager ei liste over
processors, og kan også inkludere en annen pipeline for å gjenbruke ressurser
og innstillinger. Hver processor sine innstillinger kan man også sette globalt,
for deretter å overskrive dem lokalt i pipelinen. Du kan også bestemme hvilke
episoder og podkaster en pipeline skal arbeide på, ved å sette et dato-intervall
og ved å spesifisere URLer eller Digas-IDer som ikke skal røres av processor-en.

Se forklaringen i `episode_processors/README.md` for en praktisk tilnærming til
hvordan dette fungerer, og `settings.default.yaml` for hvordan du setter opp
pipelines og processors i innstillingene.

## Moduler

### Viktigste

<dl>
    <dt>webserver.py</dt>
    <dd>Hovedapplikasjonens inngang. Orkestrerer og setter alt sammen.</dd>
    <dt>views/web_feed.py</dt>
    <dd>Generering av podkastene.</dd>
    <dt>init_globals.py</dt>
    <dd>Lager instanser av alle datakildene som brukes av webapplikasjonen.
    Dette gjøres både ved oppstart og når det har gått lang nok tid (trigges av webserver.py).</dd>
    <dt>feed_utils/init_pipelines.py</dt>
    <dd>Setter opp pipelines (pipe-and-filter arkitektur) for å prosessere
    podkaster og episoder.</dd>
    <dt>utils/settings_loader.py</dt>
    <dd>Laster inn innstillingene, by default fra settings.default.yaml og
    settings.yaml. Har muligheter til å utvides med andre måter å finne
    innstillinger på.</dd>
    <dt>process_images.py</dt>
    <dd>Skript som må kjøres jevnlig for å laste ned og behandle podkastbilder.</dd>
</dl>

### Python-pakker under src/

<dl>
    <dt>episode_processors</dt>
    <dd>Processors som behandler episoder og noe infrastruktur rundt dette.</dd>
    <dt>feed_utils</dt>
    <dd>Diverse nyttige verktøy for å gjøre ting på feedene.</dd>
    <dt>show_processors</dt>
    <dd>Processors som behandler podkaster/programmer og noe infrastruktur rundt dette.</dd>
    <dt>static</dt>
    <dd>Diverse filer som serveres av Nginx direkte, under URIet <code>/static</code>.</dd>
    <dt>utils</dt>
    <dd>Nyttige verktøy som ikke er direkte relatert til feeds eller webserveren.</dd>
    <dt>views</dt>
    <dd>Moduler og funksjoner som behandler HTTP-forespørsler.</dd>
    <dt>web_utils</dt>
    <dd>Nyttige verktøy for å håndtere URLer og webserver-delen av applikasjonen.</dd>
</dl>

## Utvikling

Kodestil: [Google Python Coding Style Guide](https://google.github.io/styleguide/pyguide.html), inkludert [pylint](https://www.pylint.org/). Skjønt, sistnevnte har ikke vært brukt så lenge, så mye følger ikke helt standarden. Da tar man gjerne og gjør det finere rundt der man gjør endringer :)


