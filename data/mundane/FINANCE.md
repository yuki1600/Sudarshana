# Finance database: how it was built and checked

Built 2026-11-18 by `tools/mundane_finance.py`.

- 11,379 listed companies; 5,340 matched to a Wikidata item; 7,118 with a first trading day (Yahoo Finance: 4,879, Wikidata: 1,174, NSE equity list: 557, KRX KIND list: 165, SSE company list: 131, SZSE company list: 113, TWSE ISIN list: 88, The Motley Fool (J&J dates its IPO the 24th, a Sunday): 1, The Motley Fool: 1, Intel's investor FAQ: 1, TI's investor FAQ: 1, Nestlé's investor FAQ (Zurich Stock Exchange): 1, L'Oréal Finance: 1, Caterpillar: 1, AInvest and Moomoo listing dates: 1, BBC News: 1, 3M's investor FAQ: 1, Rodden A: Timed documented source, news: 1), 7,099 of them timed
- founding: 1,414 to the day, 3,829 to the month or year, 7,716 unknown
- 1,437 unicorns; 497 matched to Wikidata; 65 cast for their founding day
- 143 of the largest unlisted companies by revenue (state-owned or private); 30 cast for their founding day

## Yahoo Finance's first trading day, exchange by exchange

Yahoo's first trading day is its price history's first day: the listing day for a company listed after Yahoo's data for the exchange begins, the start of its data for one listed before. A day many symbols share is such a start and never used (below). On the US markets the rest are used before Wikidata: checked against it, Yahoo had Microsoft's, Home Depot's, Amgen's and FedEx's IPO days where Wikidata's start time was a later move between exchanges, a renaming or a bulk import. Elsewhere Yahoo stands for a listing day only from the date below on, from which 90% of its days agree within 3 days with the exchange's list or Wikidata. An exchange with too few days checked to find that date takes 2016-01-01, from which the days of all the exchanges off the US, pooled, agree 90% of the time (most of the rest are Yahoo counting a company's trading on another board before its move, or missing its first few days).

| MIC | exchange | checked | trusted from | agree after |
|---|---|---|---|---|
| XNSE | National Stock Exchange of India | 357 | 1999-04-28 | 311/343 |
| XNAS | Nasdaq | 288 | always (US) | — |
| XNYS | New York Stock Exchange | 269 | always (US) | — |
| XASX | Australian Securities Exchange | 232 | 1999-02-22 | 168/187 |
| XSHG | Shanghai Stock Exchange | 157 | 1993-06-10 | 154/157 |
| XSHE | Shenzhen Stock Exchange | 116 | 1994-05-09 | 106/114 |
| XHKG | Hong Kong Stock Exchange | 103 | 2007-11-13 | 45/48 |
| XKRX | Korea Exchange | 91 | 2004-08-05 | 64/70 |
| XTKS | Tokyo Stock Exchange | 56 | 2015-11-04 | 16/17 |
| XTAI | Taiwan Stock Exchange | 38 | 2016-01-01 (pooled) | — |
| XIDX | Indonesia Stock Exchange | 36 | 2007-11-12 | 17/17 |
| XSAU | Saudi Exchange | 33 | 2016-01-01 (pooled) | — |
| XBKK | Stock Exchange of Thailand | 32 | 2000-11-03 | 26/28 |
| XETR | Xetra | 26 | 2017-11-02 | 12/12 |
| XLON | London Stock Exchange | 23 | 2016-01-01 (pooled) | — |
| XKOS | KOSDAQ | 20 | 2000-04-28 | 18/19 |
| XFRA | Frankfurt Stock Exchange | 13 | 2007-11-02 | 10/11 |
| XBRU | Euronext Brussels | 10 | 2005-06-20 | 8/8 |
| XAMS | Euronext Amsterdam | 9 | 2016-01-01 (pooled) | — |
| XPAR | Euronext Paris | 7 | 2016-01-01 (pooled) | — |
| XSTO | Nasdaq Stockholm | 6 | 2016-01-01 (pooled) | — |
| XNZE | NZX | 6 | 2016-01-01 (pooled) | — |
| XHEL | Nasdaq Helsinki | 5 | 2016-01-01 (pooled) | — |
| XOSL | Oslo Børs | 4 | 2016-01-01 (pooled) | — |
| BVMF | B3 | 4 | 2016-01-01 (pooled) | — |
| XWAR | Warsaw Stock Exchange | 4 | 2016-01-01 (pooled) | — |
| MISX | Moscow Exchange | 3 | 2016-01-01 (pooled) | — |
| XSWX | SIX Swiss Exchange | 3 | 2016-01-01 (pooled) | — |
| XTSE | Toronto Stock Exchange | 3 | 2016-01-01 (pooled) | — |
| ASEX | Athens Stock Exchange | 3 | 2016-01-01 (pooled) | — |
| OTCM | OTC Markets | 3 | always (US) | — |
| XMEX | Mexican Stock Exchange | 1 | 2016-01-01 (pooled) | — |
| XMAD | Bolsa de Madrid | 1 | 2016-01-01 (pooled) | — |
| XCSE | Nasdaq Copenhagen | 1 | 2016-01-01 (pooled) | — |
| XPRA | Prague Stock Exchange | 1 | 2016-01-01 (pooled) | — |
| XWBO | Vienna Stock Exchange | 1 | 2016-01-01 (pooled) | — |
| XLIT | Nasdaq Vilnius | 1 | 2016-01-01 (pooled) | — |
| XMIL | Borsa Italiana | 1 | 2016-01-01 (pooled) | — |
| XRIS | Nasdaq Riga | 1 | 2016-01-01 (pooled) | — |

Days Yahoo's histories start on, not used (market, day, symbols): ASEX 2000-01-03 (2); BVMF 2000-01-03 (11); BVMF 2000-01-04 (2); DSMD 2010-02-22 (38); MISX 2010-03-03 (10); ROCO 2007-12-28 (1); ROCO 2007-12-31 (9); US 1962-01-02 (28); US 1972-06-01 (19); US 1973-02-21 (74); US 1973-05-03 (24); US 1980-03-17 (192); US 1981-12-31 (12); US 1994-04-04 (11); US 2002-07-01 (2); US 2003-10-07 (8); US 2005-09-29 (2); US 2007-12-28 (1); US 2010-01-05 (10); US 2010-02-22 (2); US 2021-01-08 (11); US 2021-06-30 (10); US 2026-07-17 (114); XADS 2010-02-22 (17); XADS 2010-03-03 (1); XAMS 2000-01-03 (1); XAMS 2026-07-17 (1); XASX 1988-01-29 (51); XASX 2000-01-04 (1); XASX 2026-07-17 (3); XBAH 2000-01-11 (12); XBKK 2000-01-04 (22); XBKK 2007-12-28 (1); XBOM 2000-01-03 (1); XBRU 2000-01-04 (34); XBUE 2000-01-03 (2); XCSE 2000-01-03 (19); XCSE 2000-01-04 (1); XCSE 2000-05-10 (1); XDUB 2000-01-04 (4); XETR 1996-12-16 (6); XETR 1998-11-09 (8); XETR 2000-01-03 (5); XETR 2007-12-28 (5); XETR 2026-07-17 (6); XFRA 2000-01-03 (40); XFRA 2000-01-05 (1); XFRA 2000-01-14 (9); XFRA 2000-02-01 (2); XFRA 2007-12-28 (8); XFRA 2026-07-17 (1); XHEL 2000-01-03 (33); XHKG 2000-01-04 (60); XHKG 2000-02-01 (1); XHKG 2005-09-29 (5); XICE 2000-01-03 (1); XICE 2026-07-17 (1); XIDX 2005-09-29 (8); XIST 2000-05-10 (25); XIST 2007-12-31 (1); XJSE 2000-01-04 (21); XKLS 2000-01-03 (30); XKRX 2000-01-04 (49); XKRX 2005-09-29 (7); XKUW 2000-01-03 (35); XKUW 2000-01-04 (2); XLIS 2000-01-03 (11); XLIS 2026-07-17 (1); XLIT 2002-06-06 (10); XLON 1988-07-01 (104); XLON 2000-01-03 (1); XLON 2000-01-04 (8); XLON 2026-07-17 (7); XMAD 2000-01-03 (28); XMAD 2026-07-17 (1); XMEX 2000-01-03 (4); XMEX 2000-01-05 (1); XMIL 1995-03-24 (10); XMIL 2000-01-03 (7); XMIL 2026-07-17 (2); XNSE 1996-01-01 (35); XNSE 2000-05-10 (1); XNSE 2002-07-01 (133); XNSE 2002-08-12 (26); XNSE 2007-12-31 (1); XNSE 2026-07-17 (2); XNZE 2000-01-05 (15); XNZE 2005-09-29 (1); XOSL 2000-01-03 (28); XOSL 2000-01-04 (1); XOSL 2026-07-17 (3); XPAR 2000-01-03 (110); XPAR 2000-01-04 (3); XPAR 2000-01-05 (2); XPAR 2000-04-12 (13); XPAR 2000-05-10 (1); XPAR 2001-01-01 (1); XPAR 2026-07-17 (4); XPRA 2000-01-05 (3); XRIS 2000-01-04 (1); XSAU 2010-02-22 (1); XSAU 2010-03-03 (62); XSAU 2010-03-04 (57); XSES 2000-01-03 (20); XSES 2005-09-29 (1); XSGO 2000-01-03 (10); XSGO 2000-01-04 (1); XSGO 2000-01-05 (1); XSHG 2000-01-04 (2); XSTC 2010-02-22 (12); XSTO 2000-01-03 (54); XSTO 2000-01-04 (1); XSTO 2005-09-29 (1); XSTO 2026-07-17 (3); XSWX 1995-04-03 (37); XSWX 1998-07-17 (6); XSWX 2000-01-04 (11); XSWX 2002-08-12 (1); XSWX 2007-12-28 (1); XSWX 2026-07-17 (1); XTAE 2000-02-01 (14); XTAE 2002-08-12 (34); XTAE 2007-12-31 (5); XTAE 2026-07-17 (1); XTAI 2000-01-04 (44); XTAI 2005-09-29 (1); XTAI 2007-12-28 (1); XTAI 2007-12-31 (1); XTAL 2000-01-03 (1); XTKS 2000-01-04 (183); XTKS 2000-01-05 (2); XTKS 2000-04-04 (10); XTKS 2001-01-01 (300); XTKS 2001-01-04 (80); XTKS 2005-09-29 (13); XTKS 2007-12-28 (4); XTKS 2010-02-22 (9); XTKS 2026-07-17 (3); XTSE 1980-03-17 (1); XTSE 1995-01-12 (21); XTSE 1996-04-25 (7); XTSE 1996-08-13 (13); XTSE 2003-10-09 (8); XTSE 2008-07-23 (6); XTSE 2026-07-17 (8); XTSX 2026-07-17 (2); XWAR 2000-01-03 (16); XWAR 2010-02-22 (4); XWAR 2026-07-17 (1); XWBO 2000-01-03 (15); XWBO 2000-01-04 (1); XWBO 2000-01-05 (1).

