# podkast.radiorevolt.no

Webserver for å servere podkaster.

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
* uWSGI som lag mellom webserver og applikasjonen
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
    <dt>web_feed.py</dt>
    <dd>Generering av podkastene.</dd>
    <dt>init_globals.py</dt>
    <dd>Lager instanser av alle datakildene som brukes av webapplikasjonen.
    Dette gjøres både ved oppstart og når det har gått lang nok tid (trigges av webserver.py).</dd>
    <dt>feed_utils/init_pipelines.py</dt>
    <dd>Setter opp pipelines (pipe-and-filter arkitektur) for å prosessere
    podkaster og episoder.</dd>
    <dt>settings_loader.py</dt>
    <dd>Laster inn innstillingene, by default fra settings.default.yaml og
    settings.yaml. Har muligheter til å utvides med andre måter å finne
    innstillinger på.</dd>
    <dt>process_images.py</dt>
    <dd>Skript som må kjøres jevnlig for å laste ned og behandle podkastbilder.</dd>
</dl>


