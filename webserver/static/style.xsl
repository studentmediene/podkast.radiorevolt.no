<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet id="stylesheet" version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
    <xsl:output method="html" doctype-system="html" encoding="UTF-8" indent="yes" />
    <xsl:template match="/">
        <html>
            <head>
                <!-- This document is adapted from BBC (example: http://www.bbc.co.uk/programmes/p002w6r2/episodes/downloads.rss).
                We hope it's okay! We did it only because it looked so good. -->
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title><xsl:value-of select="rss/channel/title"/> Podkast på Radio Revolt</title>
                <style>
                    body {
                    background: #313131;
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
                    background: #2B2B2B;
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
                    font-size: 1.4em;
                    box-sizing: border-box;
                    }

                    .podcast-image {
                    max-width: 100%;
                    }

                    @media (min-width: 22em) {
                    .podcast-image {
                    width: 40%;
                    max-width: 300px;
                    float: left;
                    margin-right: 16px;
                    }
                    }

                    .episodes-list {
                    list-style: none;
                    margin: 0;
                    padding: 0;
                    }

                    .episodes-list__item {
                    margin-bottom: 2.5em;
                    }

                    .no-margin {
                    margin: 0;
                    }

                    a, a:link, a:visited {
                    color: #e79c0f;
                    text-decoration: none;
                    }

                    a:hover, a:active, a:focus {
                    color: #d7920d;
                    text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="header lined">
                    <div class="limited">
                        <img class="logo" src="/static/logo.png" alt="Radio Revolt - Studentradioen i Trondheim" />
                    </div>
                </div>
                <div class="lined">
                    <div class="limited">
                        <p>
                            <strong>Dette er en podkast</strong>. Ved å bruke podkaster, kan du få nye episoder lastet ned automatisk
                            til mobilen din. Alt du trenger er en <strong>podkast-app</strong>! Har du iPhone kan du bruke iTunes,
                            har du Android anbefaler vi <a href="https://play.google.com/store/apps/details?id=fm.player">Player FM</a>
                            og har du Windows Phone kan du bruke podkast-appen som er innebygd.
                        </p>

                        <p>
                            Kopier nettadressen nedenfor og legg den til i podkast-appen din.
                        </p>
                        <p>
                            <input class="input" type="text" id="input"><xsl:attribute name="value"><xsl:value-of select="rss/channel/link"/></xsl:attribute></input>
                            <script>
                                var input = document.getElementById('input');
                                input.value = window.location;
                                var focused = false;
                                if (input) {
                                input.onblur = function() { focused = false; };
                                input.onclick = function() {
                                if (!focused) {
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
                                    <p><a> <xsl:attribute name="href"> <xsl:value-of select="enclosure/@url"/> </xsl:attribute> Last ned MP3 </a></p>
                                </li>
                            </xsl:for-each>
                        </ul>
                    </div>
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