Wikidata start times shared by 10 or more listings of a market, taken for bulk imports and not used: BVMF 2021-01-10; BVMF 2021-09-28; BVMF 2021-09-29; BVMF 2021-09-30; BVMF 2021-10-01; BVMF 2021-10-30; US 1990-01-02; US 1990-03-26; US 1994-01-03; XTKS 2013-07-16. Tokyo's 1949-05-16, the exchange's reopening, is kept.

## Listing days the sources disagree on (295)

The first source is the one kept.

| company | exchange | kept | day | other | day |
|---|---|---|---|---|---|
| Microsoft | Nasdaq | Yahoo Finance | 1986-03-13 | Wikidata | 1987-09-17 |
| TSMC | New York Stock Exchange | Yahoo Finance | 1997-10-09 | Wikidata | 1997-10-20 |
| Meta Platforms (Facebook) | Nasdaq | Yahoo Finance | 2012-05-18 | Wikidata | 2022-06-09 |
| Novartis | New York Stock Exchange | Yahoo Finance | 1996-11-07 | Wikidata | 2000-05-11 |
| AstraZeneca | New York Stock Exchange | Yahoo Finance | 1993-05-12 | Wikidata | 1999-04-06 |
| Shell | New York Stock Exchange | Yahoo Finance | 1984-03-12 | Wikidata | 2022-01-31 |
| RTX | New York Stock Exchange | Yahoo Finance | 1962-04-02 | Wikidata | 2020-04-03 |
| SAP | New York Stock Exchange | Yahoo Finance | 1995-09-18 | Wikidata | 1998-08-03 |
| McDonald | New York Stock Exchange | Yahoo Finance | 1966-07-05 | Wikidata | 1970-01-02 |
| T-Mobile US | Nasdaq | Yahoo Finance | 2007-04-19 | Wikidata | 2013-05-01 |
| Sumitomo Mitsui Financial Group | New York Stock Exchange | Yahoo Finance | 2006-01-27 | Wikidata | 2010-11-01 |
| Foxconn Industrial Internet | Shanghai Stock Exchange | SSE company list | 2018-06-08 | Yahoo Finance | 2018-06-13 |
| Phillips 66 | New York Stock Exchange | Yahoo Finance | 2012-04-12 | Wikidata | 2012-04-30 |
| ING | New York Stock Exchange | Yahoo Finance | 1994-05-18 | Wikidata | 1997-06-13 |
| Cadence Design Systems | Nasdaq | Yahoo Finance | 1987-06-10 | Wikidata | 2005-10-31 |
| Moody's | New York Stock Exchange | Yahoo Finance | 1994-10-31 | Wikidata | 2000-10-03 |
| CPKC (Canadian Pacific Kansas City) | New York Stock Exchange | Yahoo Finance | 1983-12-30 | Wikidata | 2001-10-03 |
| Itaú Unibanco | New York Stock Exchange | Yahoo Finance | 2002-02-25 | Wikidata | 2009-05-20 |
| Canadian National Railway | New York Stock Exchange | Yahoo Finance | 1996-11-26 | Wikidata | 1995-11-17 |
| Vertiv Holdings | New York Stock Exchange | Yahoo Finance | 2018-08-02 | Wikidata | 2020-02-10 |
| Freeport-McMoRan | New York Stock Exchange | Yahoo Finance | 1995-07-10 | Wikidata | 1995-11-16 |
| Monolithic Power Systems | Nasdaq | Yahoo Finance | 2004-11-19 | Wikidata | 2005-05-16 |
| Cement Roadstone Holding | New York Stock Exchange | Yahoo Finance | 1989-07-13 | Wikidata | 1994-06-13 |
| Edwards Lifesciences | New York Stock Exchange | Yahoo Finance | 2000-03-27 | Wikidata | 2000-04-03 |
| Diageo | New York Stock Exchange | Yahoo Finance | 1991-03-14 | Wikidata | 1997-12-17 |
| Kotak Mahindra Bank | National Stock Exchange of India | NSE equity list | 1995-12-20 | Yahoo Finance | 2001-07-02 |
| The People's Insurance Company (PICC) | Shanghai Stock Exchange | SSE company list | 2018-11-16 | Yahoo Finance | 2018-11-23 |
| Hikvision | Shenzhen Stock Exchange | SZSE company list | 2010-05-28 | Yahoo Finance | 2010-12-20 |
| Block | New York Stock Exchange | Yahoo Finance | 2015-11-19 | Wikidata | 2025-01-21 |
| Baker Hughes | Nasdaq | Yahoo Finance | 1987-04-06 | Wikidata | 2019-10-19 |
| Franco-Nevada | New York Stock Exchange | Yahoo Finance | 2007-12-07 | Wikidata | 2011-09-08 |
| Thomson Reuters | Nasdaq | Yahoo Finance | 2002-06-12 | Wikidata | 2008-04-17 |
| Yum! Brands | New York Stock Exchange | Yahoo Finance | 1997-09-17 | Wikidata | 1997-09-26 |
| Carrier Global | New York Stock Exchange | Yahoo Finance | 2020-03-19 | Wikidata | 2020-04-03 |
| D. R. Horton | New York Stock Exchange | Yahoo Finance | 1992-06-05 | Wikidata | 1995-12-19 |
| Woodside Energy | New York Stock Exchange | Yahoo Finance | 1996-11-18 | Wikidata | 2022-06-02 |
| Rocket Lab | Nasdaq | Yahoo Finance | 2020-11-24 | Wikidata | 2025-05-23 |
| TKO Group Holdings | New York Stock Exchange | Yahoo Finance | 1999-10-19 | Wikidata | 2023-09-12 |
| Celltrion | Korea Exchange | KRX KIND list | 2018-02-09 | Yahoo Finance | 2005-07-19 |
| JSW Steel | National Stock Exchange of India | NSE equity list | 2005-03-23 | Yahoo Finance | 2003-05-08 |
| Hindustan Aeronautics | National Stock Exchange of India | NSE equity list | 2018-03-28 | Yahoo Finance | 2018-04-02 |
| Iron Mountain | New York Stock Exchange | Yahoo Finance | 1996-02-01 | Wikidata | 1999-04-26 |
| LabCorp | New York Stock Exchange | Yahoo Finance | 1990-03-29 | Wikidata | 1995-05-09 |
| EchoStar | Nasdaq | Yahoo Finance | 2008-01-02 | Wikidata | 2026-06-24 |
| Quest Diagnostics | New York Stock Exchange | Yahoo Finance | 1996-12-17 | Wikidata | 1996-12-26 |
| Flex | Nasdaq | Yahoo Finance | 1994-03-18 | Wikidata | 1998-11-06 |
| Darden Restaurants | New York Stock Exchange | Yahoo Finance | 1995-05-09 | Wikidata | 1998-11-06 |
| Wiwynn | Taiwan Stock Exchange | TWSE ISIN list | 2019-03-27 | Yahoo Finance | 2017-11-13 |
| ON Semiconductor | Nasdaq | Yahoo Finance | 2000-05-02 | Wikidata | 2000-04-28 |
| InterContinental Hotels Group | New York Stock Exchange | Yahoo Finance | 2003-04-10 | Wikidata | 2016-05-09 |
| Fox Corporation | Nasdaq | Yahoo Finance | 2019-03-13 | Wikidata | 2019-03-19 |
| Kinross Gold | New York Stock Exchange | Yahoo Finance | 1981-03-17 | Wikidata | 1994-10-19 |
| Xylem | New York Stock Exchange | Yahoo Finance | 2011-10-13 | Wikidata | 2011-11-01 |
| China Securities (CSC Financial) | Shanghai Stock Exchange | SSE company list | 2018-06-20 | Yahoo Finance | 2018-06-27 |
| Hua Nan Financial Holdings | Taiwan Stock Exchange | TWSE ISIN list | 2001-12-19 | Wikidata | 2001-12-26 |
| Grupo Cibest (Bancolombia) | New York Stock Exchange | Yahoo Finance | 1995-07-26 | Wikidata | 1998-06-29 |
| FedEx Freight | New York Stock Exchange | Yahoo Finance | 2026-05-27 | Wikidata | 2026-06-01 |
| Rogers Communications | New York Stock Exchange | Yahoo Finance | 1996-01-11 | Wikidata | 2007-06-15 |
| SoFi | Nasdaq | Yahoo Finance | 2021-01-04 | Wikidata | 2021-06-01 |
| Rongsheng Petrochemical | Shenzhen Stock Exchange | SZSE company list | 2010-11-02 | Yahoo Finance | 2011-11-10 |
| Jones Lang LaSalle | New York Stock Exchange | Yahoo Finance | 1997-07-17 | Wikidata | 1999-03-12 |
| Supermicro | Nasdaq | Yahoo Finance | 2007-03-29 | Wikidata | 2007-03-19 |
| Check Point Software | Nasdaq | Yahoo Finance | 1996-06-28 | Wikidata | 1999-03-03 |
| Origin Energy | Australian Securities Exchange | Wikidata | 1961-07-13 | Yahoo Finance | 1999-02-22 |
| Telus | New York Stock Exchange | Yahoo Finance | 1996-06-11 | Wikidata | 2000-10-17 |
| Lincoln Electric | Nasdaq | Yahoo Finance | 1994-04-07 | Wikidata | 1995-06-13 |
| Solventum | New York Stock Exchange | Yahoo Finance | 2024-03-26 | Wikidata | 2024-04-01 |
| Pinnacle Financial Partners | New York Stock Exchange | Yahoo Finance | 2000-08-22 | Wikidata | 2000-08-18 |
| ICON plc | Nasdaq | Yahoo Finance | 1998-05-15 | Wikidata | 2013-02-04 |
| Healthpeak Properties | New York Stock Exchange | Yahoo Finance | 1985-05-23 | Wikidata | 2024-03-04 |
| Samsung SDS | Korea Exchange | KRX KIND list | 2014-11-14 | Yahoo Finance | 2014-08-25 |
| LATAM Airlines | New York Stock Exchange | Yahoo Finance | 2024-07-25 | Wikidata | 1997-11-07 |
| iFLYTEK | Shenzhen Stock Exchange | SZSE company list | 2008-05-12 | Yahoo Finance | 2008-04-25 |
| Scentre Group | Australian Securities Exchange | Wikidata | 2014-06-25 | Yahoo Finance | 2010-12-12 |
| Flutter Entertainment | New York Stock Exchange | Yahoo Finance | 2002-10-04 | Wikidata | 2024-01-29 |
| Zydus Lifesciences | National Stock Exchange of India | NSE equity list | 2000-04-18 | Yahoo Finance | 2000-04-27 |
| Wharf REIC | Hong Kong Stock Exchange | Wikidata | 2017-11-23 | Yahoo Finance | 2017-11-15 |
| Zhejiang Century Huatong | Shenzhen Stock Exchange | SZSE company list | 2011-07-28 | Yahoo Finance | 2011-08-10 |
| Jindal Steel &amp; Power | National Stock Exchange of India | NSE equity list | 1999-12-29 | Yahoo Finance | 1999-09-22 |
| Guidewire Software | New York Stock Exchange | Yahoo Finance | 2012-01-25 | Wikidata | 2012-01-30 |
| Huntington Ingalls Industries | New York Stock Exchange | Yahoo Finance | 2011-03-22 | Wikidata | 2011-03-31 |
| Alpha Services and Holdings | Athens Stock Exchange | Wikidata | 1925-11-02 | Yahoo Finance | 2025-07-02 |
| AES | New York Stock Exchange | Yahoo Finance | 1991-06-26 | Wikidata | 1996-10-16 |
| U-Haul | New York Stock Exchange | Yahoo Finance | 1994-11-04 | Wikidata | 2022-12-19 |
| LG Corp | Korea Exchange | KRX KIND list | 1970-02-13 | Yahoo Finance | 2004-11-05 |
| Stifel | New York Stock Exchange | Yahoo Finance | 1983-07-19 | Wikidata | 1986-11-24 |
| CubeSmart | New York Stock Exchange | Yahoo Finance | 2004-10-22 | Wikidata | 2011-09-19 |
| Affiliated Managers Group | New York Stock Exchange | Yahoo Finance | 1997-11-21 | Wikidata | 1998-06-29 |
| Houlihan Lokey | New York Stock Exchange | Yahoo Finance | 2015-08-13 | Wikidata | 2026-05-10 |
| Shree Cement | National Stock Exchange of India | NSE equity list | 1995-04-26 | Yahoo Finance | 2001-07-02 |
| Murphy USA | New York Stock Exchange | Yahoo Finance | 2013-08-19 | Wikidata | 2013-09-03 |
| S-OIL | Korea Exchange | KRX KIND list | 1987-05-27 | Wikidata | 1987-05-08 |
| Stantec | New York Stock Exchange | Yahoo Finance | 2005-08-05 | Wikidata | 2008-07-31 |
| Food &amp; Life Companies | Tokyo Stock Exchange | Wikidata | 2017-03-22 | Yahoo Finance | 2017-03-31 |
| Lynas | Australian Securities Exchange | Wikidata | 1986-09-11 | Yahoo Finance | 1999-06-10 |
| MGM Resorts | New York Stock Exchange | Yahoo Finance | 1988-05-02 | Wikidata | 1990-01-12 |
| Oshkosh Corporation | New York Stock Exchange | Yahoo Finance | 1985-10-02 | Wikidata | 2002-07-01 |
| Sanmina | Nasdaq | Yahoo Finance | 1993-04-14 | Wikidata | 1993-06-22 |
| 360 Security Technology | Shanghai Stock Exchange | SSE company list | 2012-01-16 | Wikidata | 2018-02-28 |
| Rhythm Pharmaceuticals | Nasdaq | Yahoo Finance | 2017-10-09 | Wikidata | 2017-10-04 |
| Aurora Innovation | Nasdaq | Yahoo Finance | 2021-05-10 | Wikidata | 2021-05-06 |
| EPAM Systems | New York Stock Exchange | Yahoo Finance | 2012-02-08 | Wikidata | 2012-01-24 |
| Aptiv | New York Stock Exchange | Yahoo Finance | 2011-11-17 | Wikidata | 2017-12-05 |
| Powerchip Semiconductor Manufacturing | Taiwan Stock Exchange | TWSE ISIN list | 2021-12-06 | Yahoo Finance | 2020-12-09 |
| Lamb Weston | New York Stock Exchange | Yahoo Finance | 2016-11-10 | Wikidata | 2016-11-01 |
| Dahua Technology | Shenzhen Stock Exchange | SZSE company list | 2008-05-20 | Yahoo Finance | 2008-05-08 |
| Immunovant | Nasdaq | Yahoo Finance | 2019-06-21 | Wikidata | 2019-12-19 |
| IES Holdings | Nasdaq | Yahoo Finance | 1998-01-28 | Wikidata | 2006-05-15 |
| SM Energy | New York Stock Exchange | Yahoo Finance | 1992-12-16 | Wikidata | 1992-12-21 |
| Kunlun Tech | Shenzhen Stock Exchange | SZSE company list | 2015-01-21 | Yahoo Finance | 2015-02-27 |
| Pilgrim's Pride | Nasdaq | Yahoo Finance | 1987-12-30 | Wikidata | 2012-12-28 |
| Zillow | Nasdaq | Yahoo Finance | 2015-08-03 | Wikidata | 2011-07-20 |
| Linde India | National Stock Exchange of India | NSE equity list | 1999-06-16 | Yahoo Finance | 2000-05-31 |
| SAIC (Science Applications International Corp) | Nasdaq | Yahoo Finance | 2013-09-16 | Wikidata | 2013-09-30 |
| NOV | New York Stock Exchange | Yahoo Finance | 1996-10-29 | Wikidata | 2005-03-14 |
| Outfront Media | New York Stock Exchange | Yahoo Finance | 2014-03-28 | Wikidata | 2014-11-20 |
| EnPro Industries | New York Stock Exchange | Yahoo Finance | 2002-05-24 | Wikidata | 2002-06-03 |
| Kratos Defense &amp; Security Solutions | Nasdaq | Yahoo Finance | 1999-11-05 | Wikidata | 2007-09-17 |
| AutoNation | New York Stock Exchange | Yahoo Finance | 1990-05-11 | Wikidata | 1999-04-06 |
| TPG Telecom | Australian Securities Exchange | Wikidata | 2020-06-30 | Yahoo Finance | 2001-05-09 |
| Buenaventura Mining Company | New York Stock Exchange | Yahoo Finance | 1996-05-15 | Wikidata | 1996-05-20 |
| Parsons | New York Stock Exchange | Yahoo Finance | 2019-05-08 | Wikidata | 2019-05-18 |
| MiniMax Group | Hong Kong Stock Exchange | Wikidata | 2001-12-19 | Yahoo Finance | 2026-01-09 |
| Herc Holdings | New York Stock Exchange | Yahoo Finance | 2006-11-16 | Wikidata | 2016-07-01 |
| Giant Network Group | Shenzhen Stock Exchange | SZSE company list | 2011-03-02 | Yahoo Finance | 2011-03-10 |
| ONE Gas | New York Stock Exchange | Yahoo Finance | 2014-01-16 | Wikidata | 2014-02-03 |
| Hancock Whitney | Nasdaq | Yahoo Finance | 1991-06-04 | Wikidata | 2018-05-25 |
| Versant Media Group | Nasdaq | Yahoo Finance | 2025-12-15 | Wikidata | 2026-01-05 |
| EnerSys | New York Stock Exchange | Yahoo Finance | 2004-08-02 | Wikidata | 2004-07-29 |
| Brink's | New York Stock Exchange | Yahoo Finance | 1996-01-03 | Wikidata | 2003-05-05 |
| Iridium Communications | Nasdaq | Yahoo Finance | 2008-03-20 | Wikidata | 2009-09-24 |
| Colliers International | Nasdaq | Yahoo Finance | 1995-01-20 | Wikidata | 2003-08-27 |
| Mercury General | New York Stock Exchange | Yahoo Finance | 1985-11-20 | Wikidata | 1996-10-09 |
| Shanghai RAAS Blood Products | Shenzhen Stock Exchange | SZSE company list | 2008-06-23 | Yahoo Finance | 2008-06-11 |
| CSW Industrials | New York Stock Exchange | Yahoo Finance | 2015-09-30 | Wikidata | 2025-06-09 |
| Planet Labs | New York Stock Exchange | Yahoo Finance | 2021-04-26 | Wikidata | 2021-12-08 |
| MONETA Money Bank | Prague Stock Exchange | Wikidata | 2016-05-06 | Yahoo Finance | 2017-01-16 |
| Oklo | New York Stock Exchange | Yahoo Finance | 2021-07-08 | Wikidata | 2024-05-10 |
| Geo Group | New York Stock Exchange | Yahoo Finance | 1994-07-27 | Wikidata | 2004-01-21 |
| Hindustan Copper | National Stock Exchange of India | NSE equity list | 2010-09-15 | Yahoo Finance | 2010-01-08 |
| Exponent | Nasdaq | Yahoo Finance | 1990-08-17 | Wikidata | 1998-03-09 |
| Golar LNG | Nasdaq | Yahoo Finance | 2003-07-15 | Wikidata | 2002-12-18 |
| Signet Jewelers | New York Stock Exchange | Yahoo Finance | 1988-07-14 | Wikidata | 1998-06-03 |
| Flagstar Bank | New York Stock Exchange | Yahoo Finance | 1993-11-23 | Wikidata | 2024-10-15 |
| BancFirst | Nasdaq | Yahoo Finance | 1990-03-26 | Wikidata | 1994-01-04 |
| Columbia Sportswear | Nasdaq | Yahoo Finance | 1998-03-27 | Wikidata | 1998-06-29 |
| Greif | New York Stock Exchange | Yahoo Finance | 1996-02-28 | Wikidata | 2002-10-07 |
| Doosan Bobcat | Korea Exchange | KRX KIND list | 2016-11-18 | Yahoo Finance | 2016-11-22 |
| ZIM Integrated Shipping Services | New York Stock Exchange | Yahoo Finance | 2021-01-28 | Wikidata | 2021-01-24 |
| WillScot | Nasdaq | Yahoo Finance | 2015-11-05 | Wikidata | 2020-07-01 |
| Caliway Biopharmaceuticals | Taiwan Stock Exchange | TWSE ISIN list | 2024-10-02 | Yahoo Finance | 2022-12-26 |
| VisEra Technologies | Taiwan Stock Exchange | TWSE ISIN list | 2022-06-30 | Yahoo Finance | 2021-04-06 |
| Community Financial System | New York Stock Exchange | Yahoo Finance | 1985-11-26 | Wikidata | 1985-11-01 |
| ZPMC (Shanghai Zhenhua Heavy Industries) | Shanghai Stock Exchange | SSE company list | 2000-12-21 | Wikidata | 1997-08-05 |
| Breville Group | Australian Securities Exchange | Wikidata | 1999-05-25 | Yahoo Finance | 1999-02-25 |
| HD Construction Equipment | Korea Exchange | KRX KIND list | 2017-05-10 | Wikidata | 2017-05-17 |
| Graphic Packaging | New York Stock Exchange | Yahoo Finance | 1992-12-10 | Wikidata | 1995-12-18 |
| D-Wave Quantum | Nasdaq | Yahoo Finance | 2020-12-11 | Wikidata | 2022-08-08 |
| Dalmia Bharat | National Stock Exchange of India | NSE equity list | 2019-01-22 | Yahoo Finance | 2018-12-21 |
| Bangkok Expressway and Metro (BEM) | Stock Exchange of Thailand | Wikidata | 2015-12-30 | Yahoo Finance | 2006-09-21 |
| Force Motors | National Stock Exchange of India | NSE equity list | 2024-02-14 | Yahoo Finance | 2019-08-19 |
| Apollo Tyres | National Stock Exchange of India | NSE equity list | 1995-05-31 | Yahoo Finance | 2002-01-01 |
| Seadrill | New York Stock Exchange | Yahoo Finance | 2022-10-14 | Wikidata | 2018-07-03 |
| Grindr | New York Stock Exchange | Yahoo Finance | 2021-01-14 | Wikidata | 2022-11-18 |
| IGO Limited | Australian Securities Exchange | Wikidata | 2002-01-17 | Yahoo Finance | 2002-01-03 |
| Garden Reach Shipbuilders & Engineers Limited | National Stock Exchange of India | NSE equity list | 2018-10-10 | Yahoo Finance | 2018-10-24 |
| ePlus | Nasdaq | Yahoo Finance | 1996-11-15 | Wikidata | 1999-11-01 |
| Porch Group | Nasdaq | Yahoo Finance | 2020-01-13 | Wikidata | 2020-12-24 |
| Clover Health Investments | Nasdaq | Yahoo Finance | 2020-06-12 | Wikidata | 2021-01-08 |
| Encore Capital Group | Nasdaq | Yahoo Finance | 1999-07-09 | Wikidata | 2002-04-09 |
| Buckle | New York Stock Exchange | Yahoo Finance | 1992-05-08 | Wikidata | 1997-05-14 |
| Shriram Pistons &amp; Rings | National Stock Exchange of India | NSE equity list | 2016-06-02 | Yahoo Finance | 2016-06-09 |
| Super Retail Group | Australian Securities Exchange | Wikidata | 2004-07-06 | Yahoo Finance | 2004-05-31 |
| QuantumScape | Nasdaq | Yahoo Finance | 2020-08-17 | Wikidata | 2025-12-23 |
| Under Armour | New York Stock Exchange | Yahoo Finance | 2016-03-23 | Wikidata | 2005-11-18 |
| Monarch Casino &amp; Resort | Nasdaq | Yahoo Finance | 1993-08-06 | Wikidata | 1993-08-10 |
| Kemper | New York Stock Exchange | Yahoo Finance | 1990-04-23 | Wikidata | 2011-08-25 |
| Energizer Holdings | New York Stock Exchange | Yahoo Finance | 2015-06-12 | Wikidata | 2000-03-27 |
| United Parks &amp; Resorts | New York Stock Exchange | Yahoo Finance | 2013-04-19 | Wikidata | 2024-02-13 |
| Federal Agricultural Mortgage Corporation | New York Stock Exchange | Yahoo Finance | 1994-02-10 | Wikidata | 1999-06-18 |
| AB Ignitis grupe | Nasdaq Vilnius | Wikidata | 2010-10-07 | Yahoo Finance | 2020-10-07 |
| Global Industrial Company | New York Stock Exchange | Yahoo Finance | 1995-06-27 | Wikidata | 2021-06-21 |
| Dentsply Sirona | Nasdaq | Yahoo Finance | 1987-08-12 | Wikidata | 1991-04-25 |
| Sarepta Therapeutics | Nasdaq | Yahoo Finance | 1997-06-04 | Wikidata | 2012-07-12 |
| Paradox Interactive | Nasdaq Stockholm | Wikidata | 2026-06-09 | Yahoo Finance | 2016-05-31 |
| Upbound Group | Nasdaq | Yahoo Finance | 1995-01-25 | Wikidata | 2023-02-27 |
| Ingenia Communities Group | Australian Securities Exchange | Wikidata | 2004-07-01 | Yahoo Finance | 2012-06-13 |
| Hub Group | Nasdaq | Yahoo Finance | 1996-03-13 | Wikidata | 2002-04-23 |
| Marksans Pharma | National Stock Exchange of India | NSE equity list | 2002-01-21 | Yahoo Finance | 2002-07-19 |
| Bega Cheese | Australian Securities Exchange | Wikidata | 2011-08-19 | Yahoo Finance | 2011-08-30 |
| CRA International | Nasdaq | Yahoo Finance | 1998-04-24 | Wikidata | 1998-06-29 |
| Liontown Resources | Australian Securities Exchange | Wikidata | 2006-12-27 | Yahoo Finance | 2006-12-22 |
| Pagaya Technologies | Nasdaq | Yahoo Finance | 2021-04-21 | Wikidata | 2022-06-23 |
| BJ's Restaurants | Nasdaq | Yahoo Finance | 1996-10-09 | Wikidata | 2004-08-16 |
| Wolfspeed | New York Stock Exchange | Yahoo Finance | 2025-09-29 | Wikidata | 2021-10-04 |
| Banpu Public Company | Stock Exchange of Thailand | Wikidata | 1989-06-16 | Yahoo Finance | 2016-10-28 |
| Preferred Bank | Nasdaq | Yahoo Finance | 1999-08-19 | Wikidata | 2005-02-15 |
| Six Flags | New York Stock Exchange | Yahoo Finance | 1987-04-23 | Wikidata | 2024-07-02 |
| Cyient | National Stock Exchange of India | NSE equity list | 1998-09-30 | Yahoo Finance | 2006-07-28 |
| Trump Media &amp; Technology Group | Nasdaq | Yahoo Finance | 2021-09-30 | Wikidata | 2024-03-26 |
| Great Lakes Dredge &amp; Dock Corp. | Nasdaq | Yahoo Finance | 2026-04-01 | Wikidata | 2006-12-27 |
| Bitdeer Technologies Group | Nasdaq | Yahoo Finance | 2021-07-28 | Wikidata | 2023-04-14 |
| Unitil Corporation | New York Stock Exchange | Yahoo Finance | 1985-03-07 | Wikidata | 1992-03-17 |
| Whitestone REIT | New York Stock Exchange | Yahoo Finance | 2026-07-14 | Wikidata | 2010-08-26 |
| Sudarshan Chemical | National Stock Exchange of India | NSE equity list | 1995-05-25 | Yahoo Finance | 2005-03-03 |
| Central Pacific Financial | New York Stock Exchange | Yahoo Finance | 1987-08-28 | Wikidata | 2002-12-31 |
| Immatics | Nasdaq | Yahoo Finance | 2018-12-12 | Wikidata | 2020-07-01 |
| Strides Pharma | National Stock Exchange of India | NSE equity list | 2000-02-02 | Yahoo Finance | 2002-06-26 |
| Service Stream Limited | Australian Securities Exchange | Wikidata | 2004-12-09 | Yahoo Finance | 2004-02-20 |
| Kingfa Science & Technology | National Stock Exchange of India | NSE equity list | 2016-11-15 | Yahoo Finance | 2010-01-08 |
| BlackSky Technology | New York Stock Exchange | Yahoo Finance | 2019-12-20 | Wikidata | 2021-09-10 |
| CEWE | Frankfurt Stock Exchange | Wikidata | 1993-03-24 | Yahoo Finance | 2013-12-16 |
| DoubleUGames | Korea Exchange | KRX KIND list | 2019-03-12 | Yahoo Finance | 2015-11-04 |
| MMTC | National Stock Exchange of India | NSE equity list | 2012-04-09 | Yahoo Finance | 2010-01-08 |
| Daily Journal | Nasdaq | Yahoo Finance | 1986-06-11 | Wikidata | 1992-04-13 |
| OppFi | New York Stock Exchange | Yahoo Finance | 2020-11-20 | Wikidata | 2021-07-21 |
| Kelsian Group | Australian Securities Exchange | Wikidata | 2013-10-16 | Yahoo Finance | 2014-01-10 |
| Lexicon Pharmaceuticals | Nasdaq | Yahoo Finance | 2000-04-07 | Wikidata | 2000-06-23 |
| Arena REIT | Australian Securities Exchange | Wikidata | 2013-06-13 | Yahoo Finance | 2013-07-01 |
| Tata Teleservices | National Stock Exchange of India | NSE equity list | 2000-10-20 | Yahoo Finance | 2000-10-26 |
| Golden Entertainment | Nasdaq | Yahoo Finance | 2026-04-30 | Wikidata | 2015-08-04 |
| Paisalo Digital | National Stock Exchange of India | NSE equity list | 2011-10-17 | Yahoo Finance | 2009-06-16 |
| FleetPartners Group | Australian Securities Exchange | Wikidata | 2023-03-23 | Yahoo Finance | 2015-04-22 |
| Scholastic | Nasdaq | Yahoo Finance | 1992-02-25 | Wikidata | 1987-05-12 |
| Energy Vault | New York Stock Exchange | Yahoo Finance | 2021-03-29 | Wikidata | 2022-02-14 |
| Kirloskar Ferrous Industries | National Stock Exchange of India | NSE equity list | 2026-04-20 | Yahoo Finance | 2019-11-13 |
| SPARC | National Stock Exchange of India | NSE equity list | 2007-07-18 | Yahoo Finance | 2003-01-14 |
| West Coast Community Bancorp | Nasdaq | Yahoo Finance | 2005-02-17 | Wikidata | 2026-09-16 |
| Arbutus Biopharma | Nasdaq | Yahoo Finance | 2007-07-26 | Wikidata | 2015-08-03 |
| MyState Limited | Australian Securities Exchange | Wikidata | 2009-09-10 | Yahoo Finance | 2009-09-17 |
| Civmec Limited | Australian Securities Exchange | Wikidata | 2018-06-22 | Yahoo Finance | 2018-08-06 |
| Ginkgo Bioworks | New York Stock Exchange | Yahoo Finance | 2021-04-19 | Wikidata | 2021-09-17 |
| Bally's Corporation | New York Stock Exchange | Yahoo Finance | 2024-12-06 | Wikidata | 2020-11-09 |
| TAT Technologies | Nasdaq | Yahoo Finance | 1987-03-31 | Wikidata | 1993-03-11 |
| Amarin Corporation | Nasdaq | Yahoo Finance | 1993-04-01 | Wikidata | 1993-04-05 |
| Hertz | Nasdaq | Yahoo Finance | 2021-07-01 | Wikidata | 2016-06-20 |
| Texmaco Rail &amp; Engineering | National Stock Exchange of India | NSE equity list | 2011-03-03 | Yahoo Finance | 2004-09-09 |
| Calavo Growers | Nasdaq | Yahoo Finance | 2026-05-28 | Wikidata | 2002-03-22 |
| Jeju Air | Korea Exchange | KRX KIND list | 2015-11-06 | Yahoo Finance | 2014-08-26 |
| ATN International | Nasdaq | Yahoo Finance | 1991-11-14 | Wikidata | 2006-05-23 |
| Jakks Pacific | Nasdaq | Yahoo Finance | 1996-05-02 | Wikidata | 1998-06-29 |
| HIVE Digital Technologies | Nasdaq | Yahoo Finance | 2011-02-02 | Wikidata | 2021-07-01 |
| Kalyani Steels | National Stock Exchange of India | NSE equity list | 2010-05-19 | Yahoo Finance | 2008-10-21 |
| Aeris Resources | Australian Securities Exchange | Wikidata | 2011-02-02 | Yahoo Finance | 2011-02-11 |
| Bafang Yunji | Taiwan Stock Exchange | TWSE ISIN list | 2021-09-09 | Yahoo Finance | 2020-09-29 |
| Claritev | New York Stock Exchange | Yahoo Finance | 2020-04-03 | Wikidata | 2025-02-28 |
| Greenply | National Stock Exchange of India | NSE equity list | 1996-03-06 | Yahoo Finance | 2002-07-03 |
| Kingstone Companies | Nasdaq | Yahoo Finance | 1999-10-26 | Wikidata | 2009-07-02 |
| Asure Software | Nasdaq | Yahoo Finance | 1992-04-07 | Wikidata | 2007-09-13 |
| Perma-Fix Environmental Services | Nasdaq | Yahoo Finance | 1992-12-08 | Wikidata | 1995-08-18 |
| Agenus | Nasdaq | Yahoo Finance | 2000-02-08 | Wikidata | 2000-02-04 |
| Lifeway Foods | Nasdaq | Yahoo Finance | 1988-12-29 | Wikidata | 1995-08-18 |
| Clearwater Paper | New York Stock Exchange | Yahoo Finance | 2008-12-05 | Wikidata | 2008-12-17 |
| Siyaram Silk Mills | National Stock Exchange of India | NSE equity list | 2007-01-29 | Yahoo Finance | 2002-04-19 |
| Confidence Petroleum | National Stock Exchange of India | NSE equity list | 2019-06-13 | Yahoo Finance | 2020-10-23 |
| Remedy Entertainment | Nasdaq Helsinki | Wikidata | 2017-05-02 | Yahoo Finance | 2017-05-29 |
| Neowiz Games | KOSDAQ | KRX KIND list | 2007-07-02 | Yahoo Finance | 2007-04-23 |
| Firy Inc. | New York Stock Exchange | Yahoo Finance | 2020-04-27 | Wikidata | 2026-06-22 |
| First Internet Bancorp | Nasdaq | Yahoo Finance | 2006-04-05 | Wikidata | 2013-02-22 |
| AC Immune | Nasdaq | Yahoo Finance | 2016-09-23 | Wikidata | 2016-09-13 |
| Air Asia Company Limited (AACL) | Taiwan Stock Exchange | TWSE ISIN list | 2018-02-22 | Yahoo Finance | 2017-02-24 |
| Solvar Limited | Australian Securities Exchange | Wikidata | 2006-10-19 | Yahoo Finance | 2006-08-16 |
| GCL Global Holdings Ltd | Nasdaq | Yahoo Finance | 2022-04-20 | Wikidata | 2025-02-14 |
| Digimarc | Nasdaq | Yahoo Finance | 1999-12-02 | Wikidata | 2005-04-15 |
| Oramed Pharmaceuticals | Nasdaq | Yahoo Finance | 2007-05-01 | Wikidata | 2006-04-10 |
| Cogent Communications | Nasdaq | Yahoo Finance | 2002-02-05 | Wikidata | 2006-03-06 |
| Paysafe | New York Stock Exchange | Yahoo Finance | 2020-10-09 | Wikidata | 2021-03-31 |
| Oriental Aromatics | National Stock Exchange of India | NSE equity list | 2019-07-11 | Yahoo Finance | 2020-04-15 |
| Ten Square Games | Warsaw Stock Exchange | Wikidata | 2018-05-11 | Yahoo Finance | 2018-09-25 |
| Commercial Vehicle Group (CVG) | Nasdaq | Yahoo Finance | 2004-08-09 | Wikidata | 2004-08-05 |
| Rico Auto Industries | National Stock Exchange of India | NSE equity list | 2003-05-12 | Yahoo Finance | 2002-07-02 |
| Medifast | New York Stock Exchange | Yahoo Finance | 1993-12-30 | Wikidata | 2002-12-20 |
| Orion Properties | New York Stock Exchange | Yahoo Finance | 2021-11-23 | Wikidata | 2021-11-15 |
| Neighborhood Intelligence | Nasdaq | Yahoo Finance | 2002-05-30 | Wikidata | 2026-08-17 |
| China Automotive Systems | Nasdaq | Yahoo Finance | 2003-03-24 | Wikidata | 2003-05-21 |
| DelfinGroup AS | Nasdaq Riga | Wikidata | 2021-10-20 | Yahoo Finance | 2021-10-27 |
| Talga Group | Australian Securities Exchange | Wikidata | 2010-07-09 | Yahoo Finance | 2011-01-17 |
| Wrap Technologies | Nasdaq | Yahoo Finance | 2018-05-29 | Wikidata | 2020-12-01 |
| Al Kathiri Holding Company | Saudi Exchange | Wikidata | 2017-07-09 | Yahoo Finance | 2019-11-04 |
| Lifevantage | Nasdaq | Yahoo Finance | 1994-04-07 | Wikidata | 2007-02-05 |
| VivoPower | Nasdaq | Yahoo Finance | 2015-05-27 | Wikidata | 1992-02-26 |
| N.B.I. Industrial Finance | National Stock Exchange of India | NSE equity list | 2016-11-23 | Yahoo Finance | 2016-12-07 |
| Wallbox | New York Stock Exchange | Yahoo Finance | 2021-04-19 | Wikidata | 2021-10-04 |
| 3i Infotech | National Stock Exchange of India | NSE equity list | 2021-10-22 | Yahoo Finance | 2005-04-22 |
| Harvard Bioscience | Nasdaq | Yahoo Finance | 2001-03-19 | Wikidata | 2000-12-07 |
| Kandi Technologies Group | Nasdaq | Yahoo Finance | 2007-09-04 | Wikidata | 2007-09-24 |
| Rave Restaurant Group | Nasdaq | Yahoo Finance | 1993-09-01 | Wikidata | 2015-01-09 |
| Xos, Inc. | Nasdaq | Yahoo Finance | 2020-12-08 | Wikidata | 2021-08-20 |
| Destination XL | Nasdaq | Yahoo Finance | 1987-06-02 | Wikidata | 1992-02-25 |
| Workhorse Group | Nasdaq | Yahoo Finance | 2010-06-02 | Wikidata | 2015-12-11 |
| SUNation Energy Inc. | Nasdaq | Yahoo Finance | 1981-11-18 | Wikidata | 2013-05-30 |
| Stem, Inc | New York Stock Exchange | Yahoo Finance | 2020-10-08 | Wikidata | 2021-04-29 |
| Neonode | Nasdaq | Yahoo Finance | 1989-01-09 | Wikidata | 1992-03-03 |
| Gameone | Hong Kong Stock Exchange | Wikidata | 2016-01-13 | Yahoo Finance | 2016-01-18 |
| SunPower | Nasdaq | Yahoo Finance | 2023-07-18 | Wikidata | 2005-11-17 |

