<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet id="stylesheet" version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
    <xsl:output method="html" doctype-system="html" encoding="UTF-8" indent="yes" />
    <xsl:template match="/">
        <xsl:text disable-output-escaping='yes'>&lt;!DOCTYPE html&gt;</xsl:text>
        <html>
            <head>
                <!-- This document is adapted from BBC (example: http://www.bbc.co.uk/programmes/p002w6r2/episodes/downloads.rss).
                We hope it's okay! We did it only because it looked so good. -->
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title><xsl:value-of select="rss/channel/title"/> fra Radio Revolt</title>
                <style>
                    body {
                    background: #222;
                    color: #fff;
                    font-family: Arial, sans-serif;
                    padding: 0;
                    margin: 0;
                    line-height: 1.4;
                    }

                    .episodes {
                    clear: both;
                    }

                    .lined {
                    border-bottom: solid 1px #000;
                    margin-bottom: 16px;
                    }

                    .header {
                    background: #edb61d;
                    margin-bottom: 16px;
                    }

                    .logo {
                    max-width: 300px;
                    max-height: 100px;
                    }

                    @media (max-width: 976px) {
                    .logo {
                    display: block;
                    margin: auto;
                    }
                    }

                    .limited {
                    margin-left: auto;
                    margin-right: auto;
                    max-width: 976px;
                    padding-left: 16px;
                    padding-right: 16px;
                    width: 100%;
                    box-sizing: border-box;
                    }

                    .podcast-image {
                    width: 100%;
                    margin-bottom: 16px;
                    }

                    .heading, p {
                    font-weight: normal;
                    margin-top: 0;
                    }

                    .input {
                    width: 100%;
                    font-size: 1.0em;
                    box-sizing: border-box;
                    border-radius: 0.1em;
                    cursor: pointer;
                    display: block;
                    margin-top: 0.1em;
                    }

                    .podcast-image {
                    max-width: 100%;
                    }

                    @media (min-width: 24em) {
                    .podcast-image {
                    width: 40%;
                    max-width: 300px;
                    float: left;
                    margin-right: 16px;
                    }
                    .input {
                    font-size: 1.3em
                    }
                    }

                    .episodes-list {
                    list-style: none;
                    margin: 0;
                    padding: 0;
                    }

                    .episodes-list__item {
                    padding-bottom: 2.0em;
                    }

                    .no-margin {
                    margin: 0;
                    }

                    a, a:link, a:visited, summary {
                    color: #edb61d;
                    text-decoration: none;
                    /* for summary */
                    cursor: pointer;
                    }

                    a:visited {
                        color: #ccae5c;
                    }

                    a:hover, a:active, a:focus, summary:hover {
                    color: #deb545;
                    text-decoration: underline;
                    }

                    details > :not(summary) {
                        margin-left: 2em;
                    }
                </style>
            </head>
            <body>
                <a class="header lined" style="display: block;" href="http://radiorevolt.no">
                    <div class="limited">
                        <img class="logo" src="/static/logo.png" alt="Radio Revolt - Studentradioen i Trondheim" />
                    </div>
                </a>
                <div class="lined">
                    <div class="limited">
                        <details>
                            <summary><strong>Dette er en podkast! Lær mer…</strong></summary>
                            <p>Med en podkastapp kan du få nye episoder av <xsl:value-of select="rss/channel/title"/>
                            lastet ned automatisk når du er på Wi‑Fi, sånn at du kan høre på dem
                            når det passer deg best.</p>

                        <p>Du kan for eksempel bruke:<br/>
                            <strong>iPhone:</strong> iTunes<br/>
                            <strong>Android:</strong> <a href="https://play.google.com/store/apps/details?id=fm.player"> Player FM</a><br/>
                            <strong>Windows Phone:</strong> den innebygde podkastappen
                        </p>
                        </details>

                        <p style="margin-top: 0.5em;">
                            Kopier nettadressen nedenfor og legg den til i podkastappen din.
                            <input class="input" type="text" id="input" readonly="readonly"><xsl:attribute name="value"><xsl:value-of select="rss/channel/link"/></xsl:attribute></input>
                            <script>
                                var input = document.getElementById('input');
                                input.value = window.location.href.replace("%C3%A5", "å").replace("%C3%A6", "æ").replace("%C3%B8", "ø");
                                var focused = false;
                                if (input) {
                                input.onblur = function() { focused = false; };
                                input.onclick = function() {
                                if (!focused || true) {
                                focused = true;
                                input.select();
                                }
                                };
                                }
                            </script>
                        </p>
                    </div>
                </div>
                <div class="limited">
                    <img class="podcast-image"> <xsl:attribute name="src"> <xsl:value-of select="rss/channel/itunes:image/@href"/> </xsl:attribute> </img>
                    <h1 class="heading"><a> <xsl:attribute name="href"><xsl:value-of select="rss/channel/link"/></xsl:attribute><xsl:value-of select="rss/channel/title"/></a></h1>
                    <p><xsl:value-of select="rss/channel/description"/></p>
                    <div class="episodes">
                        <h2 class="heading">Episoder</h2>
                        <ul class="episodes-list">
                            <xsl:for-each select="rss/channel/item">
                                <li class="episodes-list__item">
                                    <h3 class="no-margin">
                                        <a> <xsl:attribute name="href"> <xsl:value-of select="link"/> </xsl:attribute> <xsl:value-of select="title"/> </a>
                                    </h3>
                                    <xsl:value-of select="description"/>
                                    <p><a> <xsl:attribute name="href"> <xsl:value-of select="enclosure/@url"/> </xsl:attribute> Last ned MP3 </a>
                                    <span style="color: #AAA">(<span id="placeholder_size"> </span> MB,
                                        varighet <xsl:value-of select="itunes:duration"/>)</span></p>
                                    <script>element = document.getElementById("placeholder_size");
                                        element.innerHTML = Math.ceil(<xsl:value-of select="enclosure/@length"/>/(1000000));
                                        element.removeAttribute("id");
                                    </script>
                                </li>
                            </xsl:for-each>
                        </ul>
                    </div>
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