## First trading days looked up by hand (11)

- Intel: Nasdaq, 1971-10-13 ([Intel's investor FAQ](https://www.intc.com/stock-info/faq))
- Johnson & Johnson: New York Stock Exchange, 1944-09-25 ([The Motley Fool (J&J dates its IPO the 24th, a Sunday)](https://www.fool.com/investing/general/2013/09/25/2-legendary-beginnings-a-disastrous-bank-failure-a.aspx))
- Caterpillar: New York Stock Exchange, 1929-12-02 ([Caterpillar](https://www.caterpillar.com/en/news/corporate-press-releases/h/caterpillar-celebrates-85-years-on-the-new-york-stock-exchange.html))
- Texas Instruments: New York Stock Exchange, 1953-10-01 ([TI's investor FAQ](https://investor.ti.com/node/5941))
- Inditex: Bolsa de Madrid, 2001-05-23 ([BBC News](http://news.bbc.co.uk/2/hi/business/1346473.stm))
- General Electric: New York Stock Exchange, 1892-06-23 ([The Motley Fool](https://www.fool.com/investing/general/2013/04/15/the-dawn-of-the-dows-most-durable-company.aspx))
- L'Oréal: Euronext Paris, 1963-10-08 ([L'Oréal Finance](https://www.loreal-finance.com/fr/laction))
- Nestlé: SIX Swiss Exchange, 1905-10-25 ([Nestlé's investor FAQ (Zurich Stock Exchange)](https://www.nestle.com/investors/faqs))
- 3M: New York Stock Exchange, 1946-01-14 ([3M's investor FAQ](https://investors.3m.com/resources/faq))
- American Express: New York Stock Exchange, 1977-05-18 ([AInvest and Moomoo listing dates](https://www.ainvest.com/stocks/NYSE-AXP/profile/))
- Coca-Cola: New York Stock Exchange, 1919 ([Coca-Cola, via 11Alive](https://11alive.com/article/money/business/world-of-coca-cola-free-admission-100-years/85-3e5edddf-a123-46b4-8281-bd260afaf0b8))

## First trades timed by the Rodden library (7)

- Apple, 1980-12-12 10:00 (Apple, Shares)
- Microsoft, 1986-03-13 09:30 (Microsoft, Shares)
- Alphabet (Google), 2004-08-19 11:55 (Google First Trade)
- Meta Platforms (Facebook), 2012-05-18 11:30 (Facebook, First Trade)
- Cisco, 1990-02-16 09:30 (Cisco Systems, Shares)
- Oracle, 1986-03-12 09:30 (Oracle, Shares)
- Infineon, 2000-03-13 09:00 (Infineon, Shares)

## Listed before the founding year Wikidata gives (148)

Usually a predecessor's listing or an inception that is a later re-founding.

- Alphabet (Google): listed 2004-08-19 (Nasdaq), founded 2015-10-02
- Cisco: listed 1990-02-16 (Nasdaq), founded 2021
- Morgan Stanley: listed 1993-02-23 (New York Stock Exchange), founded 2008-07-17
- RTX: listed 1962-04-02 (New York Stock Exchange), founded 2020-04-03
- Mitsubishi UFJ Financial: listed 2001-04-02 (New York Stock Exchange), founded 2005-10-01
- KLA: listed 1980-10-08 (Nasdaq), founded 1997
- BHP Group: listed 1885-08-13 (Australian Securities Exchange), founded 2001
- Danaher: listed 1978-12-29 (New York Stock Exchange), founded 1981
- AT&T: listed 1983-11-21 (New York Stock Exchange), founded 2005
- Banco Bilbao Vizcaya Argentaria: listed 1988-12-15 (New York Stock Exchange), founded 1999
- CME Group: listed 2002-12-06 (Nasdaq), founded 2007-07-12
- Enbridge: listed 1984-03-15 (New York Stock Exchange), founded 1987-12-15
- GSK plc: listed 1980-03-28 (New York Stock Exchange), founded 2000-12-27
- Equinor: listed 2001-06-18 (New York Stock Exchange), founded 2007-10-01
- Westpac Banking: listed 1970-07-18 (Australian Securities Exchange), founded 1982-10
- PNC Financial Services: listed 1975-11-17 (New York Stock Exchange), founded 1982
- Simon Property Group: listed 1993-12-14 (New York Stock Exchange), founded 1998
- Cadence Design Systems: listed 1987-06-10 (Nasdaq), founded 1988
- Royal Caribbean Group: listed 1993-04-28 (New York Stock Exchange), founded 1997
- Mondelez International: listed 2001-06-13 (Nasdaq), founded 2012
- CPKC (Canadian Pacific Kansas City): listed 1983-12-30 (New York Stock Exchange), founded 2023-04-14
- EOG Resources: listed 1989-10-04 (New York Stock Exchange), founded 1999
- Itaú Unibanco: listed 2002-02-25 (New York Stock Exchange), founded 2008
- Lloyds Banking Group: listed 2001-11-28 (New York Stock Exchange), founded 2009-01
- Aon: listed 1980-06-02 (New York Stock Exchange), founded 1982
- Cencora: listed 1995-04-04 (New York Stock Exchange), founded 2001
- Fubon Financial: listed 2001-12-19 (Taiwan Stock Exchange), founded 2008-12-19
- Diageo: listed 1991-03-14 (New York Stock Exchange), founded 1997-12-17
- Garmin: listed 2000-12-08 (New York Stock Exchange), founded 2010-02-09
- Thales: listed 1998-12-30 (Euronext Paris), founded 2000-12-06
- Keurig Dr Pepper: listed 2008-05-07 (Nasdaq), founded 2018
- DNB: listed 1992-08-17 (Oslo Børs), founded 2002-09-10
- Wabtec: listed 1995-06-16 (New York Stock Exchange), founded 1999
- Exelon Corporation: listed 1973-05-02 (New York Stock Exchange), founded 2000
- Ventas: listed 1997-05-05 (New York Stock Exchange), founded 1998
- Commerzbank: listed 1870-02-26 (Frankfurt Stock Exchange), founded 1958-11-04
- ArcelorMittal: listed 1997-08-07 (New York Stock Exchange), founded 2006
- Thomson Reuters: listed 2002-06-12 (Nasdaq), founded 2008-04-17
- IQVIA: listed 2013-05-09 (New York Stock Exchange), founded 2016
- Ambev: listed 1997-03-05 (New York Stock Exchange), founded 1999
- AngloGold Ashanti: listed 1998-08-05 (New York Stock Exchange), founded 2004
- Ciena: listed 1997-02-07 (New York Stock Exchange), founded 1999
- Rocket Lab: listed 2020-11-24 (Nasdaq), founded 2025-05-23
- TKO Group Holdings: listed 1999-10-19 (New York Stock Exchange), founded 2023-09-12
- Ping An Bank: listed 1991-04-03 (Shenzhen Stock Exchange), founded 1995
- CK Hutchison Holdings: listed 1972-11-01 (Hong Kong Stock Exchange), founded 2015-03-18
- Ingersoll Rand: listed 2017-05-12 (New York Stock Exchange), founded 2020-02
- Willis Towers Watson: listed 2001-06-12 (Nasdaq), founded 2016
- Fortescue: listed 1987-03-19 (Australian Securities Exchange), founded 2003
- International Consolidated Airlines: listed 2007-05-10 (OTC Markets), founded 2011-01-21
- Tapestry: listed 2000-10-06 (New York Stock Exchange), founded 2017
- Incyte: listed 1993-11-04 (Nasdaq), founded 2001
- TechnipFMC: listed 2001-06-15 (New York Stock Exchange), founded 2017-01-17
- Kinross Gold: listed 1981-03-17 (New York Stock Exchange), founded 1993
- Shanghai International Port Group (SIPG): listed 2000-07-19 (Shanghai Stock Exchange), founded 2003
- CRRC: listed 2008-08-18 (Shanghai Stock Exchange), founded 2015-06-01
- BCE Inc.: listed 1982-11-15 (New York Stock Exchange), founded 1983
- Royal Gold: listed 1981-06-09 (Nasdaq), founded 1991
- Skyworks Solutions: listed 1984-09-07 (Nasdaq), founded 2002
- Geely: listed 1973-02-23 (Hong Kong Stock Exchange), founded 1986
- Ovintiv: listed 2002-04-08 (New York Stock Exchange), founded 2020
- Suncorp: listed 1988-07-07 (Australian Securities Exchange), founded 1996
- Origin Energy: listed 1961-07-13 (Australian Securities Exchange), founded 2000
- Vodafone Idea: listed 2007-03-09 (National Stock Exchange of India), founded 2018-08-31
- Japan Exchange Group: listed 2004-04-01 (Tokyo Stock Exchange), founded 2013
- SK Innovation: listed 2007-07-25 (Korea Exchange), founded 2011
- Flutter Entertainment: listed 2002-10-04 (New York Stock Exchange), founded 2016
- HD Korea Shipbuilding &amp; Offshore Engineering: listed 1999-08-24 (Korea Exchange), founded 2019-06-03
- Unum: listed 1986-11-06 (New York Stock Exchange), founded 1999
- CSPC Pharmaceutical Group Limited: listed 1994-06-21 (Hong Kong Stock Exchange), founded 1997-08-21
- Sirius XM: listed 1994-09-13 (Nasdaq), founded 2008-07-29
- Stellantis: listed 2010-06-09 (New York Stock Exchange), founded 2021-01-16
- Knight-Swift Transportation: listed 1994-10-25 (New York Stock Exchange), founded 2017
- Match Group: listed 1993-01-19 (Nasdaq), founded 2009
- Kunlun Energy Company: listed 1973-03-13 (Hong Kong Stock Exchange), founded 1993
- MGM Resorts: listed 1988-05-02 (New York Stock Exchange), founded 2000-05-31
- Randstad: listed 1905-06-12 (Euronext Amsterdam), founded 1960
- Vicinity Centres: listed 2011-12-05 (Australian Securities Exchange), founded 2015-06-11
- DB Insurance: listed 1973-06-28 (Korea Exchange), founded 1993
- Molson Coors: listed 1975-06-12 (New York Stock Exchange), founded 2005
- VIAVI Solutions: listed 1993-11-17 (Nasdaq), founded 2015
- Sojitz Corporation: listed 2003-04-01 (Tokyo Stock Exchange), founded 2004
- San’an Optoelectronics: listed 1996-05-28 (Shanghai Stock Exchange), founded 2000
- China Rare Earth Resources And Technology: listed 1998-09-11 (Shenzhen Stock Exchange), founded 2021-12-23
- The Mosaic Company: listed 1988-01-26 (New York Stock Exchange), founded 2004
- JBT Marel Corporation: listed 2008-07-22 (New York Stock Exchange), founded 2025
- Glacier Bancorp: listed 1984-03-22 (Nasdaq), founded 1990
- Kratos Defense &amp; Security Solutions: listed 1999-11-05 (Nasdaq), founded 2004
- AutoNation: listed 1990-05-11 (New York Stock Exchange), founded 1996
- Alibaba Health Information Technology: listed 1972-07-06 (Hong Kong Stock Exchange), founded 2004
- Shanghai Lujiazui Finance & Trade Zone Development Co.,Ltd.: listed 1993-06-28 (Shanghai Stock Exchange), founded 1994
- CTF Services Limited: listed 1997-04-25 (Hong Kong Stock Exchange), founded 2003
- West Fraser Timber: listed 2009-02-13 (New York Stock Exchange), founded 2020
- VEON: listed 1996-11-15 (Nasdaq), founded 2009
- China Resources Gas Group: listed 1994-11-07 (Hong Kong Stock Exchange), founded 1999
- Avis Budget Group: listed 1983-09-14 (Nasdaq), founded 2006
- Joby Aviation: listed 2020-11-09 (New York Stock Exchange), founded 2021
- Air France-KLM: listed 1999-02-22 (Euronext Paris), founded 2004-05-05
- Liberty Global: listed 2004-06-09 (Nasdaq), founded 2005
- Lionsgate Studios: listed 2022-03-01 (New York Stock Exchange), founded 2024-05-14
- Avient: listed 1999-09-13 (New York Stock Exchange), founded 2000
- Bath &amp; Body Works: listed 1982-04-01 (New York Stock Exchange), founded 1990
- WillScot: listed 2015-11-05 (Nasdaq), founded 2020-07-01
- SkyWest: listed 1986-06-26 (Nasdaq), founded 2005-09-08
- WisdomTree: listed 1993-03-04 (New York Stock Exchange), founded 2006
- Acadia Realty Trust: listed 1993-05-27 (New York Stock Exchange), founded 1998
- Guoco: listed 1983-05-03 (Hong Kong Stock Exchange), founded 1991
- Fuji Oil Holdings: listed 1978-10-02 (Tokyo Stock Exchange), founded 2015-10-01
- Taseko Mines: listed 1992-03-25 (NYSE American), founded 1999
- Innospec: listed 1998-05-13 (Nasdaq), founded 1999
- Iluka Resources: listed 1962-06-30 (Australian Securities Exchange), founded 1998
- Magellan Financial Group: listed 2004-07-01 (Australian Securities Exchange), founded 2006
- YOOZOO Interactive: listed 2007-09-25 (Shenzhen Stock Exchange), founded 2009
- Edgewell Personal Care: listed 2000-03-27 (New York Stock Exchange), founded 2015-07-01
- Biglari: listed 1992-02-25 (New York Stock Exchange), founded 2008
- Six Flags: listed 1987-04-23 (New York Stock Exchange), founded 2024-07-01
- RPC, Inc.: listed 1984-06-11 (New York Stock Exchange), founded 1991
- Fnac Darty: listed 2013-06-20 (Euronext Paris), founded 2016-07-18
- Webjet Limited: listed 1997-11-19 (Australian Securities Exchange), founded 1998
- China Everbright Limited: listed 1973-02-26 (Hong Kong Stock Exchange), founded 1997
- Arafura Rare Earths: listed 2003-11-05 (Australian Securities Exchange), founded 2006
- Clearfield: listed 1986-08-06 (Nasdaq), founded 2008
- Core Laboratories: listed 1995-09-21 (New York Stock Exchange), founded 1998
- Frontera Energy: listed 2016-11-03 (Toronto Stock Exchange), founded 2017-06-12
- Anora Group: listed 2018-03-23 (Nasdaq Helsinki), founded 2021
- FRP Holdings: listed 1986-07-02 (Nasdaq), founded 1988
- Braskem: listed 1999-01-13 (New York Stock Exchange), founded 2002
- Wing Tai Properties: listed 1973-02-07 (Hong Kong Stock Exchange), founded 2010
- PowerFleet: listed 1999-06-30 (Nasdaq), founded 2019
- Jumbo Interactive Limited: listed 1972-06-14 (Australian Securities Exchange), founded 1995
- Reliance Infrastructure: listed 1995-02-08 (National Stock Exchange of India), founded 2002
- Ribbon Communications: listed 2000-05-25 (Nasdaq), founded 2017
- Nekkar ASA: listed 1995-05-02 (Oslo Børs), founded 1996
- Conduent: listed 2016-12-13 (New York Stock Exchange), founded 2017
- Digital Domain: listed 1992-07-06 (Hong Kong Stock Exchange), founded 1993
- Franklin Covey: listed 1992-06-03 (New York Stock Exchange), founded 1997
- Hong Kong Technology Venture Company (HKTV): listed 1997-08-04 (Hong Kong Stock Exchange), founded 2014
- Vaxart: listed 1981-12-11 (Nasdaq), founded 2004-01-01
- LiveWire Group: listed 2020-11-24 (New York Stock Exchange), founded 2021
- Emperor International: listed 1972-11-14 (Hong Kong Stock Exchange), founded 1973
- Lifevantage: listed 1994-04-07 (Nasdaq), founded 2003
- Nerdy, Inc,: listed 2020-11-27 (New York Stock Exchange), founded 2021
- Kandi Technologies Group: listed 2007-09-04 (Nasdaq), founded 2013-04-19
- Kartoon Studios: listed 2012-02-03 (Nasdaq), founded 2013-11
- Immutep: listed 1988-06-23 (Australian Securities Exchange), founded 2001
- All in! Games: listed 2013-01-08 (Warsaw Stock Exchange), founded 2018
- Imugene: listed 1993-11-24 (Australian Securities Exchange), founded 2012
- Neonode: listed 1989-01-09 (Nasdaq), founded 2002

## Index members not found among the companies (79)

- AEX: RELX Group
- DAX: Scout24
- Euro Stoxx 50: Ferrari
- FTSE 100: Alliance Witan
- FTSE 100: Coca-Cola Europacific Partners
- FTSE 100: F & C Investment Trust
- FTSE 100: Fresnillo plc
- FTSE 100: Polar Capital Technology Trust
- FTSE 100: RELX
- FTSE 100: Rio Tinto (corporation)
- FTSE 100: Scottish Mortgage Investment Trust
- FTSE MIB: Ferrari
- Hang Seng: China Hongqiao Group
- Hang Seng: China Resources Mixc Lifestyle
- Hang Seng: Haier
- Hang Seng: Hengan International
- Hang Seng: Sands China
- Hang Seng: Shenzhou International
- Hang Seng: Xinyi Solar
- Nasdaq-100: Coca-Cola Europacific Partners
- Nasdaq-100: CoreWeave
- Nasdaq-100: Lumentum
- Nasdaq-100: PayPal
- Nasdaq-100: Pinduoduo
- Nasdaq-100: Rocket Lab
- Nifty 50: Tata Motors Passenger Vehicles
- Nikkei 225: All Nippon Airways
- Nikkei 225: Alps Electric
- Nikkei 225: Aozora Bank
- Nikkei 225: Asahi Breweries
- Nikkei 225: Chiba Bank
- Nikkei 225: Comsys
- Nikkei 225: Credit Saison
- Nikkei 225: Dai-ichi Life
- Nikkei 225: Daiichi Sankyo
- Nikkei 225: Denki Kagaku Kogyo
- Nikkei 225: Dentsu
- Nikkei 225: Fujikura
- Nikkei 225: Fukuoka Financial Group
- Nikkei 225: Haseko
- Nikkei 225: Hoya Corporation
- Nikkei 225: JTEKT
- Nikkei 225: Japan Steel Works
- Nikkei 225: Kuraray
- Nikkei 225: Lasertec
- Nikkei 225: Marui
- Nikkei 225: Mercari
- Nikkei 225: Mitsui
- Nikkei 225: NTN Corporation
- Nikkei 225: Nippon Electric Glass
- Nikkei 225: Nippon Express
- Nikkei 225: Nisshin Seifun Group
- Nikkei 225: Nitori
- Nikkei 225: Nitto Denko
- Nikkei 225: Nomura Holdings
- Nikkei 225: Nomura Research Institute
- Nikkei 225: Otsuka Holdings
- Nikkei 225: Resonac
- Nikkei 225: SHIFT Inc.
- Nikkei 225: Sapporo Brewery
- Nikkei 225: Secom
- Nikkei 225: Shizuoka Bank
- Nikkei 225: Socionext
- Nikkei 225: Sompo Holdings
- Nikkei 225: Sumitomo Group
- Nikkei 225: T&D Holdings
- Nikkei 225: Teijin
- Nikkei 225: Tokai Carbon
- Nikkei 225: Tokuyama Corporation
- Nikkei 225: Tokyu Land
- Nikkei 225: Yamato Transport
- Nikkei 225: ZOZO
- S&P 500: Skydance
- S&P/ASX 50: Rio Tinto (corporation)
- S&P/ASX 50: Sigma Healthcare
- S&P/ASX 50: The Vanguard Group
- S&P/TSX 60: Brookfield Asset Management
- SMI: Amrize
- SMI: Roche Holding AG
