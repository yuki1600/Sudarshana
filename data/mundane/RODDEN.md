# Rodden library × Research databases

The cross-check of tools/mundane_rodden.py: the Rodden library's event charts (AA and A rated, BTS/) against the Research databases
(data/mundane). Matched: both moments within 3 minutes, or the same day, kind and place (500 km). Research takes Rodden's time where it
has none to the minute; where both are timed and differ, Research keeps its own. Unmatched Rodden events are added to Research
(rodden_disasters.json, rodden_nations.json), and those of no kind Research has to its Events database (rodden_events.json).
Only Research changes: the Rodden library stays as it is.

Rodden event charts: 2,143 (earthquake 548, UFO sighting 481, air crash 208, TV show 93, entertainment 84, terror attack 75, space flight 63, historic 56, celestial 50, sports event 42, volcano 40, business 39, phenomenon 33, nation 32, accident 31, organization 28, explosion 22, other 18, fire 18, rail accident 17, shooting 17, political 16, tsunami 16, military 15, city 12, shipwreck 10, aviation 9, nuclear test 8, flood 8, law 7, science 6, meteor 6, tornado 6, landslide 5, assassination 5, cyclone 4, crime 4, wildfire 3, inauguration 3, avalanche 2, storm 1, death 1, oath 1).

| Outcome | Charts |
|---|---:|
| agree | 340 |
| place differs | 11 |
| time differs | 65 |
| timed from Rodden | 157 |
| matched in all | 573 |
| added to Research | 1,567 records (1,570 charts) |

| Added to | Records |
|---|---:|
| disasters | 396 |
| nations | 14 |
| events | 1,157 |

## Times that differ (Research keeps its own)

| Rodden chart | Rodden | Research | Record | Minutes | km |
|---|---|---|---|---:|---:|
| Nature:Earthquake Palestine 1202 | 1202-05-20 02:07:16 UTC | 1202-05-20 02:40 UTC | ea440 1202 Syria earthquake | -33 | 31 |
| Nature:Earthquake Cyprus 1222 | 1222-05-11 04:05:20 UTC | 1222-05-11 06:15 UTC | ea5936 Cyprus | -130 | 2 |
| Nature: Basel Earthquake | 1356-10-18 21:00:00 UTC | 1356-10-18 21:30 UTC | ea551 Basel | -30 | 17 |
| Nature:Earthquake series Aigle:Switzerland 1584 | 1584-03-11 11:30:00 UTC | 1584-03-11 10:30 UTC | ts5680 Switzerland | 60 | 2 |
| Nature:Earthquake Peru 1600 | 1600-02-19 16:46:12 UTC | 1600-02-19 10:00 UTC | ea814 Volcan Huaynaputina | 406 | 82 |
| Nature:Earthquake Philippines 1619 | 1619-12-01 05:53:24 UTC | 1619-11-30 04:00 UTC | ea889 N Luzon: Ilocos Prov,Zagaian Prov | 1553 | 19 |
| Nature:Earthquake Philippines 1645 | 1645-11-30 12:30:00 UTC | 1645-11-30 12:00 UTC | ea961 Luzon: S Batangas To N Cagayan | 30 | 138 |
| Nature:Earthquake Italy 1688 | 1688-06-05 15:30:00 UTC | 1688-06-05 13:15 UTC | ea1112 Benevento | 135 | 4 |
| Nature:Earthquake Irpinia-Basilicata | 1694-09-08 11:40:00 UTC | 1694-09-08 10:45 UTC | ea1134 Calitri | 55 | 31 |
| Nature:Earthquake Peru 1725 | 1725-01-07 04:15:00 UTC | 1725-01-07 04:25 UTC | ea1230 Trujillo, Ancash, Lima | -10 | 98 |
| Nature:Earthquake Italy 1743 | 1743-02-20 15:50:00 UTC | 1743-02-20 16:30 UTC | ea7777 Salento | -40 | 59 |
| Nature:Earthquake Peru 1746 | 1746-10-29 03:38:36 UTC | 1746-10-29 03:30 UTC | ea1295 1746 Lima–Callao earthquake | 9 | 9 |
| Nature:Earthquake Chile 1751 | 1751-05-25 05:22:12 UTC | 1751-05-25 05:30 UTC | ts440 Central Chile | -8 | 19 |
| Nature: Lisbon Earthquake 1755 | 1755-11-01 10:16:32 UTC | 1755-11-01 09:30 UTC | ea1339 1755 Lisbon earthquake | 47 | 205 |
| Nature:Earthquake Altdorf:Switzerland 1774 | 1774-09-10 15:30:00 UTC | 1774-09-10 15:25 UTC | ea1420 Switzerland | 5 | 4 |
| Nature:Earthquake Mexico 1787 | 1787-03-28 17:43:52 UTC | 1787-03-28 17:30 UTC | ea6033 1787 New Spain earthquake | 14 | 199 |
| Nature:Earthquake Japan 1804 | 1804-07-10 12:40:24 UTC | 1804-07-10 13:00 UTC | ea1566 Kisakata | -20 | 19 |
| Nature:Earthquake California 1812 (a) Wrightwood | 1812-12-08 14:50:32 UTC | 1812-12-08 15:00 UTC | ea1609 San Juan Capistrano | -9 | 2 |
| Nature:Earthquake California 1812 (b) Santa Barbar | 1812-12-21 18:28:48 UTC | 1812-12-21 19:00 UTC | ea1610 1812 Ventura earthquake | -31 | 30 |
| Nature:Earthquake India 1819 | 1819-06-16 14:04:56 UTC | 1819-06-16 23:30 UTC | ea1642 1819 Rann of Kutch earthquake | -565 | 102 |
| Nation: Brazil (Empire, Independence) | 1822-09-07 19:14:33 UTC | 1822-09-07 16:30 UTC-3.109 | na-br-independence-cry-of-ipiranga Independence (Cry of Ipiranga) | -22 | 0 |
| Nature:Earthquake:Valparaiso 1822 | 1822-11-20 03:16:32 UTC | 1822-11-20 02:30 UTC | ea1669 Valparaiso, Quillota, Concon, Aconcagua | 47 | 34 |
| Nature:Earthquake:Spain 1829 | 1829-03-21 18:17:44 UTC | 1829-03-21 18:30 UTC | ea1727 Torrevieja, Murcia | -12 | 31 |
| Nature:Earthquake Italy 1832 | 1832-03-08 18:30:00 UTC | 1832-03-08 18:15:00 UTC | ea1753 Cutro | 15 | 4 |
| Nature:Earthquake Israel 1837 | 1837-01-01 14:08:25 UTC | 1837-01-01 01:00 UTC | ea1794 Zefat (Safed); Lebanon: Beirut (Beyrout) | 788 | 33 |
| Nature:Earthquake Chile 1837 | 1837-11-07 12:30:00 UTC | 1837-11-07 12:51 UTC | ea1800 1837 Valdivia earthquake | -21 | 307 |
| Nature:Earthquake Martinique 1839 | 1839-01-11 09:59:20 UTC | 1839-01-11 09:55:00 UTC | ea1811 Fort-De-France, St Pierre; Castries | 4 | 62 |
| Nature:Earthquake Turkey 1840 | 1840-07-02 15:46:56 UTC | 1840-07-02 16:00 UTC | ea1823 Mt Ararat, Aguri, Aralikh; Iran: Maku | -13 | 47 |
| Nature:Earthquake Haiti 1842 | 1842-05-07 22:02:48 UTC | 1842-05-07 21:00 UTC | ea1840 Cap-Haitien | 63 | 0 |
| Nature:Earthquake Italy 1851 | 1851-08-14 13:20:00 UTC | 1851-08-14 01:23 UTC | ea1918 Melfi, Rapolla, Barile, Rionero, Mt Vulture | 717 | 4 |
| Nature:Earthquake Japan 1854 (a) | 1854-12-23 00:07:28 UTC | 1854-12-23 00:46 UTC | ea1969 Enshunada Sea | -39 | 145 |
| Nature:Earthquake Japan 1854 (b) | 1854-12-24 06:52:28 UTC | 1854-12-24 08:00:00 UTC | ea1971 Nankaido | -68 | 273 |
| Nature:Earthquake New Zealand 1855 | 1855-01-23 09:30:00 UTC | 1855-01-23 09:00 UTC | ea1973 Wellington,Waiouru,Wanganui,Otaki | 30 | 19 |
| Nature:Earthquake Turkey 1855 (b) | 1855-04-11 19:40:00 UTC | 1855-04-11 17:40 UTC | ea1981 Bursa | 120 | 3 |
| Nature: Wallis Earthquake:Switzerland 1855 | 1855-07-25 12:20:14 UTC | 1855-07-25 12:00 UTC | ea1986 Haut-Valais | 20 | 1 |
| Nature:Fort Tejon Earthquake 1857 | 1857-01-09 16:24:00 UTC | 1857-01-09 10:13:00 UTC | ea2007 San Luis Obispo | 371 | 9 |
| Nature:Arica Earthquake and Tsunami:Chile 1868 | 1868-08-13 21:26:20 UTC | 1868-08-13 21:30 UTC | ea2139 1868 Arica earthquake | -4 | 71 |
| Nature:Earthquake California 1868 (Hayward) | 1868-10-21 16:01:20 UTC | 1868-10-21 15:53:00 UTC | ea2148 Hayward,San Francisco | 8 | 4 |
| Nature:Earthquake Japan 1872 | 1872-03-14 08:31:40 UTC | 1872-03-14 08:20 UTC | ea2193 Honshu: Sw | 12 | 8 |
| Nature:Earthquake Turkey 1872 | 1872-04-03 05:15:32 UTC | 1872-04-03 05:45 UTC | ea2198 Antakya (Antioch), Suedije | -29 | 8 |
| Nature:Cucuta Earthquake:Colombia/Venezuela | 1875-05-18 16:15:00 UTC | 1875-05-18 16:25 UTC | ea2233 Cucuta,San Cayetano,Villa Del Rosario | -10 | 2 |
| Nature:Earthquake and tsunami Iquique | 1877-05-10 01:56:40 UTC | 1877-05-10 00:59 UTC | ea2248 1877 Iquique earthquake | 58 | 147 |
| Nature:Earthquake Iran 1879 | 1879-03-22 00:28:48 UTC | 1879-03-22 00:00 UTC | ea2269 Bozqush, Ardabil, Gamrud, Tark, Manan | 29 | 61 |
| Nature:Earthquake Turkey 1883 | 1883-10-15 15:30:00 UTC | 1883-10-15 13:30 UTC | ea2331 Ayvalik, Izmir, Cesme | 120 | 119 |
| Nature:Earthquake Italy 1887 | 1887-02-23 05:35:00 UTC | 1887-02-23 05:21 UTC | ea2366 Ligurian Coast | 14 | 4 |
| Nature:Earthquake Turkey 1903 | 1903-04-28 23:39:00 UTC | 1903-04-28 23:46 UTC | ea2649 1903 Manzikert earthquake | -7 | 6 |
| Nature: Aegean Sea Earthquake 1905 | 1905-11-08 21:41:00 UTC | 1905-11-08 22:06:11 UTC | ea2739 Aegean Sea | -25 | 73 |
| Nature:Earthquake Iran 1909 | 1909-01-23 03:00:00 UTC | 1909-01-23 02:48:29 UTC | ea2850 1909 Borujerd earthquake | 12 | 215 |
| Nature:Earthquake Costa Rica 1910 | 1910-05-05 00:26:20 UTC | 1910-05-04 23:50:00 UTC | ea2904 1910 Costa Rica earthquakes | 36 | 17 |
| Nature:Earthquake Series:Guatemala 1917 | 1917-12-26 05:21:00 UTC | 1917-12-26 04:30 UTC | ea3101 Guatemala City | 51 | 10 |
| Nature:Earthquake Mexico 1920 | 1920-01-04 04:15:43 UTC | 1920-01-03 21:48:03 UTC | ea3148 1920 Xalapa earthquake | 388 | 31 |
| Nature:Earthquake Turkey 1942 | 1942-12-20 13:03:00 UTC | 1942-12-20 14:03:09 UTC | ea3725 Niksar, Erbaa | -60 | 39 |
| Nature:Earthquake Turkey 1943 | 1943-11-26 21:20:48 UTC | 1943-11-26 22:20:48 UTC | ea3764 1943 Tosya–Ladik earthquake | -60 | 191 |
| Nature:Earthquake Turkey 1944 | 1944-02-01 02:22:00 UTC | 1944-02-01 03:22:40 UTC | ea3774 Turkey | -61 | 69 |
| Nation: Sri Lanka (Independence) | 1948-02-04 00:30:00 UTC | 1948-02-04 00:00 UTC+5.5 | na-lk-independence-ceylon Independence (Ceylon) | 360 | 0 |
| Nature:Earthquake China 1951 (Taiwan) (a) | 1951-10-21 21:34:00 UTC | 1951-10-22 05:43:01 UTC | ea3982 Taiwan | -489 | 23 |
| Nature:Earthquake Turkey 1970 | 1970-03-28 19:02:24 UTC | 1970-03-28 21:02:26 UTC | ea4523 Gediz | -120 | 15 |
| Nature:Earthquakes Mexico: 1982 | 1982-06-07 06:52:34 UTC | 1982-06-07 10:59:40 UTC | ea4943 Guererro, Orziba, Oaxaca, Guadalupe | -247 | 245 |
| Nation: East Timor | 2002-05-19 15:30:00 UTC | 2002-05-20 00:00 UTC+9 | na-tl-independence Independence | 30 | 1 |
| Nature: Zarand Earthquake:Iran 2005 | 2005-02-22 02:55:00 UTC | 2005-02-22 02:25:22 UTC | ea5848 Kerman Province: Zarand | 30 | 58 |
| Nature: Earthquake Samoa | 2009-09-28 17:48:00 UTC | 2009-09-29 17:48:10 UTC | ea8408 2009 Samoa earthquake and tsunami | -1440 | 189 |
| Nation: Republic of South Sudan | 2011-07-09 10:35:00 UTC | 2011-07-09 00:00 UTC+3 | na-ss-independence Independence | 815 | 4 |
| Nature: 2017 Central Italy earthquakes | 2017-01-18 10:25:25 UTC | 2017-01-18 10:14:11 UTC | ea10234 Farindola | 11 | 10 |
| Nature: 2018 Sunda Strait tsunami | 2018-12-22 14:30:00 UTC | 2018-12-22 13:55 UTC | ts5699 2018 Sunda Strait tsunami | 35 | 0 |
| Nature: Aegean Sea earthquake 2020 | 2020-10-30 09:51:00 UTC | 2020-10-30 11:51:27 UTC | ea10521 2020 Aegean Sea earthquake | -120 | 77 |

## Places more than 300 km apart (same moment)

| Rodden chart | Rodden | Research | Record | Minutes | km |
|---|---|---|---|---:|---:|
| Nature:Earthquake Alaska 1906 | 1906-08-17 00:10:00 UTC | 1906-08-17 00:11:10 UTC | ea2777 Aleutian Islands: Rat Islands | -1 | 359 |
| Nature:Earthquake Mexico 1911 | 1911-06-07 11:02:00 UTC | 1911-06-07 11:02:49 UTC | ea2932 Colima, Jalisco, Mexico City | -1 | 427 |
| Nature:Earthquake:Alaska 1965 | 1965-02-04 05:01:22 UTC | 1965-02-04 05:01:22 UTC | ea4337 1965 Rat Islands earthquake | 0 | 328 |
| Nature:Earthquake and Tsunami:Alaska 1965 | 1965-02-04 05:01:22 UTC | 1965-02-04 05:01:22 UTC | ea4337 1965 Rat Islands earthquake | 0 | 328 |
| Nature:Kilauea volcano (1975) | 1975-11-29 14:48:00 UTC | 1975-11-29 14:47:40 UTC | ea4704 1975 Hawaii earthquake | 0 | 550 |
| Nature:Caldiran-Muradiye-Earthquake, 1976 | 1976-11-24 12:22:16 UTC | 1976-11-24 12:22:17 UTC | ea4752 Muradiye | 0 | 1443 |
| Nature:Earthquake Mexico: 1978 | 1978-11-29 19:52:49 UTC | 1978-11-29 19:52:47 UTC | ea4819 Oaxaca | 0 | 464 |
| Nature:Earthquake Mexico City | 1985-09-19 13:17:00 UTC | 1985-09-19 13:17:47 UTC | ea5076 1985 Mexico City earthquake | -1 | 381 |
| Nature:Panay Earthquake:Philippines 1990 | 1990-06-14 07:41:00 UTC | 1990-06-14 07:40:56 UTC | ea5245 Culasi, Panay | 0 | 432 |
| Nature: Bam Earthquake 2003 | 2003-12-26 01:56:00 UTC | 2003-12-26 01:56:52 UTC | ea5751 Southeastern: Bam, Baravat | -1 | 887 |
| Nature: 2018 Hawaii earthquake | 2018-05-04 22:33:00 UTC | 2018-05-04 22:32:54 UTC | ea10332 Puna District | 0 | 561 |

## Research records timed from Rodden

| Rodden chart | Rodden | Research | Record | Minutes | km |
|---|---|---|---|---:|---:|
| Nature:Earthquake Armenia 893 | 0893-12-27 20:34:28 UTC | 0893-12-28 (no time) | ea268 Dvin; Iran: Ardabil |  | 74 |
| Nature:Earthquake Italy 1279 | 1279-04-30 18:00:00 UTC | 1279-04-30 (no time) | ea477 Forli, Spoleto, Romagna, Marche, Bologna |  | 139 |
| Nature:Earthquake Italy 1328 | 1328-11-30 16:52:40 UTC | 1328-12-01 (no time) | ea520 Norcia |  | 7 |
| Nature:Earthquake Iran 1336 | 1336-10-21 01:30:00 UTC | 1336-10-21 01:30 UTC | ea524 Khaf | 0 | 77 |
| Nature:Earthquake Italy 1349 | 1349-09-09 08:15:00 UTC | 1349-09-09 (no time) | ea540 L'Aquila, Abruzzi, Sannio |  | 90 |
| Nature:Earthquake Italy 1361 | 1361-07-17 17:39:44 UTC | 1361-07-17 (no time) | ea555 Basilicata To Pouilles |  | 100 |
| Nature:Earthquake Italy 1456 | 1456-12-05 04:31:16 UTC | 1456-12-05 04:30 UTC | ea611 Avellino,Napoli,Abruzzi, Brindisi,Benevento | 1 | 99 |
| Nature:Earthquake Chile 1575 | 1575-12-16 18:30:00 UTC | 1575-12-16 18:30 UTC | ea767 1575 Valdivia earthquake | 0 | 3 |
| Nature:Earthquake Japan 1586 | 1586-01-17 15:53:00 UTC | 1586-01-18 (no time) | ea5957 1586 Tenshō earthquake |  | 47 |
| Nature:Earthquake Peru 1586 | 1586-07-10 00:30:00 UTC | 1586-07-10 00:30 UTC | ea786 Lima | 0 | 76 |
| Nature:Vienna Neulengbach Earthquake | 1590-09-15 22:46:20 UTC | 1590-09-15 (no time) | ea801 Kamp River |  | 33 |
| Nature:Earthquake Unterwalden:Switzerland 1601 | 1601-09-18 01:00:00 UTC | 1601-09-18 (no time) | ea819 Switzerland |  | 20 |
| Nature:Earthquake S-Peru/Chile: 1604 | 1604-11-24 18:30:00 UTC | 1604-11-24 18:30 UTC | ea826 1604 Arica earthquake | 0 | 177 |
| Nature:Earthquake Japan 1605 | 1605-02-03 10:52:28 UTC | 1605-02-03 (no time) | ea834 Enshunada |  | 223 |
| Nature:Earthquake China 1605 | 1605-07-13 14:38:35 UTC | 1605-07-13 (no time) | ea835 Guangdong Province |  | 19 |
| Nature:Earthquake:Peru 1619 | 1619-02-14 16:30:00 UTC | 1619-02-14 16:30 UTC | ea885 Trujillo, Piura, Santa | 0 | 20 |
| Nature:Gargano Earthquake:Italy 1627 | 1627-07-30 10:50:00 UTC | 1627-07-30 10:50 UTC | ea910 Lesina | 0 | 15 |
| Nature:Earthquake Indonesia 1629 | 1629-08-01 01:30:00 UTC | 1629-08-01 (no time) | ea5965 Banda Sea |  | 7 |
| Nature:Earthquake Iran 1641 | 1641-02-05 14:54:48 UTC | 1641-02-05 (no time) | ea950 Tabriz, Kurdistan |  | 20 |
| Nature:Earthquake Chile 1647 | 1647-05-14 02:30:00 UTC | 1647-05-14 02:30 UTC | ea970 Santiago | 0 | 8 |
| Nature:Earthquake China 1652 | 1652-07-13 03:17:56 UTC | 1652-07-13 (no time) | ea984 Yunnan Province: Midu |  | 4 |
| Nature:Earthquake Peru 1655 | 1655-11-13 19:45:00 UTC | 1655-11-13 19:45 UTC | ea998 Lima, Callao | 0 | 66 |
| Nature:Earthquake Chile 1657 | 1657-03-15 23:30:00 UTC | 1657-03-15 23:30 UTC | ea1003 Concepcion, Chillan | 0 | 2 |
| Nature:Earthquake Italy 1661 | 1661-03-22 13:30:00 UTC | 1661-03-22 13:30 UTC | ea1019 Firenze (Florence), Predappio | 0 | 12 |
| Nature:Earthquake Peru 1664 | 1664-05-12 09:15:00 UTC | 1664-05-12 09:15 UTC | ea1028 Ica, Pisco | 0 | 11 |
| Nature:Earthquake Croatia 1667 (Ragusa) | 1667-04-06 07:10:00 UTC | 1667-04-06 07:10 UTC | ea1042 Croatia: Dubrovnik: Ragusa | 0 | 4 |
| Nature:Earthquake China 1668 | 1668-07-25 11:58:11 UTC | 1668-07-25 (no time) | ea1054 1668 Shandong earthquake |  | 189 |
| Nature:Earthquake Japan 1677 | 1677-11-04 10:38:35 UTC | 1677-11-04 (no time) | ea1076 1677 Bōsō earthquake |  | 116 |
| Nature:Earthquake:Peru 1687 | 1687-10-20 10:30:00 UTC | 1687-10-20 10:30 UTC | ea1101 1687 Peru earthquake | 0 | 172 |
| Nature:Earthquake:Villach 1690 | 1690-12-04 14:34:40 UTC | 1690-12-04 (no time) | ea1121 Carinthie |  | 3 |
| Nature:Earthquake Jamaica 1692 | 1692-06-07 16:47:24 UTC | 1692-06-07 (no time) | ea1126 1692 Jamaica earthquake |  | 22 |
| Nature: Earthquake and Tsunami, Sicily 1693 | 1693-01-11 13:30:00 UTC | 1693-01-11 13:30 UTC | ea10630 1693 Sicily earthquake | 0 | 182 |
| Nature:Earthquake Italy 1703 | 1703-01-14 18:00:00 UTC | 1703-01-14 (no time) | ea1157 Central Apennino, Norcia, L'Aquila, Perugia |  | 3 |
| Nature:Earthquake:Japan 1703 | 1703-12-30 17:00:00 UTC | 1703-12-30 17:00 UTC | ea1163 1703 Genroku earthquake | 0 | 81 |
| Nature:Earthquake China 1718 | 1718-06-18 20:58:12 UTC | 1718-06-19 (no time) | ea1210 1718 Tongwei–Gansu earthquake |  | 26 |
| Nature:Earthquake Iran 1721 | 1721-04-26 03:00:00 UTC | 1721-04-26 03:00 UTC | ea1222 Tabriz | 0 | 41 |
| Nature:Irpinia Earthquake 1732 | 1732-11-29 07:40:00 UTC | 1732-11-29 (no time) | ea1259 Ariano, Lucanie, Avellino |  | 77 |
| Nature:Earthquake Russia 1737 | 1737-10-16 16:00:00 UTC | 1737-10-16 16:00 UTC | ea6001 1737 Kamchatka earthquake | 0 | 218 |
| Nature:Earthquake China 1751 | 1751-05-25 07:20:28 UTC | 1751-05-25 (no time) | ea1317 Yunnan Province |  | 8 |
| Nature: Earthquake Brig/Visp:Switzerland 1755 | 1755-12-09 13:30:00 UTC | 1755-12-09 13:30 UTC | ea1343 Switzerland | 0 | 2 |
| Nature:Earthquake Azores 1757 | 1757-07-09 23:45:00 UTC | 1757-07-09 23:45 UTC | ea1348 Sao Jorge | 0 | 75 |
| Nature:Earthquake Syria 1759 | 1759-11-25 16:58:12 UTC | 1759-11-25 (no time) | ea1362 Baalbec; Syria: Damascus, Antioch |  | 91 |
| Nature:Earthquake China 1765 | 1765-09-02 01:00:27 UTC | 1765-09-02 (no time) | ea1375 Gansu Province: Wushan, Gangu |  | 14 |
| Nature:Earthquake Japan 1766 | 1766-03-08 08:37:00 UTC | 1766-03-08 (no time) | ea1378 Hirosaki |  | 10 |
| Nature:Earthquake Japan 1771 | 1771-04-23 23:43:22 UTC | 1771-04-24 (no time) | ea1405 1771 Great Yaeyama Tsunami |  | 41 |
| Nature:Earthquakes:Calabria 1783 | 1783-02-05 12:00:00 UTC | 1783-02-05 12:00 UTC | ea1455 Tyrrhenian Calabria | 0 | 5 |
| Nature:Earthquake Peru 1784 | 1784-05-13 12:35:00 UTC | 1784-05-13 12:35 UTC | ea1471 Arequipa,Camana,Moquegua,Tambo | 0 | 49 |
| Nature:Earthquake China 1786 (a) | 1786-06-01 05:11:52 UTC | 1786-06-01 (no time) | ea1488 1786 Kangding-Luding earthquake |  | 29 |
| Nature:Earthquake Algeria 1790 | 1790-10-09 01:15:00 UTC | 1790-10-09 01:15 UTC | ea1504 Oran; Spain: Cartagena, Santa Fe | 0 | 11 |
| Nature: Mount Unzen Earthquake and Tsunami | 1792-05-21 10:12:52 UTC | 1792-05-21 (no time) | ts568 Shimabara Bay, Kyushu Island |  | 143 |
| Nature:Earthquake China 1792 (Taiwan) | 1792-08-09 08:58:12 UTC | 1792-08-09 (no time) | ea1516 Jiayi, Tainan |  | 14 |
| Nature:Earthquake Japan 1793 | 1793-02-17 04:35:35 UTC | 1793-02-17 (no time) | ea1521 Sanriku,Rikuzen,Rikuchu |  | 252 |
| Nature:Riobamba Earthquake:Ecuador 1797 | 1797-02-04 12:30:00 UTC | 1797-02-04 12:30 UTC | ea1537 Riobamba, Quito, Cuzco; Peru; Colombia | 0 | 5 |
| Nature:Earthquake Indonesia 1797 (Sumatra) | 1797-02-10 08:18:36 UTC | 1797-02-10 (no time) | ea5933 1797 Sumatra earthquake |  | 184 |
| Nature:Earthquake Venezuela 1797 | 1797-12-14 23:00:00 UTC | 1797-12-14 (no time) | ea1541 Cumana, Cariaco |  | 17 |
| Nature:Earthquake Italy 1805 | 1805-07-26 21:00:00 UTC | 1805-07-26 20:57 UTC | ts3217 Campania | 3 | 22 |
| Nature:Earthquake Greece 1810 (Crete) | 1810-02-16 21:15:00 UTC | 1810-02-16 (no time) | ea1585 Crete: Iraklion (Candia) |  | 23 |
| Nation: Venezuela | 1811-07-05 19:27:44 UTC | 1811-07-05 (no time) | na-ve-declaration-of-independence Declaration of Independence |  | 6 |
| Nature: Earthquake Missouri | 1811-12-16 08:13:08 UTC | 1811-12-16 08:15 UTC | ea1594 Northeast (New Madrid Earthquakes) | -2 | 134 |
| Nature:Eruption:Mayon 1814 | 1814-01-31 23:45:04 UTC | 1814-02-01 (no time) | vo707 Mayon |  | 15 |
| Nature: Tambora volcano (1815) | 1815-04-10 02:05:08 UTC | 1815-04-10 (no time) | vo367 Tambora |  | 82 |
| Nature:Earthquake China 1815 | 1815-10-22 16:33:22 UTC | 1815-10-23 (no time) | ea1619 Shanxi Province |  | 273 |
| Nature:Earthquake China 1816 | 1816-12-07 19:16:48 UTC | 1816-12-08 (no time) | ea8098 Sichuan Province |  | 10 |
| Nature:Earthquake Algeria 1825 | 1825-03-02 07:00:00 UTC | 1825-03-02 07:00 UTC | ea1692 Blida, Algiers | 0 | 8 |
| Nature:Earthquake Japan 1828 | 1828-12-17 21:44:12 UTC | 1828-12-18 (no time) | ea1720 Sandyo In Etigo |  | 50 |
| Nature:Earthquake China 1830 | 1830-06-12 12:22:28 UTC | 1830-06-12 (no time) | ea1740 Hebei Province |  | 17 |
| Nature:Earthquake Nepal 1833 | 1833-08-26 17:16:44 UTC | 1833-08-26 (no time) | ea1758 Kathmandu; India: Bihar; China: Tibet |  | 67 |
| Nature:Earthquake China 1833 (Yunnan) | 1833-09-06 03:09:20 UTC | 1833-09-06 (no time) | ea1759 Yunnan Province |  | 36 |
| Nature:Earthquake Indonesia 1833 (Sumatra) | 1833-11-24 15:30:00 UTC | 1833-11-24 (no time) | ea1763 1833 Sumatra earthquake |  | 173 |
| Nature:Earthquake Guadeloupe 1843 | 1843-02-08 14:50:00 UTC | 1843-02-08 14:50:00 UTC | ea1846 1843 Guadeloupe earthquake | 0 | 67 |
| Nature: 1847 Zenkoji Earthquake, Japan | 1847-05-08 12:21:00 UTC | 1847-05-08 (no time) | ea1887 Zenkoji, Nagano |  | 42 |
| Nation: Switzerland 1848 | 1848-09-12 12:20:16 UTC | 1848-09-12 (no time) | na-ch-federal-state Federal State |  | 1 |
| Nature:Earthquake China 1848 (Taiwan) | 1848-12-02 23:57:52 UTC | 1848-12-03 (no time) | ea1895 Zhanghua |  | 4 |
| Nature:Earthquake China 1850 | 1850-09-12 15:10:55 UTC | 1850-09-12 (no time) | ea1905 Sichuan: Xichang |  | 11 |
| Nature:Earthquake Albania 1851 | 1851-10-12 06:00:00 UTC | 1851-10-12 06:00 UTC | ea1921 Vlore (Valona),Berat; Turkey | 0 | 18 |
| Nature:Earthquake Venezuela 1853 | 1853-07-15 18:16:40 UTC | 1853-07-15 (no time) | ea1948 Cumana |  | 5 |
| Nature:Earthquake Japan 1854 | 1854-07-08 16:55:08 UTC | 1854-07-09 (no time) | ea1960 Iga, Ise, Yamato |  | 28 |
| Nature:Earthquake Turkey 1855 | 1855-02-28 01:00:00 UTC | 1855-02-28 01:00 UTC | ea1977 Tayabas, Bursa | 0 | 3 |
| Nature:Basilicata Earthquake 1857 | 1857-12-16 21:15:00 UTC | 1857-12-16 21:18 UTC | ea2013 Campania, Potenza | -3 | 1 |
| Nature:Earthquake Japan 1858 | 1858-04-08 16:54:40 UTC | 1858-04-09 (no time) | ea2020 Hida: N |  | 110 |
| Nature:Erzurum Earthquake 1859 | 1859-06-02 08:00:00 UTC | 1859-06-02 08:00 UTC | ea2036 Erzurum | 0 | 2 |
| Nature:Earthquake Indonesia 1861 (Sumatra) | 1861-02-16 12:18:20 UTC | 1861-02-16 (no time) | ea2043 1861 Sumatra earthquake |  | 330 |
| Nature:Earthquake Indonesia 1861 (Sumatra) (b) | 1861-03-09 13:18:20 UTC | 1861-03-09 (no time) | ea6142 Sw. Sumatra |  | 274 |
| Nature:Earthquake China 1862 (Taiwan) | 1862-06-07 01:58:12 UTC | 1862-06-06 (no time) | ea2059 Tainan |  | 47 |
| Nature:Earthquake Greece 1863 | 1863-04-22 20:30:00 UTC | 1863-04-22 20:30 UTC | ea2068 Rhodes, Kos | 0 | 21 |
| Nature:Earthquake Philippines 1863 | 1863-06-03 11:20:00 UTC | 1863-06-03 11:20 UTC | ea2073 Manila, Rizal, Bulacan | 0 | 9 |
| Nature:Earthquake Indonesia 1867 (Java) | 1867-06-09 21:15:00 UTC | 1867-06-10 (no time) | ea2117 Java: Jogyakarta, Surakarta |  | 116 |
| Nature:Great Ka'u Earthquake (1868) | 1868-04-03 02:25:00 UTC | 1868-04-03 02:24 UTC | ea2125 1868 Hawaii earthquake | 1 | 22 |
| Nature:Earthquake Ecuador 1868 | 1868-08-16 06:30:00 UTC | 1868-08-16 06:30 UTC | ea2143 Guayaquil,Ibarra; Colombia: San Pablo | 0 | 8 |
| Nature:Earthquake Iran 1871 | 1871-12-23 14:06:00 UTC | 1871-12-23 (no time) | ea2185 Quchan |  | 28 |
| Nature: Lone Pine Earthquake:California 1872 | 1872-03-26 10:30:00 UTC | 1872-03-26 10:30 UTC | ea2195 Owens Valley | 0 | 25 |
| Nature:Earthquake El Salvador 1873 | 1873-03-05 04:26:48 UTC | 1873-03-04 (no time) | ea2206 Santa Tomas, San Vicente |  | 10 |
| Nature:Earthquake Italy 1873 | 1873-06-29 03:58:00 UTC | 1873-06-29 03:58 UTC | ea2209 Bellunese | 0 | 15 |
| Nature:Earthquake China 1879 | 1879-06-30 21:00:19 UTC | 1879-07-01 (no time) | ea2272 Gansu Province |  | 30 |
| Nature:Chios Earthquake 1881 | 1881-04-03 11:30:00 UTC | 1881-04-03 11:30 UTC | ea2298 Khios; Turkey: Cesme | 0 | 25 |
| Nature:Earthquake China 1881 | 1881-07-20 13:59:19 UTC | 1881-07-20 (no time) | ea2304 Gansu Province |  | 84 |
| Nature:Earthquake Italy 1883 | 1883-07-28 20:25:00 UTC | 1883-07-28 20:25 UTC | ea2324 Ischia Is: Casamicciola, Forino, Lacco Ameno | 0 | 6 |
| Nature: Colchester earthquake 1884 | 1884-04-22 09:18:00 UTC | 1884-04-22 09:18 UTC | ea10981 Colchester, England | 0 | 9 |
| Nature:Earthquake Greece 1886 | 1886-08-27 21:32:00 UTC | 1886-08-27 21:32 UTC | ea2357 Triphylie (Peleponese), Philiatra | 0 | 13 |
| Nature:Earthquake South Carolina 1886 | 1886-09-01 02:51:00 UTC | 1886-09-01 02:51:00 UTC | ea2362 Charleston | 0 | 14 |
| Nature:Earthquake China 1887 | 1887-12-16 12:10:00 UTC | 1887-12-16 (no time) | ea2378 Yunnan Province |  | 9 |
| Nature: 1891 Mino-Owari Earthquake | 1891-10-27 21:38:00 UTC | 1891-10-27 21:37 UTC | ea2411 Mino-Owari | 1 | 24 |
| Nature:Mérida Earthquake:Venezuela 1894 | 1894-04-29 02:42:40 UTC | 1894-04-29 02:45:00 UTC | ea2448 Merida,Tovar; Colombia: N Santander | -2 | 63 |
| Nature:Earthquake Japan 1894 | 1894-10-22 08:35:00 UTC | 1894-10-22 08:35 UTC | ea2456 Syonai | 0 | 11 |
| Nature:Earthquake Missouri 1895 | 1895-10-31 11:08:00 UTC | 1895-10-31 11:08 UTC | ea6532 Charleston | 0 | 5 |
| Nature:Earthquake Iran 1896 | 1896-01-04 15:14:48 UTC | 1896-01-05 (no time) | ea2482 Khvoy (Khoy) |  | 289 |
| Nature: Sanriku Earthquake and Tsunami 1896 | 1896-06-15 10:32:00 UTC | 1896-06-15 10:33 UTC | ea2489 1896 Sanriku earthquake | -1 | 239 |
| Nature:Earthquake India 1897 | 1897-06-12 11:06:00 UTC | 1897-06-12 11:06:46 UTC | ea2513 Assam; Bangladesh | -1 | 181 |
| Nature: Earthquake Series Yakutat Bay: Alaska 1899 | 1899-09-10 21:41:00 UTC | 1899-09-10 21:41 UTC | ea2557 Se Alaska | 0 | 52 |
| Nature:Earthquake Indonesia 1899 (Moluccas) | 1899-09-29 17:03:00 UTC | 1899-09-29 17:03 UTC | ea6229 Banda Sea | 0 | 59 |
| Nature: Volcano Mount Pelée (1902) | 1902-05-08 11:56:20 UTC | 1902-05-08 (no time) | vo4193 Pelee |  | 7 |
| Nature:Earthquake China 1902 | 1902-08-22 03:00:00 UTC | 1902-08-22 03:00 UTC | ea2631 1902 Turkestan earthquake | 0 | 40 |
| Nature: Santa Maria Volcano (1902) | 1902-10-24 23:02:04 UTC | 1902-10-25 (no time) | vo3521 1902 eruption of Santa María |  | 112 |
| Nature:Earthquake Uzbekistan 1902 | 1902-12-16 05:07:00 UTC | 1902-12-16 05:07 UTC | ea2640 Andizhan | 0 | 8 |
| Nature: Rockslide:Frank Slide | 1903-04-29 11:47:28 UTC | 1903-04-29 (no time) | di-landslide-frank-slide Frank Slide |  | 2 |
| Nature:Earthquake China 1904 | 1904-08-30 12:57:28 UTC | 1904-08-30 (no time) | ea2694 Sichuan Province |  | 24 |
| Nature:Eruption Mount Vesuvius 1906 | 1906-04-04 04:30:00 UTC | 1906-04-04 (no time) | vo1344 Vesuvius |  | 1 |
| Nature: Valparaiso Earthquake:Chile 1906 | 1906-08-17 00:38:46 UTC | 1906-08-17 00:40 UTC | ea2779 South Central | -1 | 34 |
| Nature:Earthquake China 1906 | 1906-12-22 18:21:00 UTC | 1906-12-22 18:21 UTC | ea2794 Xinjiang Province | 0 | 132 |
| Nature:Earthquake Peru 1908 | 1908-12-12 12:08:00 UTC | 1908-12-12 12:08 UTC | ea2844 Off Coast | 0 | 240 |
| Nature:Earthquake Burma (Myanmar) 1908 | 1908-12-12 12:55:00 UTC | 1908-12-12 (no time) | ea2842 Kachin |  | 27 |
| Nature: Provence Earthquakes | 1909-06-11 21:05:39 UTC | 1909-06-11 21:06 UTC | ea2867 Vernegues,Charleval,La Roque D'Antheron | 0 | 12 |
| Accident: Halifax explosion | 1917-12-06 13:04:35 UTC | 1917-12-06 13:04 UTC | ts2792 Halifax, Nova Scotia | 1 | 2 |
| Nation: Turkey (Republic) | 1923-10-29 18:30:00 UTC | 1923-10-29 20:30 UTC+2 | na-tr-republic Republic | 0 | 2 |
| Nature:Earthquake:S-Colombia 1923 | 1923-12-14 10:31:00 UTC | 1923-12-14 10:31 UTC | ea3239 Ipiales | 0 | 19 |
| Nature:Earthquake:Japan 1927 | 1927-03-07 09:27:00 UTC | 1927-03-07 09:27 UTC | ea3306 Honshu: Sw | 0 | 4 |
| Nature:Earthquake Israel 1927 | 1927-07-11 13:04:00 UTC | 1927-07-11 13:04 UTC | ea3325 Damiya | 0 | 12 |
| Nature:Irpinia Earthquake 1930 | 1930-07-23 00:09:00 UTC | 1930-07-23 00:09 UTC | ea3420 Irpinia | 0 | 56 |
| Nature:Eruption:Paricutin (1943) | 1943-02-20 22:00:00 UTC | 1943-02-20 (no time) | vo4493 Michoacan-Guanajuato |  | 58 |
| Nature:Earthquake Japan 1943 | 1943-09-10 08:37:00 UTC | 1943-09-10 08:37 UTC | ea3755 Honshu: S | 0 | 38 |
| Nature:Earthquake Japan 1944 | 1944-12-07 04:36:00 UTC | 1944-12-07 04:35 UTC | ea3791 1944 Tōnankai earthquake | 1 | 107 |
| Nature:Earthquake Japan 1945 | 1945-01-12 18:38:00 UTC | 1945-01-12 18:38 UTC | ea3797 Honshu: S | 0 | 209 |
| Nation: Israel | 1948-05-14 14:00:00 UTC | 1948-05-14 16:00 UTC+2 | na-il-declaration-of-independence Declaration of Independence | 0 | 2 |
| Nation: India (Republic) | 1950-01-26 04:48:00 UTC | 1950-01-26 10:18 UTC+5.5 | na-in-republic Republic | 0 | 5 |
| Nation: Egypt (Republic) | 1953-06-18 23:30:00 UTC | 1953-06-18 (no time) | na-eg-republic Republic |  | 1 |
| Nature:Earthquake Afghanistan 1956 | 1956-06-09 23:13:55 UTC | 1956-06-09 (no time) | ea4099 Kabul |  | 42 |
| Disaster: Malpasset Dam failure | 1959-12-02 20:13:00 UTC | 1959-12-02 (no time) | di-flood-malpasset-dam Malpasset Dam |  | 9 |
| Nature: Dam broke Vajont (1963) | 1963-10-09 21:39:00 UTC | 1963-10-09 21:39 UTC | ts5569 Vajont Dam, Vajont River | 0 | 2 |
| Nation: Sri Lanka (Republic) | 1972-05-22 07:13:00 UTC | 1972-05-22 12:43 UTC+5.5 | na-lk-republic Republic | 0 | 0 |
| Nature:Etna Eruption 1979 | 1979-09-12 15:47:00 UTC | 1979-09-12 (no time) | vo30 Etna |  | 2 |
| Nature:El Chichon eruption 1982 | 1982-03-29 05:32:00 UTC | 1982-03-29 (no time) | vo3518 Chichon, El |  | 19 |
| Nature:Eruption:Nevado del Ruiz | 1985-11-14 03:30:00 UTC | 1985-11-13 (no time) | vo3835 Ruiz, Nevado del |  | 48 |
| Nature:Eruption:Mihara 1986 | 1986-11-15 08:25:00 UTC | 1986-11-15 (no time) | vo1332 Izu-Oshima |  | 427 |
| Nation: Ukraine | 1991-08-24 15:00:00 UTC | 1991-08-24 18:00 UTC+3 | na-ua-independence Independence | 0 | 2 |
| Nature: Fire Oakland | 1991-10-20 17:53:00 UTC | 1991-10-19 (no time) | di-wildfire-oakland-hills-firestorm Oakland Hills firestorm |  | 8 |
| Nature:Eruption:Mayon 1993 | 1993-02-02 05:11:00 UTC | 1993-02-02 (no time) | vo4462 Mayon |  | 15 |
| Nature: Merapi eruption 1994 | 1994-11-22 03:15:00 UTC | 1994-11-22 (no time) | vo112 Merapi |  | 77 |
| Nature: Volcano Iceland (1996) | 1996-09-30 22:30:00 UTC | 1996-09-30 (no time) | vo4291 Grimsvotn |  | 1 |
| Nature: Volcano Congo | 2002-01-17 04:50:00 UTC | 2002-01-17 (no time) | vo4964 Nyiragongo |  | 18 |
| Nature:Etna Eruption 2002 | 2002-10-28 12:12:00 UTC | 2002-10-28 (no time) | vo5487 Etna |  | 2 |
| Nature: 2014 mudslide Seattle | 2014-03-22 17:38:00 UTC | 2014-03-22 (no time) | di-landslide-2014-oso-mudslide 2014 Oso mudslide |  | 84 |
| Nature: Volcano Mount Ontake Nagano Japan | 2014-09-27 02:53:00 UTC | 2014-09-27 (no time) | vo6064 2014 Mount Ontake eruption |  | 105 |
| Nature: 2016 Alberta wildfire | 2016-05-02 03:57:00 UTC | 2016-05-01 (no time) | di-wildfire-2016-fort-mcmurray-wildfire 2016 Fort McMurray Wildfire |  | 8 |
| Nature: 2017 Sichuan Landslide | 2017-06-23 21:38:00 UTC | 2017-06-24 (no time) | di-landslide-2017-sichuan-landslide 2017 Sichuan landslide |  | 206 |
| Nature: 2018 Volcán de Fuego eruption | 2018-06-03 18:00:00 UTC | 2018-06-03 (no time) | vo7164 2018 Volcán de Fuego eruption |  | 22 |
| Nature: 2018 Woolsey Fire, California | 2018-11-08 22:24:00 UTC | 2018-11-08 (no time) | di-wildfire-woolsey-fire Woolsey Fire |  | 4 |
| Nature: 2019 Whakaari/ White Island eruption | 2019-12-09 01:11:00 UTC | 2019-12-09 (no time) | vo7464 2019 Whakaari / White Island eruption |  | 0 |

## Rodden events added to Research

| Id | Type | Date | Time | Charts |
|---|---|---|---|---|
| ro-celestial-ten-planets-in-air-element | celestial | -0176-06-15 | 04:35:00 UTC+0 | Celestial: Ten planets in Air element |
| ro-celestial-ten-planets-in-water-element-872-bce | celestial | -0871-03-03 | 23:15:00 UTC+0 | Celestial: Ten planets in Water element 872 BCE |
| ro-celestial-seven-planets-and-node-in-capricorn | celestial | -1098-01-13 | 06:50:00 UTC+0 | Celestial: Seven planets and Node in Capricorn |
| ro-celestial-seven-planets-and-node-in-libra | celestial | -1197-10-19 | 21:59:30 UTC+0 | Celestial: Seven planets and Node in Libra |
| ro-celestial-ten-planets-in-water-element-1264-bce | celestial | -1263-07-04 | 23:53:00 UTC+0 | Celestial: Ten planets in Water element 1264 BCE |
| ro-celestial-ten-planets-in-fire-element-2065-bce | celestial | -2064-08-17 | 16:37:00 UTC+0 | Celestial: Ten planets in Fire element 2065 BCE |
| ro-celestial-ten-planets-in-earth-element | celestial | -2699-09-25 | 19:18:00 UTC+0 | Celestial: Ten planets in Earth element |
| ro-celestial-seven-planets-and-node-in-scorpio | celestial | -4018-12-06 | 09:44:00 UTC+0 | Celestial: Seven planets and Node in Scorpio |
| ro-celestial-jupiter-saturn-uranus-neptune-cross | celestial | 0025-05-18 | 19:05:00 UTC+0 | Celestial: Jupiter-Saturn-Uranus-Neptune Cross |
| ro-celestial-ten-planets-in-water-element-219-ce | celestial | 0219-07-08 | 20:06:00 UTC+0 | Celestial: Ten planets in Water element 219 CE |
| ro-celestial-seven-planets-and-node-in-gemini | celestial | 0531-05-31 | 08:10:00 UTC+0 | Celestial: Seven planets and Node in Gemini |
| ro-celestial-ten-planets-in-fire-element-615-ce | celestial | 0615-12-14 | 06:23:00 UTC+0 | Celestial: Ten planets in Fire element 615 CE |
| ro-nature-eruption-sunset-crater-1064 | volcano | 1063-10-25 | 14:00:00 UTC+0 | Nature:Eruption:Sunset Crater 1064 |
| ro-nature-earthquake-japan-1099 | earthquake | 1099-02-16 | 06:00:00 UTC+9.02333 | Nature:Earthquake Japan 1099 |
| ro-cities-house-of-zahringen-foundations | city | 1120-01-07 | 05:23:00 UTC+0 | Cities: House of Zähringen:Foundations |
| ro-nation-portugal-battle-of-sao-mamede | founding | 1128-06-24 | 12:30:00 UTC-0.553333 | Nation: Portugal (Battle of Sao Mamede) |
| ro-cities-berne-conj-jup-sat | city | 1186-11-08 | 08:31:16 UTC+0 | Cities: Berne:Conj. Jup-Sat |
| ro-ufo-sighting-1771 | UFO sighting | 1254-01-01 | 19:00:00 UTC-0.022815 | UFO Sighting 1771 |
| ro-nature-earthquake-japan-1293 | earthquake | 1293-05-20 | 05:00:00 UTC+9.30335 | Nature:Earthquake Japan 1293 |
| ro-nature-earthquake-japan-1361 | earthquake | 1361-07-26 | 04:00:00 UTC+8.90333 | Nature:Earthquake Japan 1361 |
| ro-nature-earthquake-turkey-1457 | earthquake | 1457-04-23 | 16:00:00 UTC+2.63222 | Nature:Earthquake Turkey 1457 |
| ro-nature-earthquake-japan-1498 | earthquake | 1498-09-20 | 08:00:00 UTC+9.18222 | Nature:Earthquake Japan 1498 |
| ro-nation-brazil-discovery | founding | 1500-04-22 | 16:30:00 UTC-2.60432 | Nation: Brazil discovery |
| ro-nature-earthquake-nepal-1505 | earthquake | 1505-06-05 | 05:00:00 UTC+5.57778 | Nature:Earthquake Nepal 1505 |
| ro-ufo-sighting-1561-nurnberg-1813 | UFO sighting | 1561-04-14 | 06:00:00 UTC+0.737778 | UFO Sighting 1561 Nürnberg (1813) |
| ro-historic-egmond-beheaded | historic | 1568-06-05 | 11:00:00 UTC+0.288889 | Historic: Egmond beheaded |
| ro-nature-unterwalden-earthquake-1601 | earthquake | 1601-09-08 | 01:00:00 UTC+0 | Nature:Unterwalden Earthquake 1601 |
| ro-historic-escalade-de-geneve | historic | 1602-12-12 | 02:00:00 UTC+0.41 | Historic: Escalade de Genève |
| ro-historic-sinking-of-vasa | shipwreck | 1628-08-10 | 16:20:00 UTC+1.20333 | Historic: Sinking of Vasa |
| ro-nature-eruption-etna-1669 | volcano | 1669-03-08 | 06:00:00 UTC+1 | Nature:Eruption Etna 1669 |
| ro-phenomena-appearance-of-a-dead-wife | phenomenon | 1681-11-29 | 20:00:00 UTC+0.764444 | Phenomena:Appearance of a dead wife |
| ro-ufo-sighting-1860 | UFO sighting | 1686-07-09 | 01:30:00 UTC+0.822222 | UFO Sighting 1860 |
| ro-nature-earthquake-turkey-1688 | earthquake | 1688-07-10 | 11:45:00 UTC+1.99444 | Nature:Earthquake Turkey 1688 |
| ro-phenomena-the-haunted-house-of-mackie-og-1695 | phenomenon | 1695-02-03 | 11:52:00 UTC+0 | Phenomena:The Haunted House of Mackie (OG 1695) |
| ro-nature-earthquake-duren-1756 | earthquake | 1756-02-18 | 08:00:00 UTC+0.431111 | Nature:Earthquake:Düren 1756 |
| ro-historic-first-voyage-of-james-cook | historic | 1768-08-25 | 14:00:00 UTC-0.277778 | Historic: First Voyage of James Cook |
| ro-historic-second-voyage-of-james-cook | historic | 1772-07-12 | 06:00:00 UTC-0.277778 | Historic: Second Voyage of James Cook |
| ro-creation-conjunctions-saturn-neptune | celestial | 1773-09-27 | 04:35:15 UTC-5.01111 | Creation conjunctions:Saturn-Neptune |
| ro-historic-third-voyage-of-james-cook | historic | 1776-07-11 | 20:00:00 UTC-0.277778 | Historic: Third Voyage of James Cook |
| ro-celestial-uranus-discovery | celestial | 1781-03-13 | 22:30:00 UTC-0.157778 | Celestial: Uranus Discovery |
| ro-first-performance-die-entfuhrung-aus-dem-serail | entertainment | 1782-07-16 | 18:30:00 UTC+1.09154 | First performance:Die Entführung aus dem Serail |
| ro-first-performance-le-nozze-di-figaro | entertainment | 1786-05-01 | 18:30:00 UTC+1.09154 | First performance: Le nozze di Figaro |
| ro-first-performance-don-karlos | entertainment | 1787-08-29 | 17:30:00 UTC+0.665556 | First performance:Don Karlos |
| ro-nation-australia-british-colonisation | founding | 1788-01-26 | 05:10:00 UTC+10.0811 | Nation: Australia (British Colonisation) |
| ro-celestial-jupiter-uranus-conjunction-1789 | celestial | 1789-06-29 | 16:16:00 UTC+0 | Celestial: Jupiter-Uranus Conjunction, 1789 |
| ro-first-performance-cosi-fan-tutte | entertainment | 1790-01-26 | 19:00:00 UTC+1.09154 | First performance:Cosi fan tutte |
| ro-first-performance-die-zauberflote | entertainment | 1791-09-30 | 19:00:00 UTC+1.09154 | First Performance:"Die Zauberflöte" |
| ro-nature-earthquake-and-eruption-mount-vesuvius | earthquake | 1794-06-12 | 23:30:00 UTC+0.962222 | Nature:Earthquake and eruption Mount Vesuvius |
| ro-celestial-ceres-discovery | celestial | 1801-01-01 | 20:43:00 UTC+0.891111 | Celestial: Ceres Discovery |
| ro-celestial-pallas-discovery | celestial | 1802-03-28 | 20:45:00 UTC+0.587778 | Celestial: Pallas Discovery |
| ro-first-performance-wilhelm-tell | entertainment | 1804-03-17 | 15:30:00 UTC+0.754444 | First Performance:Wilhelm Tell |
| ro-nature-rockslide-arth-goldau-1806 | landslide | 1806-09-02 | 17:00:00 UTC+0.567778 | Nature: Rockslide:Arth Goldau 1806 |
| ro-celestial-vesta-discovery | celestial | 1807-03-29 | 20:05:00 UTC+0.587778 | Celestial: Vesta Discovery |
| ro-phenomena-the-uffikon-case-1814-1816 | phenomenon | 1815-01-01 | 06:00:00 UTC+0.534444 | Phenomena:The Uffikon Case (1814-1816) |
| ro-cities-cleveland-oh | city | 1815-06-05 | 00:00:00 UTC-5.44667 | Cities: Cleveland OH |
| ro-phenomena-the-holligen-bells-riddle | phenomenon | 1816-07-31 | 15:00:00 UTC+0.495556 | Phenomena:The Holligen bells riddle |
| ro-nation-greece-1821-independence-conjunctions | independence | 1821-02-18 | 07:30:00 UTC+0 | Nation: Greece 1821:Independence Conjunctions |
| ro-first-performance-faust-i | entertainment | 1829-01-19 | 18:00:00 UTC+0.701111 | First performance:Faust I |
| ro-nature-earthquake-iran-1830 | earthquake | 1830-03-27 | 12:00:00 UTC+3.47111 | Nature:Earthquake Iran 1830 |
| ro-phenomena-spook-and-stall-spook-in-kerner-s-house | phenomenon | 1836-01-28 | 00:30:00 UTC+0.618889 | Phenomena:Spook and Stall Spook in Kerner's House |
| ro-cities-newark-nj | city | 1836-04-11 | 00:00:00 UTC-4.94444 | Cities: Newark NJ |
| ro-nature-earthquake-china-1845-taiwan | earthquake | 1845-03-04 | 12:00:00 UTC+8.03556 | Nature:Earthquake China 1845 (Taiwan) |
| ro-phenomena-angelique-cottin-begin-appearances | phenomenon | 1846-01-15 | 20:00:00 UTC+0.028889 | Phenomena:Angélique Cottin, begin appearances |
| ro-invention-saxophone | other | 1846-03-21 | 12:20:00 UTC+0.155556 | Invention: Saxophone |
| ro-historic-ca-constitution | political | 1849-10-13 | 14:00:00 UTC-8.12556 | Historic: CA Constitution |
| ro-business-swiss-franc-1850 | business | 1850-05-05 | 22:03:00 UTC+0 | Business:Swiss franc (1850) |
| ro-cities-paterson-nj | city | 1851-04-14 | 12:00:00 UTC-4.94444 | Cities: Paterson NJ |
| ro-nature-mount-vesuvius-eruption-1855 | volcano | 1855-05-01 | 15:00:00 UTC+0.962222 | Nature:Mount Vesuvius eruption (1855) |
| ro-nature-earthquake-greece-1856-crete | earthquake | 1856-10-04 | 02:45:00 UTC+1.67556 | Nature:Earthquake Greece 1856 (Crete) |
| ro-orsini-plot | terror attack | 1858-01-14 | 20:30:00 UTC+0.155556 | Orsini Plot |
| ro-phenomena-omen-and-death | phenomenon | 1859-04-12 | 19:35:00 UTC+1.13578 | Phenomena:Omen and Death |
| ro-battle-of-solferino | military | 1859-06-24 | 14:00:00 UTC+0.704444 | Battle of Solferino |
| ro-military-civil-war-of-usa | military | 1861-04-12 | 04:30:00 UTC-5.32778 | Military: Civil War of USA |
| ro-historic-westminster-bridge | historic | 1862-05-24 | 04:00:00 UTC+0 | Historic: Westminster Bridge |
| ro-phenomena-louise-steudner | phenomenon | 1862-12-21 | 05:04:00 UTC+0 | Phenomena:Louise Steudner |
| ro-historic-london-underground-first-train | historic | 1863-01-10 | 06:00:00 UTC+0 | Historic: London Underground, First Train |
| ro-mortality-assassination-39537 | assassination | 1865-04-14 | 22:15:00 UTC-5.13556 | Mortality: Assassination 39537 |
| ro-nature-earthquake-greece-1867 | earthquake | 1867-02-04 | 04:19:00 UTC+1.36222 | Nature:Earthquake Greece 1867 |
| ro-nature-earthquake-greece-1867-b | earthquake | 1867-03-07 | 18:00:00 UTC+1.76889 | Nature:Earthquake Greece 1867 (b) |
| ro-phenomena-final-message-to-a-medium | phenomenon | 1868-02-07 | 08:00:00 UTC+0.155556 | Phenomena:Final message to a medium |
| ro-inauguration-hofoper-am-ring | inauguration | 1869-05-25 | 19:00:00 UTC+1.09154 | Inauguration:Hofoper am Ring |
| ro-phenomena-prophecy-sonrel-s-vision | phenomenon | 1869-07-23 | 13:54:00 UTC+0 | Phenomena:Prophecy:Sonrel's Vision |
| ro-accident-darmstadt-theatre-fire | fire | 1871-10-24 | 16:30:00 UTC+0.577778 | Accident:Darmstadt Theatre fire |
| ro-nature-mount-vesuvius-eruption-1872 | volcano | 1872-04-26 | 16:00:00 UTC+0.832222 | Nature:Mount Vesuvius eruption 1872 |
| ro-ufo-sighting-2770 | UFO sighting | 1872-12-07 | 01:00:00 UTC+0 | UFO Sighting 2770 |
| ro-ufo-sighting-2811 | UFO sighting | 1874-07-28 | 11:00:00 UTC-5.33333 | UFO Sighting 2811 |
| ro-phenomena-haunted-houses-calvados-case-og-scorpio | phenomenon | 1875-11-07 | 19:15:00 UTC+0 | Phenomena:Haunted Houses:Calvados Case (OG scorpio |
| ro-historic-theosophical-society | organization | 1875-11-17 | 20:00:00 UTC-4.93333 | Historic: Theosophical Society |
| ro-celestial-jupiter-saturn-uranus-pluto-cross | celestial | 1875-12-22 | 20:21:00 UTC+0 | Celestial: Jupiter-Saturn-Uranus-Pluto Cross |
| ro-ufo-sighting-2943 | UFO sighting | 1879-05-15 | 21:40:00 UTC+3.31111 | UFO Sighting 2943 |
| ro-disaster-tay-bridge-collapse | other | 1879-12-28 | 19:32:00 UTC+0 | Disaster: Tay Bridge collapse |
| ro-phenomena-extraordinary-message | phenomenon | 1880-03-25 | 20:30:00 UTC-0.21 | Phenomena:Extraordinary message |
| ro-ufo-sighting-2983 | UFO sighting | 1880-05-08 | 06:00:00 UTC+7.91778 | UFO Sighting 2983 |
| ro-phenomena-appearance-of-a-dying-son | phenomenon | 1881-01-24 | 07:30:00 UTC+0.155556 | Phenomena:Appearance of a dying son |
| ro-ufo-sighting-3020 | UFO sighting | 1881-06-11 | 04:00:00 UTC+9.94222 | UFO Sighting 3020 |
| ro-nature-elm-rockslide | landslide | 1881-09-11 | 17:35:00 UTC+0.496111 | Nature: Elm Rockslide |
| ro-accident-fire-vienna-theatre | fire | 1881-12-08 | 18:45:00 UTC+1.09154 | Accident: Fire, Vienna Theatre |
| ro-phenomena-the-worksop-disturbances-1883 | phenomenon | 1883-03-01 | 23:30:00 UTC+0 | Phenomena:The Worksop Disturbances (1883) |
| ro-phenomena-telepathic-event-a-fallen-baby | phenomenon | 1883-10-03 | 11:00:00 UTC+0 | Phenomena:Telepathic event:A fallen baby |
| ro-historic-washington-monument | historic | 1885-02-21 | 11:45:00 UTC-5 | Historic: Washington Monument |
| ro-historic-statue-of-liberty | historic | 1886-10-28 | 16:00:00 UTC-5 | Historic: Statue of Liberty |
| ro-nature-earthquake-kazakhstan-1887 | earthquake | 1887-06-08 | 23:35:00 UTC+0 | Nature:Earthquake Kazakhstan 1887 |
| ro-phenomena-telepathy-spatial-vision | phenomenon | 1889-01-14 | 14:15:00 UTC-5 | Phenomena:Telepathy:Spatial Vision |
| ro-historic-eiffel-tower | historic | 1889-03-31 | 14:35:00 UTC+0.155556 | Historic: Eiffel Tower |
| ro-nature-flood-jonestown | flood | 1889-05-31 | 03:10:00 UTC-5 | Nature: Flood Jonestown |
| ro-mortality-electrocution | death | 1890-08-06 | 06:36:00 UTC-5 | Mortality: Electrocution |
| ro-historic-pulitzer-building | historic | 1890-12-10 | 23:30:00 UTC-5 | Historic: Pulitzer Building |
| ro-synodic-nep-pluto-geo | celestial | 1891-08-02 | 09:29:00 UTC+0 | Synodic: Nep-Pluto Geo |
| ro-phenomena-dream-vision-railways-accident | phenomenon | 1891-12-30 | 03:00:00 UTC-6.20667 | Phenomena:Dream vision:Railways Accident |
| ro-synodic-nep-pluto-helio | celestial | 1892-01-29 | 08:51:00 UTC+0 | Synodic: Nep-Pluto Helio |
| ro-phenomena-a-ghost-s-rudiment | phenomenon | 1893-10-21 | 21:00:00 UTC+1 | Phenomena:A ghost's rudiment |
| ro-accident-ship-explosion | explosion | 1893-11-03 | 16:45:00 UTC-0.253333 | Accident: Ship explosion |
| ro-inauguration-tower-bridge | inauguration | 1894-06-30 | 12:00:00 UTC+0 | Inauguration:Tower Bridge |
| ro-phenomena-the-durweston-poltergeist | phenomenon | 1894-12-18 | 10:30:00 UTC+0 | Phenomena:The Durweston Poltergeist |
| ro-ufo-sighting-3697 | UFO sighting | 1896-08-18 | 21:00:00 UTC-8 | UFO Sighting 3697 |
| ro-ufo-sighting-3740 | UFO sighting | 1897-03-28 | 22:30:00 UTC-6 | UFO Sighting 3740 |
| ro-ufo-sighting-3741 | UFO sighting | 1897-04-01 | 21:00:00 UTC-6 | UFO Sighting 3741 |
| ro-ufo-sighting-3744 | UFO sighting | 1897-04-14 | 15:00:00 UTC-6 | UFO Sighting 3744 |
| ro-ufo-sighting-3745 | UFO sighting | 1897-04-15 | 21:00:00 UTC-6 | UFO Sighting 3745 |
| ro-ufo-sighting-3746 | UFO sighting | 1897-04-19 | 22:30:00 UTC-6 | UFO Sighting 3746 |
| ro-sports-boston-marathon | sports event | 1897-04-19 | 12:19:00 UTC-5 | Sports: Boston Marathon |
| ro-ufo-sighting-3749 | UFO sighting | 1897-04-22 | 23:30:00 UTC-6 | UFO Sighting 3749 |
| ro-phenomena-telepathic-dream-killing-an-actor | phenomenon | 1897-12-16 | 19:20:00 UTC+0 | Phenomena:Telepathic dream:Killing an Actor |
| ro-cities-new-york-new-york-consolidation | city | 1898-01-01 | 00:00:00 UTC-5 | Cities: New York, New York (Consolidation) |
| ro-nature-earthquake-turkmenistan-1898-iran | earthquake | 1898-11-17 | 15:06:00 UTC+0 | Nature:Earthquake Turkmenistan 1898 (Iran) |
| ro-nature-earthquake-turkey-1899 | earthquake | 1899-09-20 | 02:12:00 UTC+0 | Nature:Earthquake Turkey 1899 |
| ro-historic-spindletop | historic | 1901-01-10 | 10:32:00 UTC-6 | Historic: Spindletop |
| ro-mortality-assassination-40326 | assassination | 1901-09-06 | 16:00:00 UTC-5 | Mortality: Assassination 40326 |
| ro-nature-torishima-volcano-1902 | volcano | 1902-07-12 | 08:10:00 UTC+9 | Nature: Torishima Volcano (1902) |
| ro-ufo-sighting-4058 | UFO sighting | 1902-10-28 | 03:00:00 UTC+0 | UFO Sighting 4058 |
| ro-cities-denver-co-consol | city | 1902-12-01 | 00:00:00 UTC-7 | Cities: Denver CO (consol) |
| ro-sports-tour-de-france | sports event | 1903-07-01 | 15:16:00 UTC+0.155833 | Sports: Tour de France |
| ro-historic-new-york-city-subway | historic | 1904-10-27 | 14:35:00 UTC-5 | Historic: New York City Subway |
| ro-entertainment-peter-pan | entertainment | 1904-12-27 | 19:45:00 UTC+0 | Entertainment: Peter Pan |
| ro-entertainment-the-story-of-the-kelly-gang | entertainment | 1906-12-26 | 14:30:00 UTC+10 | Entertainment: The Story of the Kelly Gang |
| ro-mundane-tunguska-event | meteor | 1908-06-30 | 07:17:00 UTC+6.79667 | Mundane: Tunguska Event |
| ro-nature-asteroid-strike | meteor | 1908-06-30 | 07:17:00 UTC+6.81778 | Nature: Asteroid Strike |
| ro-ufo-sighting-4498 | UFO sighting | 1909-05-18 | 23:00:00 UTC+0 | UFO Sighting 4498 |
| ro-ufo-sighting-4537 | UFO sighting | 1910-02-05 | 23:45:00 UTC-8 | UFO Sighting 4537 |
| ro-accident-fire-nyc | fire | 1911-03-25 | 16:40:00 UTC-5 | Accident: Fire, NYC |
| ro-historic-titanic-voyage | historic | 1912-04-10 | 12:00:00 UTC+0 | Historic: Titanic Voyage |
| ro-historic-titanic-sinking | shipwreck | 1912-04-15 | 02:38:00 UTC+0 | Historic: Titanic Sinking |
| ro-phenomena-noisy-memories | phenomenon | 1912-04-27 | 04:00:00 UTC+0 | Phenomena:Noisy Memories |
| ro-sports-1912-summer-olympics-stockholm | business | 1912-07-06 | 12:00:00 UTC+1 | Sports: 1912 Summer Olympics, Stockholm |
| ro-historic-woolworth-building | historic | 1913-04-24 | 19:30:00 UTC-5 | Historic: Woolworth Building |
| ro-entertainment-art | entertainment | 1913-08-23 | 15:00:00 UTC+1 | Entertainment: Art |
| ro-business-federal-reserve | business | 1913-12-23 | 18:02:00 UTC-5 | Business: Federal Reserve |
| ro-aviation-scheduled-flight | air crash | 1914-01-01 | 10:10:00 UTC-6 | Aviation: Scheduled flight |
| ro-phenomena-prophecy-bishop-lanyi-s-dream | phenomenon | 1914-06-28 | 03:30:00 UTC+1 | Phenomena:Prophecy:Bishop Lanyi's dream |
| ro-phenomena-prophecy-major-gillhausen-s-vision | phenomenon | 1914-08-03 | 02:00:00 UTC+1 | Phenomena:Prophecy:Major Gillhausen's Vision |
| ro-space-naca | space flight | 1915-03-03 | 08:00:00 UTC-5 | Space: NACA |
| ro-historic-first-poison-attack-1915 | terror attack | 1915-04-22 | 17:00:00 UTC+0 | Historic: First poison attack 1915 |
| ro-ufo-sighting-4929 | UFO sighting | 1915-08-21 | 06:30:00 UTC+2 | UFO Sighting 4929 |
| ro-historic-battle-of-verdun | military | 1916-02-21 | 07:00:00 UTC+0 | Historic: Battle of Verdun |
| ro-phenomena-stall-spook-stuttgart | phenomenon | 1916-04-30 | 07:15:00 UTC+1 | Phenomena:Stall spook Stuttgart |
| ro-battle-of-jutland-1916 | military | 1916-05-31 | 16:48:00 UTC+2 | Battle of Jutland (1916) |
| ro-phenomena-fatima-last | phenomenon | 1917-10-13 | 13:30:00 UTC+1 | Phenomena: Fatima last |
| ro-nation-georgia-1918-independence | nation | 1918-05-26 | 17:10:00 UTC+2.98639 | Nation: Georgia (1918 Independence) |
| ro-phenomena-appearance-of-a-dying-friend | phenomenon | 1918-12-07 | 15:25:00 UTC+0 | Phenomena:Appearance of a dying friend |
| ro-ufo-sighting-5197 | UFO sighting | 1919-01-06 | 17:30:00 UTC+0 | UFO Sighting 5197 |
| ro-historic-treaty-of-versailles | political | 1919-06-28 | 15:12:00 UTC+1 | Historic: Treaty of Versailles |
| ro-business-coca-cola | business | 1919-09-05 | 12:00:00 UTC-4 | Business: Coca-Cola |
| ro-nature-earthquake-argentina-1920 | earthquake | 1920-12-10 | 04:26:07 UTC+0 | Nature:Earthquake Argentina 1920 |
| ro-nation-kingdom-of-iraq | founding | 1921-08-23 | 06:00:00 UTC+3 | Nation: Kingdom of Iraq |
| ro-ufo-sighting-5509 | UFO sighting | 1922-02-22 | 05:00:00 UTC-6 | UFO Sighting 5509 |
| ro-entertainment-bbc | entertainment | 1922-11-14 | 18:00:00 UTC+0 | Entertainment: BBC |
| ro-historic-egyptian-tomb | historic | 1923-02-16 | 13:15:00 UTC+2 | Historic: Egyptian tomb |
| ro-putsch-try-1923 | political | 1923-10-23 | 05:00:00 UTC+1 | Putsch try 1923 |
| ro-nature-tornado-midwest | tornado | 1925-03-18 | 01:05:00 UTC-6 | Nature: Tornado Midwest |
| ro-cities-brisbane-australia-amalgamation | city | 1925-10-01 | 00:01:00 UTC+10 | Cities: Brisbane, Australia (Amalgamation) |
| ro-nature-tokachidake-1926 | other | 1926-05-24 | 16:18:00 UTC+9 | Nature:Tokachidake 1926 |
| ro-ufo-sighting-6149 | UFO sighting | 1926-08-05 | 09:30:00 UTC+6.55667 | UFO Sighting 6149 |
| ro-entertainment-bbc-inc | entertainment | 1927-01-01 | 00:00:00 UTC+0 | Entertainment: BBC Inc. |
| ro-nature-earthquake-yugoslavia-1927-croatia | earthquake | 1927-02-14 | 03:43:00 UTC+0 | Nature:Earthquake Yugoslavia 1927 (Croatia) |
| ro-space-german-society-for-space-navigation | space flight | 1927-07-05 | 20:00:00 UTC+1 | Space: German Society for Space Navigation |
| ro-nation-vatican-city-state | founding | 1929-06-07 | 11:00:00 UTC+1 | Nation: Vatican City State |
| ro-ufo-sighting-6610 | UFO sighting | 1929-06-12 | 23:00:00 UTC-5 | UFO Sighting 6610 |
| ro-historic-kellogg-briand-pact | historic | 1929-07-24 | 00:00:00 UTC+1 | Historic: Kellogg-Briand Pact |
| ro-business-wall-street-crash | business | 1929-10-29 | 17:32:00 UTC-5 | Business: Wall Street Crash |
| ro-historic-museum-of-modern-art-moma | historic | 1929-11-08 | 09:00:00 UTC-5 | Historic: Museum of Modern Art (MoMA) |
| ro-celestial-pluto-discovery | celestial | 1930-02-18 | 16:00:00 UTC-7 | Celestial: Pluto Discovery |
| ro-nature-meteor-strike-brazil-1930 | meteor | 1930-08-13 | 12:04:00 UTC+0 | Nature: Meteor strike Brazil 1930 |
| ro-historic-empire-state-bldg | historic | 1931-05-01 | 11:30:00 UTC-4 | Historic: Empire State Bldg |
| ro-historic-sydney-harbour-bridge | historic | 1932-03-19 | 10:30:00 UTC+10 | Historic: Sydney Harbour Bridge |
| ro-sports-1932-summer-olympics-los-angeles | sports event | 1932-07-30 | 15:32:00 UTC-8 | Sports: 1932 Summer Olympics, Los Angeles |
| ro-sports-1932-winter-olympics-lake-placid | sports event | 1932-08-04 | 10:00:00 UTC-4 | Sports: 1932 Winter Olympics, Lake Placid |
| ro-geneva-s-revolt-1932 | political | 1932-11-09 | 21:34:00 UTC+1 | Geneva's Revolt 1932 |
| ro-political-hitler-appointed-as-chancellor-1933 | political | 1933-01-30 | 11:25:00 UTC+1 | Political: Hitler appointed as Chancellor (1933) |
| ro-entertainment-king-kong | entertainment | 1933-03-02 | 10:00:00 UTC-5 | Entertainment: King Kong |
| ro-ufo-sighting-7586 | UFO sighting | 1935-04-05 | 19:30:00 UTC+0 | UFO Sighting 7586 |
| ro-plane-crash-alaska-1935 | air crash | 1935-08-15 | 20:18:00 UTC-10 | Plane Crash: Alaska (1935) |
| ro-sports-olympic-torch-relay | sports event | 1936-08-01 | 11:42:00 UTC+1 | Sports: Olympic torch relay |
| ro-sports-1936-summer-olympics-berlin | sports event | 1936-08-01 | 17:03:00 UTC+1 | Sports: 1936 Summer Olympics, Berlin |
| ro-entertainment-guiding-light | entertainment | 1937-01-25 | 16:45:00 UTC-5 | Entertainment: Guiding Light |
| ro-shooting-spree-ponce-massacre | terror attack | 1937-03-21 | 15:15:00 UTC-4 | Shooting Spree: Ponce Massacre |
| ro-accident-hindenburg | air crash | 1937-05-06 | 19:23:00 UTC-4 | Accident: Hindenburg |
| ro-sports-st-louis-rams | sports event | 1937-09-10 | 20:30:00 UTC-5 | Sports: St. Louis Rams |
| ro-phenomena-last-greetings | phenomenon | 1938-02-14 | 12:00:00 UTC+1 | Phenomena:Last greetings |
| ro-astrology-afa | organization | 1938-05-04 | 11:38:00 UTC-5 | Astrology: AFA |
| ro-ufo-sighting-8216 | UFO sighting | 1938-07-25 | 23:30:00 UTC+2 | UFO Sighting 8216 |
| ro-historic-world-s-fair | historic | 1939-04-30 | 15:12:00 UTC-4 | Historic:  World's Fair |
| ro-historic-london-blitz-1940 | historic | 1940-09-07 | 20:10:00 UTC+1 | Historic: London Blitz 1940 |
| ro-historic-sinking-of-the-bismarck | shipwreck | 1941-05-27 | 10:40:00 UTC+2 | Historic: Sinking of the Bismarck |
| ro-historic-great-patriotic-war | military | 1941-06-22 | 04:00:00 UTC+2 | Historic: Great Patriotic War |
| ro-military-pearl-harbor | military | 1941-12-07 | 07:30:00 UTC-10.5 | Military: Pearl Harbor |
| ro-military-war-u-s-a-japan | military | 1941-12-08 | 16:20:00 UTC-5 | Military: War U.S.A.- Japan |
| ro-historic-pentagon | historic | 1942-04-29 | 10:30:00 UTC-4 | Historic: Pentagon |
| ro-entertainment-casablanca | entertainment | 1942-11-26 | 11:30:00 UTC-4 | Entertainment: Casablanca |
| ro-nuclear-first-atomic-reaction | nuclear test | 1942-12-02 | 15:40:00 UTC-5 | Nuclear: First Atomic Reaction |
| ro-science-atomic-pile | science | 1942-12-02 | 15:25:00 UTC-5 | Science: Atomic Pile |
| ro-1943-frankford-junction-derailment | rail accident | 1943-09-06 | 18:06:00 UTC-4 | 1943 Frankford Junction derailment |
| ro-celestial-neptune-cycle | celestial | 1944-03-07 | 10:06:00 UTC-4 | Celestial: Neptune Cycle |
| ro-historic-d-day | historic | 1944-06-06 | 06:30:00 UTC+2 | Historic: D Day |
| ro-ufo-sighting-9816 | UFO sighting | 1944-12-22 | 18:00:00 UTC+1 | UFO Sighting 9816 |
| ro-historic-tokyo-destroyed | historic | 1945-03-10 | 00:08:00 UTC+9 | Historic: Tokyo destroyed |
| ro-military-armistice-ww-ii | military | 1945-05-08 | 22:01:00 UTC+2 | Military: Armistice WW II |
| ro-historic-german-occupation | historic | 1945-06-05 | 18:00:00 UTC+3 | Historic: German Occupation |
| ro-nuclear-first-atomic-test | nuclear test | 1945-07-16 | 05:29:21 UTC-6 | Nuclear: First Atomic Test |
| ro-plane-crash-b-25-hits-empire-stat-building-1945 | air crash | 1945-07-28 | 09:49:00 UTC-4 | Plane Crash: B-25 hits Empire Stat Building (1945) |
| ro-nuclear-atomic-bombing-of-hiroshima | terror attack | 1945-08-06 | 08:15:00 UTC+9 | Nuclear: Atomic bombing of Hiroshima |
| ro-nuclear-second-atom-bomb | terror attack | 1945-08-09 | 11:02:00 UTC+9 | Nuclear: Second Atom Bomb |
| ro-historic-ww-ii-conclusion | historic | 1945-09-02 | 09:04:00 UTC+9 | Historic: WW II conclusion |
| ro-nature-sierre-earthquake-switzerland-1946 | earthquake | 1946-01-25 | 18:32:00 UTC+1 | Nature: Sierre Earthquake:Switzerland 1946 |
| ro-nature-earthquake-aleutians | earthquake | 1946-04-01 | 00:29:00 UTC+12 | Nature: Earthquake Aleutians |
| ro-ufo-sighting-10223 | UFO sighting | 1946-06-07 | 01:30:00 UTC-3 | UFO Sighting 10223 |
| ro-nature-hekla-eruption-1947 | volcano | 1947-03-29 | 06:45:00 UTC-1 | Nature:Hekla eruption ((1947) |
| ro-accident-texas-city-explosion-1947 | explosion | 1947-04-16 | 09:12:00 UTC-6 | Accident: Texas City Explosion 1947 |
| ro-ufo-sighting-10595 | UFO sighting | 1947-06-10 | 23:00:00 UTC-7 | UFO Sighting 10595 |
| ro-ufo-sighting-10607 | UFO sighting | 1947-06-21 | 11:50:00 UTC-8 | UFO Sighting 10607 |
| ro-ufo-sighting-10614 | UFO sighting | 1947-06-24 | 14:59:00 UTC-8 | UFO Sighting 10614 |
| ro-ufo-sighting-10617 | UFO sighting | 1947-06-27 | 10:30:00 UTC-7 | UFO Sighting 10617 |
| ro-ufo-sighting-10620 | UFO sighting | 1947-06-28 | 15:15:00 UTC-8 | UFO Sighting 10620 |
| ro-ufo-sighting-10621 | UFO sighting | 1947-06-28 | 21:20:00 UTC-6 | UFO Sighting 10621 |
| ro-ufo-sighting-10622 | UFO sighting | 1947-06-30 | 09:10:00 UTC-7 | UFO Sighting 10622 |
| ro-ufo-sighting-10628 | UFO sighting | 1947-07-02 | 21:50:00 UTC-7 | UFO Sighting 10628 |
| ro-ufo-sighting-10630 | UFO sighting | 1947-07-04 | 01:05:00 UTC-8 | UFO Sighting 10630 |
| ro-ufo-sighting-10633 | UFO sighting | 1947-07-07 | 16:00:00 UTC-7 | UFO Sighting 10633 |
| ro-ufo-sighting-10636 | UFO sighting | 1947-07-08 | 10:00:00 UTC-8 | UFO Sighting 10636 |
| ro-ufo-sighting-10658 | UFO sighting | 1947-07-16 | 16:47:00 UTC-7 | UFO Sighting 10658 |
| ro-ufo-sighting-10668 | UFO sighting | 1947-07-23 | 11:30:00 UTC-3 | UFO Sighting 10668 |
| ro-ufo-sighting-10669 | UFO sighting | 1947-07-23 | 14:00:00 UTC-3 | UFO Sighting 10669 |
| ro-historic-c-i-a-formation | historic | 1947-07-26 | 12:20:00 UTC-4 | Historic: C.I.A. formation |
| ro-accident-1947-ocean-liberty-explosion-france | explosion | 1947-07-28 | 17:24:00 UTC+1 | Accident: 1947 Ocean Liberty explosion, France |
| ro-ufo-sighting-10685 | UFO sighting | 1947-08-02 | 05:42:00 UTC-4 | UFO Sighting 10685 |
| ro-creation-conjunctions-saturn-pluto-1947 | celestial | 1947-08-11 | 01:20:00 UTC+0 | Creation conjunctions: Saturn-Pluto (1947) |
| ro-ufo-sighting-10698 | UFO sighting | 1947-08-13 | 13:00:00 UTC-7 | UFO Sighting 10698 |
| ro-astrology-dav | organization | 1947-10-16 | 12:24:00 UTC+1 | Astrology: DAV |
| ro-ufo-sighting-10829 | UFO sighting | 1948-01-01 | 00:15:00 UTC-6 | UFO Sighting 10829 |
| ro-ufo-sighting-10839 | UFO sighting | 1948-01-07 | 15:15:00 UTC-6 | UFO Sighting 10839 |
| ro-ufo-sighting-10841 | UFO sighting | 1948-01-09 | 19:20:00 UTC-5 | UFO Sighting 10841 |
| ro-mortality-gandhi-assassination | assassination | 1948-01-30 | 17:12:00 UTC+5.5 | Mortality: Gandhi assassination |
| ro-ufo-sighting-10958 | UFO sighting | 1948-05-25 | 20:00:00 UTC+1 | UFO Sighting 10958 |
| ro-law-nhs-england | law | 1948-07-05 | 00:00:00 UTC+1 | Law: NHS England |
| ro-ufo-sighting-10995 | UFO sighting | 1948-07-07 | 02:29:00 UTC-6 | UFO Sighting 10995 |
| ro-ufo-sighting-11007 | UFO sighting | 1948-07-24 | 02:45:00 UTC-6 | UFO Sighting 11007 |
| ro-sports-1948-summer-olympics-london | sports event | 1948-07-29 | 16:00:00 UTC+1 | Sports: 1948 Summer Olympics, London |
| ro-ufo-sighting-11021 | UFO sighting | 1948-08-11 | 00:00:00 UTC-6 | UFO Sighting 11021 |
| ro-historic-parliamentarian-council | historic | 1948-09-01 | 13:00:00 UTC+2 | Historic: Parliamentarian Council |
| ro-ufo-sighting-11064 | UFO sighting | 1948-10-01 | 21:00:00 UTC-6 | UFO Sighting 11064 |
| ro-ufo-sighting-11105 | UFO sighting | 1948-11-23 | 22:00:00 UTC+1 | UFO Sighting 11105 |
| ro-ufo-sighting-11114 | UFO sighting | 1948-12-05 | 21:27:00 UTC-7 | UFO Sighting 11114 |
| ro-ufo-sighting-11116 | UFO sighting | 1948-12-08 | 18:33:00 UTC-7 | UFO Sighting 11116 |
| ro-ufo-sighting-11226 | UFO sighting | 1949-04-24 | 10:30:00 UTC-7 | UFO Sighting 11226 |
| ro-ufo-sighting-11337 | UFO sighting | 1949-08-20 | 22:45:00 UTC-7 | UFO Sighting 11337 |
| ro-nuclear-first-soviet-nuclear-try | nuclear test | 1949-08-29 | 07:00:00 UTC+6 | Nuclear:First Soviet Nuclear try |
| ro-nation-german-democratic-republic-ddr | republic | 1949-10-07 | 12:45:00 UTC+1 | Nation: German Democratic Republic (DDR) |
| ro-accident-air-france-lockheed-constellation-crash | air crash | 1949-10-28 | 02:51:00 UTC-2 | Accident: Air France Lockheed Constellation Crash |
| ro-ufo-sighting-11423 | UFO sighting | 1949-12-04 | 17:00:00 UTC-2 | UFO Sighting 11423 |
| ro-ufo-sighting-11510 | UFO sighting | 1950-03-08 | 10:00:00 UTC-5 | UFO Sighting 11510 |
| ro-ufo-sighting-11520 | UFO sighting | 1950-03-17 | 10:15:00 UTC-7 | UFO Sighting 11520 |
| ro-ufo-sighting-11521 | UFO sighting | 1950-03-18 | 18:30:00 UTC-3 | UFO Sighting 11521 |
| ro-ufo-sighting-11536 | UFO sighting | 1950-03-28 | 04:17:00 UTC+1 | UFO Sighting 11536 |
| ro-ufo-sighting-11537 | UFO sighting | 1950-03-28 | 21:00:00 UTC+1 | UFO Sighting 11537 |
| ro-ufo-sighting-11543 | UFO sighting | 1950-04-08 | 02:00:00 UTC-6 | UFO Sighting 11543 |
| ro-ufo-sighting-11561 | UFO sighting | 1950-05-07 | 18:45:00 UTC-7 | UFO Sighting 11561 |
| ro-ufo-sighting-11567 | UFO sighting | 1950-05-11 | 07:30:00 UTC-7 | UFO Sighting 11567 |
| ro-ufo-sighting-11575 | UFO sighting | 1950-05-22 | 12:15:00 UTC-7 | UFO Sighting 11575 |
| ro-ufo-sighting-11611 | UFO sighting | 1950-07-04 | 20:45:00 UTC-7 | UFO Sighting 11611 |
| ro-ufo-sighting-11662 | UFO sighting | 1950-08-15 | 11:30:00 UTC-7 | UFO Sighting 11662 |
| ro-ufo-sighting-11829 | UFO sighting | 1951-03-12 | 16:00:00 UTC+1 | UFO Sighting 11829 |
| ro-ufo-sighting-11834 | UFO sighting | 1951-03-15 | 10:30:00 UTC+5.5 | UFO Sighting 11834 |
| ro-ufo-sighting-11899 | UFO sighting | 1951-06-19 | 12:00:00 UTC+1 | UFO Sighting 11899 |
| ro-entertainment-beauty-contest | entertainment | 1951-07-27 | 21:00:00 UTC+1 | Entertainment: Beauty Contest |
| ro-phenomena-the-dieppe-case | phenomenon | 1951-08-04 | 04:00:00 UTC+1 | Phenomena:The Dieppe Case |
| ro-ufo-sighting-11953 | UFO sighting | 1951-08-25 | 21:10:00 UTC-7 | UFO Sighting 11953 |
| ro-ufo-sighting-11954 | UFO sighting | 1951-08-25 | 21:20:00 UTC-6 | UFO Sighting 11954 |
| ro-entertainment-search-for-tomorrow | entertainment | 1951-09-03 | 12:30:00 UTC-4 | Entertainment: Search for Tomorrow |
| ro-ufo-sighting-11967 | UFO sighting | 1951-09-10 | 11:10:00 UTC-4 | UFO Sighting 11967 |
| ro-ufo-sighting-11968 | UFO sighting | 1951-09-10 | 11:35:00 UTC-4 | UFO Sighting 11968 |
| ro-ufo-sighting-11969 | UFO sighting | 1951-09-10 | 15:15:00 UTC-4 | UFO Sighting 11969 |
| ro-ufo-sighting-11980 | UFO sighting | 1951-09-18 | 00:20:00 UTC-2.5 | UFO Sighting 11980 |
| ro-ufo-sighting-11984 | UFO sighting | 1951-09-23 | 07:55:00 UTC-7 | UFO Sighting 11984 |
| ro-entertainment-i-love-lucy | entertainment | 1951-10-15 | 21:00:00 UTC-5 | Entertainment: I Love Lucy |
| ro-ufo-sighting-12012 | UFO sighting | 1951-11-02 | 23:00:00 UTC-8 | UFO Sighting 12012 |
| ro-ufo-sighting-12144 | UFO sighting | 1952-05-07 | 16:22:00 UTC-3 | UFO Sighting 12144 |
| ro-ufo-sighting-12179 | UFO sighting | 1952-06-13 | 15:30:00 UTC+1 | UFO Sighting 12179 |
| ro-ufo-sighting-12181 | UFO sighting | 1952-06-15 | 15:40:00 UTC-5 | UFO Sighting 12181 |
| ro-ufo-sighting-12182 | UFO sighting | 1952-06-15 | 16:20:00 UTC-5 | UFO Sighting 12182 |
| ro-ufo-sighting-12183 | UFO sighting | 1952-06-15 | 16:25:00 UTC-5 | UFO Sighting 12183 |
| ro-ufo-sighting-12184 | UFO sighting | 1952-06-15 | 16:43:00 UTC-5 | UFO Sighting 12184 |
| ro-ufo-sighting-12185 | UFO sighting | 1952-06-15 | 17:43:00 UTC-5 | UFO Sighting 12185 |
| ro-ufo-sighting-12186 | UFO sighting | 1952-06-15 | 19:35:00 UTC-5 | UFO Sighting 12186 |
| ro-ufo-sighting-12187 | UFO sighting | 1952-06-15 | 19:59:00 UTC-5 | UFO Sighting 12187 |
| ro-ufo-sighting-12192 | UFO sighting | 1952-06-21 | 22:58:00 UTC-5 | UFO Sighting 12192 |
| ro-business-bild-newspaper | business | 1952-06-24 | 05:30:00 UTC+1 | Business: Bild newspaper |
| ro-ufo-sighting-12195 | UFO sighting | 1952-06-28 | 13:20:00 UTC-7 | UFO Sighting 12195 |
| ro-ufo-sighting-12200 | UFO sighting | 1952-07-01 | 07:25:00 UTC-4 | UFO Sighting 12200 |
| ro-ufo-sighting-12201 | UFO sighting | 1952-07-01 | 07:30:00 UTC-4 | UFO Sighting 12201 |
| ro-ufo-sighting-12202 | UFO sighting | 1952-07-01 | 09:30:00 UTC-4 | UFO Sighting 12202 |
| ro-ufo-sighting-12211 | UFO sighting | 1952-07-12 | 21:40:00 UTC-6 | UFO Sighting 12211 |
| ro-ufo-sighting-12215 | UFO sighting | 1952-07-18 | 22:45:00 UTC-5 | UFO Sighting 12215 |
| ro-ufo-sighting-12217 | UFO sighting | 1952-07-19 | 23:30:00 UTC-4 | UFO Sighting 12217 |
| ro-sports-1952-summer-olympics-helsinki | sports event | 1952-07-19 | 14:10:00 UTC+2 | Sports: 1952 Summer Olympics, Helsinki |
| ro-ufo-sighting-12226 | UFO sighting | 1952-07-26 | 22:10:00 UTC-4 | UFO Sighting 12226 |
| ro-ufo-sighting-12228 | UFO sighting | 1952-07-28 | 01:00:00 UTC-7 | UFO Sighting 12228 |
| ro-ufo-sighting-12231 | UFO sighting | 1952-08-03 | 23:00:00 UTC-7 | UFO Sighting 12231 |
| ro-ufo-sighting-12232 | UFO sighting | 1952-08-04 | 23:00:00 UTC-7 | UFO Sighting 12232 |
| ro-ufo-sighting-12234 | UFO sighting | 1952-08-05 | 11:45:00 UTC+9 | UFO Sighting 12234 |
| ro-phenomena-the-runcorn-poltergeist-begin | phenomenon | 1952-08-14 | 00:03:00 UTC+0 | Phenomena:The Runcorn poltergeist (begin) |
| ro-ufo-sighting-12246 | UFO sighting | 1952-08-18 | 23:00:00 UTC-7 | UFO Sighting 12246 |
| ro-ufo-sighting-12250 | UFO sighting | 1952-08-24 | 06:00:00 UTC-6 | UFO Sighting 12250 |
| ro-ufo-sighting-12257 | UFO sighting | 1952-09-05 | 23:00:00 UTC-7 | UFO Sighting 12257 |
| ro-ufo-sighting-12258 | UFO sighting | 1952-09-06 | 23:00:00 UTC-7 | UFO Sighting 12258 |
| ro-ufo-sighting-12265 | UFO sighting | 1952-09-16 | 23:00:00 UTC-7 | UFO Sighting 12265 |
| ro-ufo-sighting-12268 | UFO sighting | 1952-09-23 | 23:00:00 UTC-7 | UFO Sighting 12268 |
| ro-ufo-sighting-12279 | UFO sighting | 1952-10-02 | 23:00:00 UTC-7 | UFO Sighting 12279 |
| ro-ufo-sighting-12285 | UFO sighting | 1952-10-12 | 23:00:00 UTC-7 | UFO Sighting 12285 |
| ro-ufo-sighting-12288 | UFO sighting | 1952-10-15 | 19:10:00 UTC+1 | UFO Sighting 12288 |
| ro-ufo-sighting-12296 | UFO sighting | 1952-10-27 | 02:03:00 UTC+1 | UFO Sighting 12296 |
| ro-ufo-sighting-12306 | UFO sighting | 1952-11-02 | 23:00:00 UTC-7 | UFO Sighting 12306 |
| ro-ufo-sighting-12316 | UFO sighting | 1952-11-20 | 12:30:00 UTC-8 | UFO Sighting 12316 |
| ro-ufo-sighting-12377 | UFO sighting | 1953-02-28 | 18:40:00 UTC+2 | UFO Sighting 12377 |
| ro-ufo-sighting-12441 | UFO sighting | 1953-06-18 | 02:30:00 UTC-6 | UFO Sighting 12441 |
| ro-ufo-sighting-12445 | UFO sighting | 1953-06-24 | 18:00:00 UTC-4 | UFO Sighting 12445 |
| ro-ufo-sighting-12448 | UFO sighting | 1953-07-02 | 13:00:00 UTC+1 | UFO Sighting 12448 |
| ro-ufo-sighting-12459 | UFO sighting | 1953-07-31 | 19:00:00 UTC+1 | UFO Sighting 12459 |
| ro-ufo-sighting-12465 | UFO sighting | 1953-08-05 | 20:05:00 UTC-7 | UFO Sighting 12465 |
| ro-ufo-sighting-12466 | UFO sighting | 1953-08-05 | 23:42:00 UTC-6 | UFO Sighting 12466 |
| ro-ufo-sighting-12475 | UFO sighting | 1953-08-16 | 20:30:00 UTC+1 | UFO Sighting 12475 |
| ro-plane-crash-air-france-mont-cimet-1953 | air crash | 1953-09-01 | 23:30:00 UTC+1 | Plane Crash: Air France Mont Cimet (1953) |
| ro-ufo-sighting-12483 | UFO sighting | 1953-09-04 | 21:30:00 UTC+1 | UFO Sighting 12483 |
| ro-ufo-sighting-12507 | UFO sighting | 1953-10-15 | 10:00:00 UTC-6 | UFO Sighting 12507 |
| ro-ufo-sighting-12513 | UFO sighting | 1953-10-25 | 21:30:00 UTC-7 | UFO Sighting 12513 |
| ro-ufo-sighting-12559 | UFO sighting | 1954-01-04 | 21:00:00 UTC+1 | UFO Sighting 12559 |
| ro-ufo-sighting-12581 | UFO sighting | 1954-02-18 | 16:00:00 UTC+0 | UFO Sighting 12581 |
| ro-ufo-sighting-12588 | UFO sighting | 1954-02-27 | 09:30:00 UTC+2 | UFO Sighting 12588 |
| ro-nuclear-castle-bravo-thermonuclear-bomb | terror attack | 1954-03-01 | 06:45:00 UTC+11 | Nuclear: Castle Bravo Thermonuclear Bomb |
| ro-ufo-sighting-12623 | UFO sighting | 1954-04-22 | 14:00:00 UTC-8 | UFO Sighting 12623 |
| ro-ufo-sighting-12633 | UFO sighting | 1954-05-15 | 22:30:00 UTC+1 | UFO Sighting 12633 |
| ro-ufo-sighting-12643 | UFO sighting | 1954-06-09 | 18:20:00 UTC+10 | UFO Sighting 12643 |
| ro-sports-miracle-of-berne-1954 | sports event | 1954-07-04 | 17:00:00 UTC+1 | Sports: Miracle of Berne 1954 |
| ro-ufo-sighting-12678 | UFO sighting | 1954-08-07 | 16:15:00 UTC+1 | UFO Sighting 12678 |
| ro-ufo-sighting-12685 | UFO sighting | 1954-08-10 | 21:30:00 UTC-4 | UFO Sighting 12685 |
| ro-ufo-sighting-12693 | UFO sighting | 1954-08-28 | 20:30:00 UTC-6 | UFO Sighting 12693 |
| ro-ufo-sighting-12695 | UFO sighting | 1954-08-30 | 05:40:00 UTC-4 | UFO Sighting 12695 |
| ro-ufo-sighting-12696 | UFO sighting | 1954-09-06 | 23:05:00 UTC-3 | UFO Sighting 12696 |
| ro-ufo-sighting-12697 | UFO sighting | 1954-09-07 | 00:30:00 UTC-3 | UFO Sighting 12697 |
| ro-ufo-sighting-12698 | UFO sighting | 1954-09-07 | 07:15:00 UTC+1 | UFO Sighting 12698 |
| ro-ufo-sighting-12700 | UFO sighting | 1954-09-10 | 20:30:00 UTC+1 | UFO Sighting 12700 |
| ro-ufo-sighting-12701 | UFO sighting | 1954-09-10 | 22:30:00 UTC+1 | UFO Sighting 12701 |
| ro-ufo-sighting-12703 | UFO sighting | 1954-09-14 | 22:00:00 UTC-6 | UFO Sighting 12703 |
| ro-ufo-sighting-12704 | UFO sighting | 1954-09-15 | 23:20:00 UTC+1 | UFO Sighting 12704 |
| ro-ufo-sighting-12705 | UFO sighting | 1954-09-17 | 22:30:00 UTC+1 | UFO Sighting 12705 |
| ro-ufo-sighting-12707 | UFO sighting | 1954-09-18 | 20:15:00 UTC+0 | UFO Sighting 12707 |
| ro-ufo-sighting-12708 | UFO sighting | 1954-09-18 | 21:40:00 UTC-7 | UFO Sighting 12708 |
| ro-ufo-sighting-12709 | UFO sighting | 1954-09-19 | 21:15:00 UTC+1 | UFO Sighting 12709 |
| ro-ufo-sighting-12710 | UFO sighting | 1954-09-20 | 23:00:00 UTC-1 | UFO Sighting 12710 |
| ro-ufo-sighting-12715 | UFO sighting | 1954-09-23 | 21:00:00 UTC+1 | UFO Sighting 12715 |
| ro-ufo-sighting-12716 | UFO sighting | 1954-09-24 | 10:00:00 UTC+1 | UFO Sighting 12716 |
| ro-ufo-sighting-12717 | UFO sighting | 1954-09-24 | 23:00:00 UTC+1 | UFO Sighting 12717 |
| ro-ufo-sighting-12719 | UFO sighting | 1954-09-26 | 14:30:00 UTC+1 | UFO Sighting 12719 |
| ro-ufo-sighting-12724 | UFO sighting | 1954-09-29 | 22:30:00 UTC+1 | UFO Sighting 12724 |
| ro-ufo-sighting-12725 | UFO sighting | 1954-09-30 | 04:45:00 UTC-5 | UFO Sighting 12725 |
| ro-ufo-sighting-12726 | UFO sighting | 1954-10-03 | 18:45:00 UTC+1 | UFO Sighting 12726 |
| ro-ufo-sighting-12728 | UFO sighting | 1954-10-05 | 04:00:00 UTC+1 | UFO Sighting 12728 |
| ro-ufo-sighting-12730 | UFO sighting | 1954-10-07 | 02:00:00 UTC+1 | UFO Sighting 12730 |
| ro-ufo-sighting-12732 | UFO sighting | 1954-10-07 | 19:30:00 UTC+1 | UFO Sighting 12732 |
| ro-ufo-sighting-12733 | UFO sighting | 1954-10-08 | 02:30:00 UTC+3.5 | UFO Sighting 12733 |
| ro-ufo-sighting-12735 | UFO sighting | 1954-10-10 | 11:45:00 UTC+1 | UFO Sighting 12735 |
| ro-ufo-sighting-12736 | UFO sighting | 1954-10-11 | 19:30:00 UTC+1 | UFO Sighting 12736 |
| ro-ufo-sighting-12738 | UFO sighting | 1954-10-14 | 06:30:00 UTC+3.5 | UFO Sighting 12738 |
| ro-ufo-sighting-12739 | UFO sighting | 1954-10-14 | 12:30:00 UTC+1 | UFO Sighting 12739 |
| ro-ufo-sighting-12740 | UFO sighting | 1954-10-16 | 16:00:00 UTC+1 | UFO Sighting 12740 |
| ro-ufo-sighting-12743 | UFO sighting | 1954-10-19 | 19:20:00 UTC+1 | UFO Sighting 12743 |
| ro-ufo-sighting-12744 | UFO sighting | 1954-10-19 | 22:30:00 UTC+1 | UFO Sighting 12744 |
| ro-ufo-sighting-12745 | UFO sighting | 1954-10-23 | 01:00:00 UTC+1 | UFO Sighting 12745 |
| ro-ufo-sighting-12746 | UFO sighting | 1954-10-23 | 03:00:00 UTC+1 | UFO Sighting 12746 |
| ro-ufo-sighting-12750 | UFO sighting | 1954-11-02 | 18:00:00 UTC+1 | UFO Sighting 12750 |
| ro-ufo-sighting-12755 | UFO sighting | 1954-11-08 | 10:30:00 UTC+1 | UFO Sighting 12755 |
| ro-ufo-sighting-12758 | UFO sighting | 1954-11-13 | 03:30:00 UTC-3 | UFO Sighting 12758 |
| ro-ufo-sighting-12759 | UFO sighting | 1954-11-17 | 02:15:00 UTC+1 | UFO Sighting 12759 |
| ro-ufo-sighting-12761 | UFO sighting | 1954-11-22 | 21:45:00 UTC-3 | UFO Sighting 12761 |
| ro-ufo-sighting-12765 | UFO sighting | 1954-11-27 | 16:15:00 UTC+3 | UFO Sighting 12765 |
| ro-ufo-sighting-12766 | UFO sighting | 1954-11-28 | 02:00:00 UTC-4.5 | UFO Sighting 12766 |
| ro-ufo-sighting-12781 | UFO sighting | 1955-01-03 | 07:25:00 UTC+10 | UFO Sighting 12781 |
| ro-ufo-sighting-12817 | UFO sighting | 1955-03-02 | 17:00:00 UTC-6 | UFO Sighting 12817 |
| ro-ufo-sighting-12838 | UFO sighting | 1955-04-06 | 09:02:00 UTC-3 | UFO Sighting 12838 |
| ro-nation-austria-2nd-republic | republic | 1955-05-15 | 11:31:00 UTC+1 | Nation: Austria (2nd Republic) |
| ro-accident-1955-le-mans-disaster | accident | 1955-06-11 | 18:28:00 UTC+1 | Accident: 1955 Le Mans disaster |
| ro-entertainment-disneyland | entertainment | 1955-07-18 | 10:00:00 UTC-7 | Entertainment: Disneyland |
| ro-ufo-sighting-12876 | UFO sighting | 1955-08-16 | 04:00:00 UTC+1 | UFO Sighting 12876 |
| ro-ufo-sighting-12880 | UFO sighting | 1955-08-20 | 22:45:00 UTC-5 | UFO Sighting 12880 |
| ro-ufo-sighting-12883 | UFO sighting | 1955-08-21 | 20:30:00 UTC-6 | UFO Sighting 12883 |
| ro-ufo-sighting-12884 | UFO sighting | 1955-08-22 | 14:00:00 UTC-7 | UFO Sighting 12884 |
| ro-nature-eruption-besymjanny-1955 | volcano | 1955-10-22 | 06:00:00 UTC+12 | Nature:Eruption:Besymjanny (1955) |
| ro-ufo-sighting-12962 | UFO sighting | 1956-02-17 | 23:00:00 UTC+1 | UFO Sighting 12962 |
| ro-entertainment-as-the-world-turns | entertainment | 1956-04-02 | 13:30:00 UTC-5 | Entertainment: As the World Turns |
| ro-ufo-sighting-12980 | UFO sighting | 1956-04-07 | 07:30:00 UTC+2 | UFO Sighting 12980 |
| ro-ufo-sighting-12997 | UFO sighting | 1956-05-09 | 23:00:00 UTC-5 | UFO Sighting 12997 |
| ro-entertainment-eurovision-song-contest | entertainment | 1956-05-24 | 21:00:00 UTC+1 | Entertainment: Eurovision Song Contest |
| ro-sports-1956-summer-olympics-melbourne | sports event | 1956-11-22 | 16:25:00 UTC+10 | Sports: 1956 Summer Olympics, Melbourne |
| ro-science-atomic-energy | science | 1957-02-09 | 15:01:00 UTC-6 | Science: Atomic Energy |
| ro-historic-treaty-of-rome | political | 1957-03-25 | 18:50:00 UTC+1 | Historic: Treaty of Rome |
| ro-ufo-sighting-13121 | UFO sighting | 1957-04-19 | 11:52:00 UTC+9 | UFO Sighting 13121 |
| ro-ufo-sighting-13140 | UFO sighting | 1957-06-03 | 21:35:00 UTC-6 | UFO Sighting 13140 |
| ro-ufo-sighting-13161 | UFO sighting | 1957-07-22 | 20:00:00 UTC-3 | UFO Sighting 13161 |
| ro-ufo-sighting-13163 | UFO sighting | 1957-07-25 | 19:00:00 UTC-3 | UFO Sighting 13163 |
| ro-ufo-sighting-13169 | UFO sighting | 1957-08-22 | 15:40:00 UTC-5 | UFO Sighting 13169 |
| ro-ufo-sighting-13173 | UFO sighting | 1957-09-01 | 23:55:00 UTC+1 | UFO Sighting 13173 |
| ro-accident-kyshtym-nuclear-explosion | nuclear test | 1957-09-29 | 16:22:00 UTC+5 | Accident: Kyshtym nuclear explosion |
| ro-space-sputnik-1 | space flight | 1957-10-04 | 19:28:34 UTC+0 | Space: Sputnik 1 |
| ro-entertainment-leave-it-to-beaver | TV show | 1957-10-04 | 19:30:00 UTC-4 | Entertainment: Leave It to Beaver |
| ro-ufo-sighting-13183 | UFO sighting | 1957-10-05 | 23:00:00 UTC-3 | UFO Sighting 13183 |
| ro-ufo-sighting-13184 | UFO sighting | 1957-10-08 | 15:00:00 UTC+12 | UFO Sighting 13184 |
| ro-ufo-sighting-13187 | UFO sighting | 1957-10-14 | 21:45:00 UTC-3 | UFO Sighting 13187 |
| ro-ufo-sighting-13188 | UFO sighting | 1957-10-15 | 01:00:00 UTC-3 | UFO Sighting 13188 |
| ro-ufo-sighting-13189 | UFO sighting | 1957-10-16 | 13:30:00 UTC-7 | UFO Sighting 13189 |
| ro-ufo-sighting-13197 | UFO sighting | 1957-10-25 | 21:00:00 UTC-3 | UFO Sighting 13197 |
| ro-ufo-sighting-13200 | UFO sighting | 1957-11-02 | 03:30:00 UTC-6 | UFO Sighting 13200 |
| ro-ufo-sighting-13201 | UFO sighting | 1957-11-02 | 11:50:00 UTC-6 | UFO Sighting 13201 |
| ro-ufo-sighting-13202 | UFO sighting | 1957-11-02 | 22:50:00 UTC-6 | UFO Sighting 13202 |
| ro-ufo-sighting-13204 | UFO sighting | 1957-11-03 | 03:00:00 UTC-7 | UFO Sighting 13204 |
| ro-ufo-sighting-13206 | UFO sighting | 1957-11-04 | 03:15:00 UTC-6 | UFO Sighting 13206 |
| ro-ufo-sighting-13207 | UFO sighting | 1957-11-04 | 22:45:00 UTC-7 | UFO Sighting 13207 |
| ro-ufo-sighting-13208 | UFO sighting | 1957-11-05 | 04:30:00 UTC-5 | UFO Sighting 13208 |
| ro-ufo-sighting-13212 | UFO sighting | 1957-11-06 | 00:10:00 UTC-7 | UFO Sighting 13212 |
| ro-ufo-sighting-13213 | UFO sighting | 1957-11-06 | 06:30:00 UTC-5 | UFO Sighting 13213 |
| ro-ufo-sighting-13215 | UFO sighting | 1957-11-07 | 07:25:00 UTC-6 | UFO Sighting 13215 |
| ro-business-disney-stock | business | 1957-11-12 | 10:00:00 UTC-5 | Business: Disney stock |
| ro-ufo-sighting-13225 | UFO sighting | 1957-11-16 | 22:30:00 UTC-3 | UFO Sighting 13225 |
| ro-ufo-sighting-13238 | UFO sighting | 1957-12-21 | 18:30:00 UTC-4 | UFO Sighting 13238 |
| ro-ufo-sighting-13247 | UFO sighting | 1958-01-16 | 12:30:00 UTC-2 | UFO Sighting 13247 |
| ro-ufo-sighting-13250 | UFO sighting | 1958-01-26 | 16:00:00 UTC+9 | UFO Sighting 13250 |
| ro-ufo-sighting-13257 | UFO sighting | 1958-02-02 | 15:30:00 UTC+9 | UFO Sighting 13257 |
| ro-plane-crash-british-european-airways-fly-609-1958 | air crash | 1958-02-06 | 15:03:00 UTC+0 | Plane crash:British-European-Airways fly 609 (1958 |
| ro-ufo-sighting-13279 | UFO sighting | 1958-04-17 | 19:25:00 UTC-3 | UFO Sighting 13279 |
| ro-astrology-aa-of-great-britain | organization | 1958-06-21 | 20:22:00 UTC+1 | Astrology: AA of Great Britain |
| ro-nation-republic-of-iraq | republic | 1958-07-14 | 07:00:00 UTC+3 | Nation: Republic of Iraq |
| ro-ufo-sighting-13318 | UFO sighting | 1958-08-13 | 20:00:00 UTC+1 | UFO Sighting 13318 |
| ro-ufo-sighting-13320 | UFO sighting | 1958-08-16 | 17:00:00 UTC+1 | UFO Sighting 13320 |
| ro-accident-eastbourne-rail-crash | rail accident | 1958-08-25 | 07:27:00 UTC+1 | Accident: Eastbourne rail crash |
| ro-entertainment-the-donna-reed-show | entertainment | 1958-09-24 | 21:00:00 UTC-4 | Entertainment: The Donna Reed Show |
| ro-space-nasa-opening | space flight | 1958-10-01 | 08:00:00 UTC-5 | Space: NASA opening |
| ro-ufo-sighting-13350 | UFO sighting | 1958-10-26 | 22:30:00 UTC-5 | UFO Sighting 13350 |
| ro-ufo-sighting-13361 | UFO sighting | 1958-11-23 | 23:25:00 UTC-6 | UFO Sighting 13361 |
| ro-ufo-sighting-13368 | UFO sighting | 1958-12-20 | 02:55:00 UTC+1 | UFO Sighting 13368 |
| ro-ufo-sighting-13370 | UFO sighting | 1958-12-22 | 15:00:00 UTC+1 | UFO Sighting 13370 |
| ro-ufo-sighting-13391 | UFO sighting | 1959-03-04 | 19:30:00 UTC+0 | UFO Sighting 13391 |
| ro-entertainment-barbie | entertainment | 1959-03-09 | 10:00:00 UTC-5 | Entertainment: Barbie |
| ro-ufo-sighting-13395 | UFO sighting | 1959-03-13 | 14:10:00 UTC+9.5 | UFO Sighting 13395 |
| ro-ufo-sighting-13398 | UFO sighting | 1959-03-25 | 11:30:00 UTC+1 | UFO Sighting 13398 |
| ro-ufo-sighting-13401 | UFO sighting | 1959-04-01 | 18:30:00 UTC-8 | UFO Sighting 13401 |
| ro-ufo-sighting-13402 | UFO sighting | 1959-04-01 | 19:00:00 UTC-8 | UFO Sighting 13402 |
| ro-space-mercury-seven-astronaut-group | space flight | 1959-04-09 | 14:00:00 UTC-5 | Space: Mercury Seven (astronaut group) |
| ro-ufo-sighting-13437 | UFO sighting | 1959-06-26 | 18:45:00 UTC+10 | UFO Sighting 13437 |
| ro-federated-state-hawaii | political | 1959-08-21 | 10:12:00 UTC-10 | Federated state: Hawaii |
| ro-ufo-sighting-13457 | UFO sighting | 1959-08-25 | 11:00:00 UTC+1 | UFO Sighting 13457 |
| ro-entertainment-bonanza | TV show | 1959-09-12 | 19:30:00 UTC-4 | Entertainment: Bonanza |
| ro-sports-denver-broncos | sports event | 1959-11-22 | 09:00:00 UTC-7 | Sports: Denver Broncos |
| ro-ufo-sighting-13498 | UFO sighting | 1959-12-22 | 23:50:00 UTC-8 | UFO Sighting 13498 |
| ro-nation-brazil | founding | 1960-04-21 | 09:30:00 UTC-3 | Nation: Brazil |
| ro-ufo-sighting-13540 | UFO sighting | 1960-05-14 | 04:00:00 UTC-3 | UFO Sighting 13540 |
| ro-ufo-sighting-13545 | UFO sighting | 1960-06-10 | 03:30:00 UTC+1 | UFO Sighting 13545 |
| ro-ufo-sighting-13568 | UFO sighting | 1960-08-13 | 23:15:00 UTC-7 | UFO Sighting 13568 |
| ro-sports-1960-summer-olympics-rome | sports event | 1960-08-25 | 17:43:00 UTC+1 | Sports: 1960 Summer Olympics, Rome |
| ro-sports-new-england-patriots | sports event | 1960-09-09 | 20:00:00 UTC-4 | Sports: New England Patriots |
| ro-entertainment-the-flintstones | TV show | 1960-09-30 | 20:30:00 UTC-4 | Entertainment: The Flintstones |
| ro-phenomena-the-sauchie-case | phenomenon | 1960-11-22 | 21:00:00 UTC+0 | Phenomena:The Sauchie Case |
| ro-entertainment-coronation-street | entertainment | 1960-12-09 | 19:00:00 UTC+0 | Entertainment: Coronation Street |
| ro-entertainment-the-avengers | TV show | 1961-01-07 | 22:00:00 UTC+0 | Entertainment: The Avengers |
| ro-plane-crash-green-cross-tragedy-chile | air crash | 1961-04-03 | 23:57:00 UTC-4 | Plane crash: Green Cross tragedy (Chile) |
| ro-space-vostok-1-first-human-spaceflight | space flight | 1961-04-12 | 06:07:00 UTC+0 | Space: Vostok 1 (first human spaceflight) |
| ro-ufo-sighting-13662 | UFO sighting | 1961-04-18 | 11:00:00 UTC-6 | UFO Sighting 13662 |
| ro-space-mercury-redstone-3-launch | space flight | 1961-05-05 | 09:34:13 UTC-5 | Space: Mercury-Redstone 3 (Launch) |
| ro-phenomena-poltergeist-seaford-case | phenomenon | 1961-05-05 | 18:21:00 UTC+0 | Phenomena: Poltergeist : Seaford case |
| ro-ufo-sighting-13666 | UFO sighting | 1961-05-07 | 04:30:00 UTC+10 | UFO Sighting 13666 |
| ro-ufo-sighting-13673 | UFO sighting | 1961-05-22 | 10:00:00 UTC-4.5 | UFO Sighting 13673 |
| ro-ufo-sighting-13678 | UFO sighting | 1961-06-03 | 18:35:00 UTC+1 | UFO Sighting 13678 |
| ro-ufo-sighting-13699 | UFO sighting | 1961-07-17 | 02:00:00 UTC-7 | UFO Sighting 13699 |
| ro-nature-earthquake-peru-brazil-border-reg-1961 | earthquake | 1961-08-19 | 05:10:00 UTC+0 | Nature:Earthquake Peru-Brazil (border reg.) 1961 |
| ro-ufo-sighting-13713 | UFO sighting | 1961-09-19 | 22:15:00 UTC-4 | UFO Sighting 13713 |
| ro-ufo-sighting-13715 | UFO sighting | 1961-10-02 | 12:00:00 UTC-7 | UFO Sighting 13715 |
| ro-celestial-seven-planets-and-node-in-aquarius | celestial | 1962-02-03 | 22:57:00 UTC+0 | Celestial: Seven planets and Node in Aquarius |
| ro-entertainment-pumuckl | entertainment | 1962-02-21 | 15:45:00 UTC+1 | Entertainment: Pumuckl |
| ro-ufo-sighting-13771 | UFO sighting | 1962-05-13 | 04:00:00 UTC-3 | UFO Sighting 13771 |
| ro-ufo-sighting-13798 | UFO sighting | 1962-08-16 | 23:55:00 UTC-3 | UFO Sighting 13798 |
| ro-ufo-sighting-13806 | UFO sighting | 1962-09-15 | 17:00:00 UTC-4 | UFO Sighting 13806 |
| ro-entertainment-the-jetsons | TV show | 1962-09-23 | 19:30:00 UTC-4 | Entertainment: The Jetsons |
| ro-entertainment-the-beverly-hillbillies | entertainment | 1962-09-26 | 21:00:00 UTC-4 | Entertainment: The Beverly Hillbillies |
| ro-ufo-sighting-13828 | UFO sighting | 1962-12-09 | 22:00:00 UTC+1 | UFO Sighting 13828 |
| ro-cities-chesapeake-va | city | 1963-01-01 | 00:00:00 UTC-5 | Cities: Chesapeake  VA; Cities: Virginia Beach  VA |
| ro-ufo-sighting-13837 | UFO sighting | 1963-01-04 | 19:00:00 UTC+1 | UFO Sighting 13837 |
| ro-entertainment-general-hospital | TV show | 1963-04-01 | 13:00:00 UTC-5 | Entertainment: General Hospital |
| ro-ufo-sighting-13882 | UFO sighting | 1963-07-02 | 20:30:00 UTC+1 | UFO Sighting 13882 |
| ro-ufo-sighting-13899 | UFO sighting | 1963-08-20 | 21:32:00 UTC+1 | UFO Sighting 13899 |
| ro-ufo-sighting-13909 | UFO sighting | 1963-09-10 | 22:00:00 UTC-5 | UFO Sighting 13909 |
| ro-terrorist-racial-bombing | terror attack | 1963-09-15 | 10:19:00 UTC-6 | Terrorist: Racial bombing |
| ro-entertainment-the-patty-duke-show | TV show | 1963-09-18 | 20:00:00 UTC-4 | Entertainment: The Patty Duke Show |
| ro-entertainment-my-favorite-martian | TV show | 1963-09-29 | 19:30:00 UTC-4 | Entertainment: My Favorite Martian |
| ro-nature-birth-of-surtsey-volcano | volcano | 1963-11-14 | 07:15:00 UTC-1 | Nature:Birth of Surtsey Volcano |
| ro-mortality-assassination-of-john-f-kennedy | assassination | 1963-11-22 | 12:30:00 UTC-6 | Mortality: Assassination of John F. Kennedy |
| ro-entertainment-doctor-who | TV show | 1963-11-23 | 17:16:00 UTC+0 | Entertainment: Doctor Who |
| ro-ufo-sighting-13942 | UFO sighting | 1963-12-27 | 16:00:00 UTC+0 | UFO Sighting 13942 |
| ro-plane-crash-eal-flight-304-1964 | air crash | 1964-02-25 | 02:06:00 UTC-6 | Plane Crash: EAL Flight 304 (1964) |
| ro-plane-crash-slick-airways-1964 | air crash | 1964-03-10 | 08:22:00 UTC-5 | Plane Crash: Slick Airways (1964) |
| ro-plane-crash-frontier-airlines-1964 | air crash | 1964-03-12 | 20:50:00 UTC-7 | Plane Crash: Frontier Airlines (1964) |
| ro-ufo-sighting-13967 | UFO sighting | 1964-04-03 | 21:00:00 UTC-6 | UFO Sighting 13967 |
| ro-ufo-sighting-13969 | UFO sighting | 1964-04-11 | 18:30:00 UTC-5 | UFO Sighting 13969 |
| ro-plane-crash-wein-alaska-airplane-1964 | air crash | 1964-04-17 | 15:14:00 UTC-11 | Plane Crash: Wein Alaska Airplane (1964) |
| ro-ufo-sighting-13975 | UFO sighting | 1964-04-24 | 10:00:00 UTC-5 | UFO Sighting 13975 |
| ro-ufo-sighting-13976 | UFO sighting | 1964-04-24 | 17:45:00 UTC-7 | UFO Sighting 13976 |
| ro-ufo-sighting-13979 | UFO sighting | 1964-04-26 | 12:30:00 UTC-7 | UFO Sighting 13979 |
| ro-entertainment-another-world | entertainment | 1964-05-04 | 15:00:00 UTC-4 | Entertainment: Another World |
| ro-entertainment-peyton-place | TV show | 1964-09-15 | 21:30:00 UTC-4 | Entertainment: Peyton Place |
| ro-entertainment-bewitched | entertainment | 1964-09-17 | 21:00:00 UTC-4 | Entertainment: Bewitched |
| ro-entertainment-the-addams-family-tv-series | TV show | 1964-09-18 | 20:30:00 UTC-4 | Entertainment: The Addams Family (TV series) |
| ro-entertainment-the-munsters | TV show | 1964-09-24 | 21:30:00 UTC-4 | Entertainment: The Munsters |
| ro-entertainment-gilligan-s-island | entertainment | 1964-09-26 | 20:30:00 UTC-4 | Entertainment: Gilligan's Island |
| ro-plane-crash-alaska-coastal-ellis-airlines-1965 | air crash | 1964-10-02 | 16:30:00 UTC-8 | Plane Crash: Alaska Coastal-Ellis Airlines (1965) |
| ro-sports-1964-summer-olympics-tokyo | sports event | 1964-10-10 | 14:51:00 UTC+9 | Sports: 1964 Summer Olympics, Tokyo |
| ro-plane-crash-bonanza-airlines-1964 | air crash | 1964-11-15 | 20:25:00 UTC-8 | Plane Crash: Bonanza Airlines (1964) |
| ro-plane-crash-twa-flight-800-1964 | air crash | 1964-11-23 | 14:15:00 UTC+1 | Plane Crash: TWA Flight 800 (1964) |
| ro-ufo-sighting-14023 | UFO sighting | 1964-11-25 | 00:45:00 UTC-5 | UFO Sighting 14023 |
| ro-nation-kenya | founding | 1964-12-12 | 00:00:00 UTC+3 | Nation: Kenya |
| ro-plane-crash-flying-tiger-line-1964 | air crash | 1964-12-24 | 00:31:00 UTC-8 | Plane Crash: Flying Tiger Line (1964) |
| ro-plane-crash-zantop-air-transport-1964 | air crash | 1964-12-30 | 02:14:00 UTC-5 | Plane Crash: Zantop Air Transport (1964) |
| ro-ufo-sighting-14031 | UFO sighting | 1965-01-04 | 17:15:00 UTC-5 | UFO Sighting 14031 |
| ro-ufo-sighting-14032 | UFO sighting | 1965-01-11 | 16:20:00 UTC-5 | UFO Sighting 14032 |
| ro-ufo-sighting-14033 | UFO sighting | 1965-01-12 | 20:20:00 UTC-8 | UFO Sighting 14033 |
| ro-nuclear-explosion-semipalatinsk | nuclear test | 1965-01-15 | 05:59:00 UTC+6 | Nuclear:Explosion Semipalatinsk |
| ro-ufo-sighting-14035 | UFO sighting | 1965-01-23 | 08:40:00 UTC-5 | UFO Sighting 14035 |
| ro-ufo-sighting-14046 | UFO sighting | 1965-03-02 | 13:55:00 UTC-5 | UFO Sighting 14046 |
| ro-ufo-sighting-14049 | UFO sighting | 1965-03-08 | 19:40:00 UTC-5 | UFO Sighting 14049 |
| ro-entertainment-the-odd-couple | entertainment | 1965-03-10 | 19:30:00 UTC-5 | Entertainment: The Odd Couple |
| ro-plane-crash-aaxico-airlines-flight-1422 | air crash | 1965-04-23 | 14:23:00 UTC-8 | Plane Crash: Aaxico Airlines Flight 1422 |
| ro-ufo-sighting-14056 | UFO sighting | 1965-04-23 | 08:00:00 UTC-5 | UFO Sighting 14056 |
| ro-ufo-sighting-14073 | UFO sighting | 1965-07-01 | 06:00:00 UTC+1 | UFO Sighting 14073 |
| ro-ufo-sighting-14074 | UFO sighting | 1965-07-03 | 23:40:00 UTC+0 | UFO Sighting 14074 |
| ro-ufo-sighting-14078 | UFO sighting | 1965-07-20 | 08:00:00 UTC-4 | UFO Sighting 14078 |
| ro-ufo-sighting-14080 | UFO sighting | 1965-07-26 | 20:00:00 UTC-3 | UFO Sighting 14080 |
| ro-ufo-sighting-14081 | UFO sighting | 1965-07-26 | 21:25:00 UTC+3 | UFO Sighting 14081 |
| ro-ufo-sighting-14084 | UFO sighting | 1965-08-09 | 18:00:00 UTC-4 | UFO Sighting 14084 |
| ro-ufo-sighting-14085 | UFO sighting | 1965-08-09 | 23:30:00 UTC-6 | UFO Sighting 14085 |
| ro-ufo-sighting-14086 | UFO sighting | 1965-08-13 | 07:00:00 UTC-7 | UFO Sighting 14086 |
| ro-ufo-sighting-14088 | UFO sighting | 1965-08-15 | 23:00:00 UTC-2 | UFO Sighting 14088 |
| ro-plane-crash-united-airlines-flight-389-1965 | air crash | 1965-08-16 | 20:21:00 UTC-5 | Plane Crash: United Airlines Flight 389 (1965) |
| ro-ufo-sighting-14090 | UFO sighting | 1965-08-20 | 11:50:00 UTC-5 | UFO Sighting 14090 |
| ro-ufo-sighting-14091 | UFO sighting | 1965-08-20 | 23:00:00 UTC-4 | UFO Sighting 14091 |
| ro-ufo-sighting-14092 | UFO sighting | 1965-08-25 | 10:10:00 UTC-5 | UFO Sighting 14092 |
| ro-ufo-sighting-14093 | UFO sighting | 1965-08-28 | 19:30:00 UTC-3 | UFO Sighting 14093 |
| ro-ufo-sighting-14095 | UFO sighting | 1965-09-01 | 05:00:00 UTC-5 | UFO Sighting 14095 |
| ro-ufo-sighting-14096 | UFO sighting | 1965-09-03 | 02:00:00 UTC-4 | UFO Sighting 14096 |
| ro-plane-crash-cordova-airlines-1964 | air crash | 1965-09-04 | 09:40:00 UTC-10 | Plane Crash: Cordova Airlines (1964) |
| ro-ufo-sighting-14099 | UFO sighting | 1965-09-08 | 22:00:00 UTC-5 | UFO Sighting 14099 |
| ro-ufo-sighting-14100 | UFO sighting | 1965-09-11 | 08:00:00 UTC-3 | UFO Sighting 14100 |
| ro-entertainment-f-troop | entertainment | 1965-09-14 | 21:00:00 UTC-4 | Entertainment: F Troop |
| ro-entertainment-lost-in-space | entertainment | 1965-09-15 | 19:30:00 UTC-4 | Entertainment: Lost in Space |
| ro-plane-crash-pan-am-flight-292-1965 | air crash | 1965-09-17 | 07:24:00 UTC-4 | Plane Crash: Pan Am Flight 292 (1965) |
| ro-ufo-sighting-14103 | UFO sighting | 1965-09-20 | 22:35:00 UTC+1 | UFO Sighting 14103 |
| ro-entertainment-days-of-our-lives | entertainment | 1965-11-08 | 14:00:00 UTC-5 | Entertainment: Days of Our Lives |
| ro-ufo-sighting-14112 | UFO sighting | 1965-11-09 | 17:58:00 UTC-5 | UFO Sighting 14112 |
| ro-plane-crash-united-airlines-flight-227-1965 | air crash | 1965-11-11 | 17:52:00 UTC-7 | Plane Crash: United Airlines Flight 227 (1965) |
| ro-plane-crash-collision-of-twa-42-vs-eal-853-1965 | air crash | 1965-12-04 | 16:18:00 UTC-5 | Plane Crash: Collision of TWA 42 vs. EAL 853 (1965 |
| ro-plane-crash-flying-tiger-line-flight-914-1965 | air crash | 1965-12-15 | 01:30:00 UTC-7 | Plane Crash: Flying Tiger Line Flight 914 (1965) |
| ro-synodic-uranus-plu-helio | celestial | 1966-01-07 | 09:32:00 UTC+0 | Synodic: Uranus-Plu Helio |
| ro-entertainment-batman-tv-series | TV show | 1966-01-12 | 19:30:00 UTC-5 | Entertainment: Batman (TV series) |
| ro-ufo-sighting-14120 | UFO sighting | 1966-01-14 | 17:55:00 UTC-5 | UFO Sighting 14120 |
| ro-ufo-sighting-14122 | UFO sighting | 1966-02-06 | 06:05:00 UTC-6 | UFO Sighting 14122 |
| ro-ufo-sighting-14123 | UFO sighting | 1966-02-06 | 20:00:00 UTC+1 | UFO Sighting 14123 |
| ro-ufo-sighting-14128 | UFO sighting | 1966-03-23 | 05:05:00 UTC-6 | UFO Sighting 14128 |
| ro-ufo-sighting-14131 | UFO sighting | 1966-03-31 | 06:00:00 UTC-8 | UFO Sighting 14131 |
| ro-ufo-sighting-14132 | UFO sighting | 1966-04-01 | 23:55:00 UTC-5 | UFO Sighting 14132 |
| ro-ufo-sighting-14136 | UFO sighting | 1966-04-17 | 05:05:00 UTC-5 | UFO Sighting 14136 |
| ro-plane-crash-american-flyers-flight-280-d-1966 | air crash | 1966-04-22 | 20:30:00 UTC-6 | Plane Crash: American Flyers Flight 280/D (1966) |
| ro-ufo-sighting-14138 | UFO sighting | 1966-04-22 | 21:00:00 UTC-5 | UFO Sighting 14138 |
| ro-ufo-sighting-14141 | UFO sighting | 1966-05-10 | 16:52:00 UTC-4 | UFO Sighting 14141 |
| ro-ufo-sighting-14142 | UFO sighting | 1966-05-10 | 22:00:00 UTC-3 | UFO Sighting 14142 |
| ro-plane-crash-zantop-air-transport-1966 | air crash | 1966-06-16 | 08:48:00 UTC-5 | Plane Crash: Zantop Air Transport (1966) |
| ro-entertainment-dark-shadows | TV show | 1966-06-27 | 16:00:00 UTC-4 | Entertainment: Dark Shadows |
| ro-business-launch-of-the-barclaycard | space flight | 1966-06-29 | 00:00:00 UTC+1 | Business: Launch of the Barclaycard |
| ro-synodic-uranus-pluto-geo | celestial | 1966-06-30 | 06:35:00 UTC+1 | Synodic: Uranus-Pluto Geo |
| ro-ufo-sighting-14151 | UFO sighting | 1966-07-22 | 23:30:00 UTC-5 | UFO Sighting 14151 |
| ro-ufo-sighting-14154 | UFO sighting | 1966-07-31 | 20:25:00 UTC-4 | UFO Sighting 14154 |
| ro-ufo-sighting-14155 | UFO sighting | 1966-08-17 | 18:30:00 UTC-3 | UFO Sighting 14155 |
| ro-plane-crash-alaska-coastal-airlines-1966 | air crash | 1966-08-21 | 10:35:00 UTC-8 | Plane Crash: Alaska Coastal Airlines (1966) |
| ro-entertainment-star-trek | entertainment | 1966-09-08 | 20:30:00 UTC-4 | Entertainment: Star Trek |
| ro-entertainment-mission-impossible | entertainment | 1966-09-17 | 21:00:00 UTC-4 | Entertainment: Mission: Impossible |
| ro-ufo-sighting-14163 | UFO sighting | 1966-09-22 | 03:00:00 UTC-7 | UFO Sighting 14163 |
| ro-ufo-sighting-14167 | UFO sighting | 1966-10-07 | 20:30:00 UTC-5 | UFO Sighting 14167 |
| ro-ufo-sighting-14168 | UFO sighting | 1966-10-10 | 17:20:00 UTC-5 | UFO Sighting 14168 |
| ro-accident-aberfan-mine-disaster | accident | 1966-10-21 | 09:15:00 UTC+1 | Accident: Aberfan mine disaster |
| ro-ufo-sighting-14171 | UFO sighting | 1966-11-02 | 19:25:00 UTC-5 | UFO Sighting 14171 |
| ro-plane-crash-pan-am-cargo-flight-1966 | air crash | 1966-11-15 | 02:42:00 UTC+1 | Plane Crash: Pan Am Cargo Flight (1966) |
| ro-ufo-sighting-14173 | UFO sighting | 1966-11-17 | 04:00:00 UTC-5 | UFO Sighting 14173 |
| ro-plane-crash-piedmont-airlines-1966 | air crash | 1966-11-20 | 06:06:00 UTC-5 | Plane Crash: Piedmont Airlines (1966) |
| ro-ufo-sighting-14177 | UFO sighting | 1966-11-22 | 16:20:00 UTC-5 | UFO Sighting 14177 |
| ro-plane-crash-flying-tiger-line-vietnam-1966 | air crash | 1966-12-24 | 19:15:00 UTC+7 | Plane Crash: Flying Tiger Line (Vietnam, 1966) |
| ro-ufo-sighting-14183 | UFO sighting | 1966-12-28 | 18:30:00 UTC-5 | UFO Sighting 14183 |
| ro-ufo-sighting-14186 | UFO sighting | 1967-01-13 | 22:00:00 UTC-7 | UFO Sighting 14186 |
| ro-ufo-sighting-14188 | UFO sighting | 1967-01-20 | 18:50:00 UTC-5 | UFO Sighting 14188 |
| ro-ufo-sighting-14189 | UFO sighting | 1967-01-25 | 04:30:00 UTC-6 | UFO Sighting 14189 |
| ro-accident-apollo-1-fire | fire | 1967-01-27 | 06:31:05 UTC-5 | Accident: Apollo 1 (Fire) |
| ro-ufo-sighting-14192 | UFO sighting | 1967-01-30 | 08:04:00 UTC-6 | UFO Sighting 14192 |
| ro-plane-crash-saturn-airways-kelly-afb-1967 | air crash | 1967-01-31 | 03:20:00 UTC-6 | Plane Crash: Saturn Airways (Kelly AFB, 1967) |
| ro-ufo-sighting-14194 | UFO sighting | 1967-02-25 | 19:50:00 UTC-6 | UFO Sighting 14194 |
| ro-plane-crash-lake-central-flight-527-1967 | air crash | 1967-03-05 | 20:07:00 UTC-5 | Plane Crash: Lake Central Flight 527 (1967) |
| ro-ufo-sighting-14196 | UFO sighting | 1967-03-08 | 01:05:00 UTC-5 | UFO Sighting 14196 |
| ro-ufo-sighting-14197 | UFO sighting | 1967-03-08 | 02:00:00 UTC-6 | UFO Sighting 14197 |
| ro-plane-crash-twa-flight-553-collision-1967 | air crash | 1967-03-09 | 11:54:00 UTC-5 | Plane Crash: TWA Flight 553 (collision, 1967) |
| ro-plane-crash-west-coast-flight-720-1967 | air crash | 1967-03-10 | 05:03:00 UTC-8 | Plane Crash: West Coast Flight 720 (1967) |
| ro-ufo-sighting-14203 | UFO sighting | 1967-03-20 | 22:45:00 UTC-5 | UFO Sighting 14203 |
| ro-plane-crash-delta-airlines-flight-9877-1967 | air crash | 1967-03-30 | 00:50:00 UTC-6 | Plane Crash: Delta Airlines Flight 9877 (1967) |
| ro-ufo-sighting-14207 | UFO sighting | 1967-04-06 | 12:45:00 UTC-6 | UFO Sighting 14207 |
| ro-ufo-sighting-14208 | UFO sighting | 1967-04-07 | 20:00:00 UTC+10 | UFO Sighting 14208 |
| ro-aviation-boeing-737-maiden-flight | aviation | 1967-04-09 | 13:15:00 UTC-8 | Aviation: Boeing 737 Maiden Flight |
| ro-ufo-sighting-14209 | UFO sighting | 1967-04-17 | 21:00:00 UTC-6 | UFO Sighting 14209 |
| ro-ufo-sighting-14210 | UFO sighting | 1967-04-21 | 01:00:00 UTC-8 | UFO Sighting 14210 |
| ro-ufo-sighting-14216 | UFO sighting | 1967-06-01 | 20:20:00 UTC+1 | UFO Sighting 14216 |
| ro-ufo-sighting-14218 | UFO sighting | 1967-06-07 | 01:30:00 UTC-3 | UFO Sighting 14218 |
| ro-ufo-sighting-14219 | UFO sighting | 1967-06-18 | 23:00:00 UTC-5 | UFO Sighting 14219 |
| ro-plane-crash-mohawk-airlines-flight-40-1967 | air crash | 1967-06-23 | 13:47:00 UTC-4 | Plane Crash: Mohawk Airlines Flight 40 (1967) |
| ro-ufo-sighting-14222 | UFO sighting | 1967-07-07 | 23:30:00 UTC+2 | UFO Sighting 14222 |
| ro-plane-crash-piedmont-airlines-flight-22-1967 | air crash | 1967-07-19 | 11:01:00 UTC-4 | Plane Crash: Piedmont Airlines Flight 22 (1967) |
| ro-ufo-sighting-14226 | UFO sighting | 1967-08-03 | 23:30:00 UTC-4 | UFO Sighting 14226 |
| ro-ufo-sighting-14227 | UFO sighting | 1967-08-07 | 02:00:00 UTC-4 | UFO Sighting 14227 |
| ro-ufo-sighting-14229 | UFO sighting | 1967-08-22 | 10:30:00 UTC+1 | UFO Sighting 14229 |
| ro-ufo-sighting-14230 | UFO sighting | 1967-08-24 | 17:00:00 UTC+10 | UFO Sighting 14230 |
| ro-ufo-sighting-14235 | UFO sighting | 1967-08-26 | 02:00:00 UTC-4 | UFO Sighting 14235 |
| ro-ufo-sighting-14237 | UFO sighting | 1967-08-29 | 10:30:00 UTC+1 | UFO Sighting 14237 |
| ro-ufo-sighting-14238 | UFO sighting | 1967-09-04 | 05:10:00 UTC-4 | UFO Sighting 14238 |
| ro-ufo-sighting-14239 | UFO sighting | 1967-09-08 | 02:30:00 UTC-4 | UFO Sighting 14239 |
| ro-ufo-sighting-14241 | UFO sighting | 1967-09-14 | 11:00:00 UTC-3 | UFO Sighting 14241 |
| ro-ufo-sighting-14243 | UFO sighting | 1967-09-15 | 20:45:00 UTC-4 | UFO Sighting 14243 |
| ro-ufo-sighting-14245 | UFO sighting | 1967-09-30 | 19:00:00 UTC+9 | UFO Sighting 14245 |
| ro-ufo-sighting-14247 | UFO sighting | 1967-10-06 | 22:00:00 UTC+1 | UFO Sighting 14247 |
| ro-ufo-sighting-14249 | UFO sighting | 1967-10-14 | 02:30:00 UTC-7 | UFO Sighting 14249 |
| ro-entertainment-hair | entertainment | 1967-10-17 | 20:30:00 UTC-4 | Entertainment: Hair |
| ro-ufo-sighting-14252 | UFO sighting | 1967-10-21 | 06:16:00 UTC-5 | UFO Sighting 14252 |
| ro-ufo-sighting-14253 | UFO sighting | 1967-10-21 | 22:00:00 UTC-5 | UFO Sighting 14253 |
| ro-ufo-sighting-14254 | UFO sighting | 1967-10-27 | 03:05:00 UTC-5 | UFO Sighting 14254 |
| ro-plane-crash-twa-flight-159-1967 | air crash | 1967-11-06 | 18:41:00 UTC-5 | Plane Crash: TWA Flight 159 (1967) |
| ro-ufo-sighting-14260 | UFO sighting | 1967-11-19 | 17:45:00 UTC-7 | UFO Sighting 14260 |
| ro-ufo-sighting-14261 | UFO sighting | 1967-11-20 | 13:00:00 UTC+1 | UFO Sighting 14261 |
| ro-ufo-sighting-14262 | UFO sighting | 1967-11-21 | 14:00:00 UTC+2 | UFO Sighting 14262 |
| ro-ufo-sighting-14265 | UFO sighting | 1967-11-24 | 14:30:00 UTC-2 | UFO Sighting 14265 |
| ro-ufo-sighting-14267 | UFO sighting | 1967-12-03 | 02:30:00 UTC-6 | UFO Sighting 14267 |
| ro-accident-plane-crash-14268 | air crash | 1967-12-21 | 16:00:00 UTC-7 | Accident: Plane Crash 14268 |
| ro-ufo-sighting-14269 | UFO sighting | 1967-12-24 | 20:30:00 UTC-5 | UFO Sighting 14269 |
| ro-ufo-sighting-14273 | UFO sighting | 1968-01-15 | 07:25:00 UTC-7 | UFO Sighting 14273 |
| ro-ufo-sighting-14278 | UFO sighting | 1968-03-04 | 20:10:00 UTC-6 | UFO Sighting 14278 |
| ro-plane-crash-ozark-air-lines-1968 | air crash | 1968-03-27 | 17:57:00 UTC-6 | Plane Crash: Ozark Air Lines (1968) |
| ro-ufo-sighting-14280 | UFO sighting | 1968-03-29 | 06:10:00 UTC+2 | UFO Sighting 14280 |
| ro-ufo-sighting-14281 | UFO sighting | 1968-04-01 | 22:45:00 UTC-5 | UFO Sighting 14281 |
| ro-ufo-sighting-14285 | UFO sighting | 1968-05-03 | 00:10:00 UTC-4 | UFO Sighting 14285 |
| ro-ufo-sighting-14286 | UFO sighting | 1968-05-05 | 20:35:00 UTC+2 | UFO Sighting 14286 |
| ro-ufo-sighting-14288 | UFO sighting | 1968-05-17 | 20:45:00 UTC-3 | UFO Sighting 14288 |
| ro-plane-crash-los-angeles-airways-flight-841-1968 | air crash | 1968-05-22 | 16:51:00 UTC-7 | Plane Crash: Los Angeles Airways Flight 841 (1968) |
| ro-ufo-sighting-14292 | UFO sighting | 1968-05-29 | 22:00:00 UTC-5 | UFO Sighting 14292 |
| ro-plane-crash-pan-am-flight-1-calcutta-1968 | air crash | 1968-06-12 | 00:58:00 UTC+5.5 | Plane Crash: Pan Am Flight 1 Calcutta (1968) |
| ro-ufo-sighting-14297 | UFO sighting | 1968-07-01 | 12:30:00 UTC-3 | UFO Sighting 14297 |
| ro-entertainment-one-life-to-live | TV show | 1968-07-15 | 15:30:00 UTC-4 | Entertainment: One Life to Live |
| ro-ufo-sighting-14298 | UFO sighting | 1968-07-22 | 20:45:00 UTC-3 | UFO Sighting 14298 |
| ro-ufo-sighting-14300 | UFO sighting | 1968-07-31 | 09:00:00 UTC+4 | UFO Sighting 14300 |
| ro-plane-crash-north-central-flight-261-1968 | air crash | 1968-08-04 | 08:48:00 UTC-5 | Plane Crash: North Central, Flight 261 (1968) |
| ro-ufo-sighting-14303 | UFO sighting | 1968-08-04 | 04:15:00 UTC-6 | UFO Sighting 14303 |
| ro-plane-crash-piedmont-airlines-flight-230-1968 | air crash | 1968-08-10 | 07:57:00 UTC-4 | Plane Crash: Piedmont Airlines Flight 230 (1968) |
| ro-plane-crash-los-angeles-airways-flight-417-1968 | air crash | 1968-08-14 | 09:35:00 UTC-7 | Plane Crash: Los Angeles Airways Flight 417 (1968) |
| ro-ufo-sighting-14308 | UFO sighting | 1968-08-16 | 06:00:00 UTC+1 | UFO Sighting 14308 |
| ro-ufo-sighting-14309 | UFO sighting | 1968-08-18 | 13:23:00 UTC+2 | UFO Sighting 14309 |
| ro-ufo-sighting-14310 | UFO sighting | 1968-08-20 | 21:50:00 UTC+2 | UFO Sighting 14310 |
| ro-ufo-sighting-14312 | UFO sighting | 1968-08-25 | 04:30:00 UTC-3 | UFO Sighting 14312 |
| ro-ufo-sighting-14313 | UFO sighting | 1968-09-11 | 23:45:00 UTC+1 | UFO Sighting 14313 |
| ro-ufo-sighting-14316 | UFO sighting | 1968-09-17 | 01:00:00 UTC-7 | UFO Sighting 14316 |
| ro-ufo-sighting-14317 | UFO sighting | 1968-09-21 | 02:00:00 UTC+1 | UFO Sighting 14317 |
| ro-ufo-sighting-14318 | UFO sighting | 1968-09-21 | 03:00:00 UTC+1 | UFO Sighting 14318 |
| ro-ufo-sighting-14320 | UFO sighting | 1968-09-24 | 21:00:00 UTC+1 | UFO Sighting 14320 |
| ro-cities-jacksonville-fl-con | city | 1968-10-01 | 09:15:00 UTC-4 | Cities: Jacksonville FL (con) |
| ro-tlatelolco-massacre | terror attack | 1968-10-02 | 18:15:00 UTC-6 | Tlatelolco Massacre |
| ro-ufo-sighting-14322 | UFO sighting | 1968-10-02 | 06:10:00 UTC-3 | UFO Sighting 14322 |
| ro-space-apollo-7-launch | space flight | 1968-10-11 | 11:02:45 UTC-4 | Space: Apollo 7 (Launch) |
| ro-ufo-sighting-14330 | UFO sighting | 1968-10-18 | 16:15:00 UTC+1 | UFO Sighting 14330 |
| ro-plane-crash-14333 | air crash | 1968-10-25 | 17:17:00 UTC-4 | Plane Crash 14333 |
| ro-ufo-sighting-14335 | UFO sighting | 1968-11-16 | 21:00:00 UTC-3 | UFO Sighting 14335 |
| ro-ufo-sighting-14338 | UFO sighting | 1968-11-19 | 18:30:00 UTC-3 | UFO Sighting 14338 |
| ro-ufo-sighting-14340 | UFO sighting | 1968-11-26 | 17:40:00 UTC-6 | UFO Sighting 14340 |
| ro-ufo-sighting-14342 | UFO sighting | 1968-11-27 | 19:00:00 UTC-6 | UFO Sighting 14342 |
| ro-plane-crash-pan-am-flight-217-1968 | air crash | 1968-12-12 | 22:02:00 UTC-4 | Plane Crash: Pan Am Flight 217 (1968) |
| ro-space-apollo-8-launch | space flight | 1968-12-21 | 07:51:00 UTC-5 | Space: Apollo 8 (Launch) |
| ro-plane-crash-allegheny-airlines-flight-736-1968 | air crash | 1968-12-24 | 20:12:00 UTC-5 | Plane Crash: Allegheny Airlines Flight 736 (1968) |
| ro-plane-crash-pan-am-cargo-flight-dec-26-1968 | air crash | 1968-12-26 | 06:15:00 UTC-10 | Plane Crash: Pan Am Cargo Flight (Dec 26, 1968) |
| ro-ufo-sighting-14351 | UFO sighting | 1968-12-26 | 21:00:00 UTC-3 | UFO Sighting 14351 |
| ro-plane-crash-north-central-flight-458-19 | air crash | 1968-12-27 | 20:22:00 UTC-6 | Plane Crash: North Central Flight 458 (19 |
| ro-plane-crash-allegheny-airlines-flight-737-1969 | air crash | 1969-01-06 | 20:35:00 UTC-5 | Plane Crash: Allegheny Airlines Flight 737 (1969) |
| ro-ufo-sighting-14355 | UFO sighting | 1969-01-06 | 20:30:00 UTC+1 | UFO Sighting 14355 |
| ro-ufo-sighting-14360 | UFO sighting | 1969-01-16 | 20:30:00 UTC+1 | UFO Sighting 14360 |
| ro-plane-crash-united-airlines-flight-266-1969 | air crash | 1969-01-18 | 18:21:00 UTC-8 | Plane Crash: United Airlines Flight 266 (1969) |
| ro-ufo-sighting-14362 | UFO sighting | 1969-01-23 | 22:30:00 UTC-3 | UFO Sighting 14362 |
| ro-ufo-sighting-14363 | UFO sighting | 1969-01-26 | 21:22:00 UTC-3 | UFO Sighting 14363 |
| ro-ufo-sighting-14365 | UFO sighting | 1969-01-31 | 22:00:00 UTC-3 | UFO Sighting 14365 |
| ro-ufo-sighting-14366 | UFO sighting | 1969-02-06 | 07:30:00 UTC-3 | UFO Sighting 14366 |
| ro-ufo-sighting-14367 | UFO sighting | 1969-02-08 | 21:05:00 UTC-3 | UFO Sighting 14367 |
| ro-ufo-sighting-14368 | UFO sighting | 1969-02-10 | 21:00:00 UTC-3 | UFO Sighting 14368 |
| ro-ufo-sighting-14369 | UFO sighting | 1969-02-12 | 05:40:00 UTC-3 | UFO Sighting 14369 |
| ro-ufo-sighting-14370 | UFO sighting | 1969-02-16 | 21:00:00 UTC-3 | UFO Sighting 14370 |
| ro-ufo-sighting-14371 | UFO sighting | 1969-02-17 | 21:15:00 UTC-3 | UFO Sighting 14371 |
| ro-ufo-sighting-14373 | UFO sighting | 1969-02-28 | 02:45:00 UTC+1 | UFO Sighting 14373 |
| ro-aviation-concorde-maiden-flight | aviation | 1969-03-02 | 15:40:00 UTC+1 | Aviation: Concorde Maiden Flight |
| ro-plane-crash-wien-consolidated-airlines-1969 | air crash | 1969-03-13 | 15:52:00 UTC-10 | Plane Crash: Wien Consolidated Airlines (1969) |
| ro-celestial-uranus-cycle | celestial | 1969-03-26 | 18:20:00 UTC-5 | Celestial: Uranus Cycle |
| ro-astrology-p-a-i | organization | 1969-03-29 | 12:44:00 UTC-8 | Astrology: P.A.I. |
| ro-ufo-sighting-14382 | UFO sighting | 1969-05-22 | 21:15:00 UTC-3 | UFO Sighting 14382 |
| ro-ufo-sighting-14383 | UFO sighting | 1969-05-23 | 21:55:00 UTC+2 | UFO Sighting 14383 |
| ro-ufo-sighting-14384 | UFO sighting | 1969-06-01 | 02:26:00 UTC+2 | UFO Sighting 14384 |
| ro-ufo-sighting-14392 | UFO sighting | 1969-07-12 | 23:00:00 UTC-5 | UFO Sighting 14392 |
| ro-ufo-sighting-14393 | UFO sighting | 1969-07-13 | 03:30:00 UTC-4 | UFO Sighting 14393 |
| ro-plane-crash-new-york-airways-1969 | air crash | 1969-07-15 | 06:57:00 UTC-4 | Plane Crash: New York Airways (1969) |
| ro-space-apollo-11-launch | space flight | 1969-07-16 | 09:32:00 UTC-4 | Space: Apollo 11 (Launch) |
| ro-space-moon-landing | space flight | 1969-07-20 | 15:17:40 UTC-5 | Space: Moon Landing |
| ro-space-first-step-on-moon | space flight | 1969-07-20 | 21:56:00 UTC-5 | Space: First step on Moon |
| ro-plane-crash-twa-training-flight-1969 | air crash | 1969-07-26 | 12:33:00 UTC-4 | Plane Crash: TWA Training Flight (1969) |
| ro-plane-crash-14398 | air crash | 1969-08-03 | 15:45:00 UTC-5 | Plane Crash 14398 |
| ro-plane-crash-allegheny-airlines-flight-853-1969 | air crash | 1969-09-09 | 14:29:00 UTC-4 | Plane Crash: Allegheny Airlines Flight 853 (1969) |
| ro-celestial-67p-churyumov-gerasimenko-comet | celestial | 1969-09-11 | 22:04:48 UTC+0 | Celestial: 67P/Churyumov-Gerasimenko (Comet) |
| ro-entertainment-the-brady-bunch | TV show | 1969-09-26 | 20:00:00 UTC-4 | Entertainment: The Brady Bunch |
| ro-nature-murchison-meteorite | meteor | 1969-09-28 | 10:58:00 UTC+10 | Nature: Murchison meteorite |
| ro-entertainment-monty-python-s-flying-circus | TV show | 1969-10-05 | 22:55:00 UTC+1 | Entertainment: Monty Python's Flying Circus |
| ro-entertainment-sesame-street | entertainment | 1969-11-10 | 11:30:00 UTC-5 | Entertainment: Sesame Street |
| ro-space-apollo-12-launch | space flight | 1969-11-14 | 11:22:00 UTC-5 | Space: Apollo 12 (Launch) |
| ro-plane-crash-mohawk-airlines-flight-411-1969 | air crash | 1969-11-19 | 20:20:00 UTC-5 | Plane Crash: Mohawk Airlines Flight 411 (1969) |
| ro-entertainment-all-my-children | entertainment | 1970-01-05 | 13:00:00 UTC-5 | Entertainment: All My Children |
| ro-ufo-sighting-14424 | UFO sighting | 1970-02-25 | 22:45:00 UTC-3 | UFO Sighting 14424 |
| ro-space-apollo-13-launch | space flight | 1970-04-11 | 13:13:00 UTC-5 | Space: Apollo 13 (Launch) |
| ro-ufo-sighting-14434 | UFO sighting | 1970-05-06 | 20:30:00 UTC-3 | UFO Sighting 14434 |
| ro-ufo-sighting-14436 | UFO sighting | 1970-05-14 | 21:45:00 UTC-4 | UFO Sighting 14436 |
| ro-ufo-sighting-14443 | UFO sighting | 1970-07-11 | 20:23:00 UTC+1 | UFO Sighting 14443 |
| ro-plane-crash-flying-tiger-line-flight-45-1970 | air crash | 1970-07-27 | 11:36:00 UTC+9 | Plane Crash: Flying Tiger Line Flight 45 (1970) |
| ro-ufo-sighting-14447 | UFO sighting | 1970-07-29 | 22:30:00 UTC-3 | UFO Sighting 14447 |
| ro-aviation-mcdonnell-douglas-dc-10-maiden-flight | aviation | 1970-08-19 | 10:00:00 UTC-7 | Aviation: McDonnell Douglas DC-10 (Maiden Flight) |
| ro-ufo-sighting-14453 | UFO sighting | 1970-08-30 | 21:10:00 UTC-3 | UFO Sighting 14453 |
| ro-plane-crash-trans-international-flight-863-1970 | air crash | 1970-09-08 | 16:06:00 UTC-4 | Plane Crash: Trans International Flight 863 (1970) |
| ro-entertainment-the-mary-tyler-moore-show | entertainment | 1970-09-19 | 21:30:00 UTC-4 | Entertainment: The Mary Tyler Moore Show |
| ro-entertainment-the-partridge-family | TV show | 1970-09-25 | 20:30:00 UTC-4 | Entertainment: The Partridge Family |
| ro-plane-crash-saturn-airways-1970 | air crash | 1970-10-10 | 21:30:00 UTC-4 | Plane Crash: Saturn Airways (1970) |
| ro-astrology-urania-trust | organization | 1970-11-09 | 00:00:00 UTC+1 | Astrology: Urania Trust |
| ro-plane-crash-southern-airways-flight-932-1970 | air crash | 1970-11-14 | 19:36:00 UTC-5 | Plane Crash: Southern Airways Flight 932 (1970) |
| ro-plane-crash-14467 | air crash | 1970-11-27 | 17:05:00 UTC-10 | Plane Crash 14467 |
| ro-plane-crash-twa-tel-aviv-1970 | air crash | 1970-11-30 | 02:55:00 UTC+2 | Plane Crash: TWA Tel Aviv (1970) |
| ro-mortality-1970-pioneer-hotel-fire-tucson | fire | 1970-12-20 | 00:21:00 UTC-7 | Mortality: 1970 Pioneer Hotel fire, Tucson |
| ro-plane-crash-trans-caribbean-flight-505-1970 | air crash | 1970-12-28 | 14:42:00 UTC-4 | Plane Crash: Trans Caribbean Flight 505 (1970) |
| ro-plane-crash-american-airlines-flight-30-1971 | air crash | 1971-01-09 | 16:20:00 UTC-5 | Plane Crash: American Airlines Flight 30 (1971) |
| ro-astrology-urania-trust-first-meeting | organization | 1971-01-26 | 18:33:00 UTC+1 | Astrology: Urania Trust, First Meeting |
| ro-space-apollo-14-launch | space flight | 1971-01-31 | 16:03:02 UTC-5 | Space: Apollo 14 (Launch) |
| ro-business-nasdaq | business | 1971-02-08 | 10:00:00 UTC-5 | Business: NASDAQ |
| ro-astrology-ncgr | organization | 1971-03-06 | 21:02:00 UTC-5 | Astrology: NCGR |
| ro-accident-fire-france | fire | 1971-03-13 | 23:45:00 UTC+1 | Accident: Fire, France |
| ro-plane-crash-western-airlines-flight-366-1971 | air crash | 1971-03-31 | 06:33:00 UTC-8 | Plane Crash: Western Airlines Flight 366 (1971) |
| ro-nature-etna-eruption-1971 | volcano | 1971-04-05 | 07:30:00 UTC+1 | Nature:Etna Eruption 1971 |
| ro-phenomena-the-fribourg-water-spook | phenomenon | 1971-04-25 | 17:00:00 UTC+1 | Phenomena:The Fribourg Water Spook |
| ro-plane-crash-hughes-airwest-flight-706-1971 | air crash | 1971-06-06 | 17:11:00 UTC-7 | Plane Crash: Hughes Airwest Flight 706 (1971) |
| ro-plane-crash-allegheny-airlines-flight-485-1971 | air crash | 1971-06-07 | 08:49:00 UTC-4 | Plane Crash: Allegheny Airlines Flight 485 (1971) |
| ro-ufo-sighting-14505 | UFO sighting | 1971-07-03 | 19:30:00 UTC-3 | UFO Sighting 14505 |
| ro-plane-crash-pan-am-flight-6005-1971 | air crash | 1971-07-25 | 13:21:00 UTC+8 | Plane Crash: Pan Am Flight 6005 (1971) |
| ro-space-apollo-15-launch | space flight | 1971-07-26 | 09:34:00 UTC-4 | Space: Apollo 15 (Launch) |
| ro-plane-crash-alaska-airlines-flight-1866-1971 | air crash | 1971-09-04 | 11:15:00 UTC-7 | Plane Crash: Alaska Airlines Flight 1866 (1971) |
| ro-ufo-sighting-14514 | UFO sighting | 1971-09-07 | 21:30:00 UTC-3 | UFO Sighting 14514 |
| ro-nature-kilauea-eruption-1971 | volcano | 1971-09-24 | 19:30:00 UTC-10 | Nature:Kilauea, eruption 1971 |
| ro-ufo-sighting-14517 | UFO sighting | 1971-09-26 | 18:58:00 UTC+8 | UFO Sighting 14517 |
| ro-ufo-sighting-14519 | UFO sighting | 1971-10-01 | 19:50:00 UTC-3 | UFO Sighting 14519 |
| ro-ufo-sighting-14521 | UFO sighting | 1971-10-16 | 14:00:00 UTC+8 | UFO Sighting 14521 |
| ro-plane-crash-eastern-airlines-vs-private-1971 | air crash | 1971-12-04 | 13:46:00 UTC-5 | Plane Crash: Eastern Airlines vs. private (1971) |
| ro-ufo-sighting-14524 | UFO sighting | 1971-12-19 | 21:00:00 UTC-3 | UFO Sighting 14524 |
| ro-ufo-sighting-14525 | UFO sighting | 1971-12-23 | 21:30:00 UTC+2 | UFO Sighting 14525 |
| ro-ufo-sighting-14527 | UFO sighting | 1971-12-29 | 01:15:00 UTC-3 | UFO Sighting 14527 |
| ro-ufo-sighting-14528 | UFO sighting | 1972-01-03 | 19:15:00 UTC+2 | UFO Sighting 14528 |
| ro-ufo-sighting-14529 | UFO sighting | 1972-01-03 | 19:23:00 UTC+2 | UFO Sighting 14529 |
| ro-ufo-sighting-14530 | UFO sighting | 1972-01-03 | 19:40:00 UTC+2 | UFO Sighting 14530 |
| ro-ufo-sighting-14531 | UFO sighting | 1972-01-03 | 19:41:00 UTC+2 | UFO Sighting 14531 |
| ro-ufo-sighting-14532 | UFO sighting | 1972-01-03 | 19:43:00 UTC+2 | UFO Sighting 14532 |
| ro-ufo-sighting-14533 | UFO sighting | 1972-01-03 | 20:25:00 UTC+2 | UFO Sighting 14533 |
| ro-ufo-sighting-14534 | UFO sighting | 1972-01-05 | 17:20:00 UTC+2 | UFO Sighting 14534 |
| ro-ufo-sighting-14535 | UFO sighting | 1972-01-05 | 20:40:00 UTC+2 | UFO Sighting 14535 |
| ro-ufo-sighting-14536 | UFO sighting | 1972-01-05 | 21:35:00 UTC+2 | UFO Sighting 14536 |
| ro-ufo-sighting-14537 | UFO sighting | 1972-01-16 | 21:00:00 UTC-3 | UFO Sighting 14537 |
| ro-historic-nantes-cathedral-fire-1972 | fire | 1972-01-28 | 16:18:00 UTC+1 | Historic: Nantes Cathedral fire 1972 |
| ro-plane-crash-mohawk-airlines-flight-405-1972 | air crash | 1972-03-03 | 20:48:00 UTC-5 | Plane Crash: Mohawk Airlines Flight 405 (1972) |
| ro-entertainment-number-96 | TV show | 1972-03-13 | 20:30:00 UTC+10 | Entertainment: Number 96 |
| ro-space-apollo-16-launch | space flight | 1972-04-16 | 12:54:00 UTC-5 | Space: Apollo 16 (Launch) |
| ro-ufo-sighting-14551 | UFO sighting | 1972-05-21 | 11:25:00 UTC-3 | UFO Sighting 14551 |
| ro-opryland | business | 1972-05-27 | 10:00:00 UTC-5 | Opryland |
| ro-plane-crash-delta-airlines-flight-9570-1972 | air crash | 1972-05-30 | 06:24:00 UTC-5 | Plane Crash: Delta Airlines Flight 9570 (1972) |
| ro-plane-crash-lake-winnebago-collision-1972 | air crash | 1972-06-29 | 10:37:00 UTC-5 | Plane Crash: Lake Winnebago collision (1972) |
| ro-ufo-sighting-14563 | UFO sighting | 1972-08-18 | 21:30:00 UTC-3 | UFO Sighting 14563 |
| ro-sports-1972-summer-olympics-munich | sports event | 1972-08-26 | 16:25:00 UTC+1 | Sports: 1972 Summer Olympics, Munich |
| ro-entertainment-m-a-s-h | entertainment | 1972-09-17 | 20:00:00 UTC-4 | Entertainment: M*A*S*H |
| ro-space-apollo-17-launch | space flight | 1972-12-07 | 00:33:00 UTC-5 | Space: Apollo 17 (Launch) |
| ro-plane-crash-united-airlines-flight-553-1972 | air crash | 1972-12-08 | 14:28:00 UTC-6 | Plane Crash: United Airlines Flight 553 (1972) |
| ro-plane-crash-delta-954-vs-north-central-575-1972 | air crash | 1972-12-20 | 18:00:00 UTC-6 | Plane Crash: Delta 954 vs. North Central 575 (1972 |
| ro-plane-crash-eastern-air-lines-flight-401-1972 | air crash | 1972-12-29 | 23:42:00 UTC-5 | Plane Crash: Eastern Air Lines Flight 401 (1972) |
| ro-entertainment-an-american-family | TV show | 1973-01-11 | 21:00:00 UTC-5 | Entertainment: An American Family |
| ro-law-roe-v-wade | law | 1973-01-22 | 10:00:00 UTC-5 | Law: Roe v. Wade |
| ro-nature-heimaey-eruption | volcano | 1973-01-23 | 02:00:00 UTC+0 | Nature:Heimaey Eruption |
| ro-entertainment-the-young-and-the-restless | TV show | 1973-03-26 | 12:00:00 UTC-5 | Entertainment: The Young and the Restless |
| ro-historic-world-trade-center | historic | 1973-04-04 | 15:00:00 UTC-5 | Historic: World Trade Center |
| ro-astrology-irish-astrological-association | organization | 1973-05-05 | 19:08:00 UTC+1 | Astrology: Irish Astrological Association |
| ro-space-skylab-space-station | space flight | 1973-05-14 | 01:30:00 UTC-4 | Space: Skylab (space station) |
| ro-ufo-sighting-14585 | UFO sighting | 1973-05-17 | 15:00:00 UTC-3 | UFO Sighting 14585 |
| ro-plane-crash-pan-am-flight-816-1973 | air crash | 1973-07-22 | 22:07:00 UTC-10 | Plane Crash: Pan Am Flight 816 (1973) |
| ro-plane-crash-ozark-air-lines-flight-809-1973 | air crash | 1973-07-23 | 17:43:00 UTC-5 | Plane Crash: Ozark Air Lines Flight 809 (1973) |
| ro-plane-crash-delta-air-lines-flight-723-1973 | air crash | 1973-07-31 | 11:08:00 UTC-4 | Plane Crash: Delta Air Lines Flight 723 (1973) |
| ro-entertainment-hip-hop | entertainment | 1973-08-11 | 21:00:00 UTC-4 | Entertainment: Hip Hop |
| ro-plane-crash-world-airways-flight-802-1973 | air crash | 1973-09-08 | 05:42:00 UTC-10 | Plane Crash: World Airways Flight 802 (1973) |
| ro-ufo-sighting-14597 | UFO sighting | 1973-09-14 | 19:30:00 UTC+8 | UFO Sighting 14597 |
| ro-plane-crash-texas-international-flight-655-1973 | air crash | 1973-09-27 | 19:52:00 UTC-5 | Plane Crash: Texas International Flight 655 (1973) |
| ro-ufo-sighting-14602 | UFO sighting | 1973-10-06 | 11:30:00 UTC-4 | UFO Sighting 14602 |
| ro-ufo-sighting-14603 | UFO sighting | 1973-10-11 | 19:00:00 UTC-5 | UFO Sighting 14603 |
| ro-historic-sydney-opera-house | historic | 1973-10-20 | 15:00:00 UTC+10 | Historic: Sydney Opera House |
| ro-ufo-sighting-14604 | UFO sighting | 1973-10-28 | 01:15:00 UTC-3 | UFO Sighting 14604 |
| ro-plane-crash-pan-am-flight-160-1973 | air crash | 1973-11-03 | 09:40:00 UTC-5 | Plane Crash: Pan Am Flight 160 (1973) |
| ro-entertainment-the-paul-hogan-show | entertainment | 1973-11-04 | 19:30:00 UTC+11 | Entertainment: The Paul Hogan Show |
| ro-entertainment-happy-days | entertainment | 1974-01-15 | 20:00:00 UTC-4 | Entertainment: Happy Days |
| ro-entertainment-the-box | TV show | 1974-02-11 | 21:00:00 UTC+11 | Entertainment: The Box |
| ro-plane-crash-turkish-airlines-flight-981-1974 | air crash | 1974-03-03 | 12:41:00 UTC+1 | Plane Crash: Turkish Airlines Flight 981 (1974) |
| ro-ufo-sighting-14618 | UFO sighting | 1974-03-29 | 04:00:00 UTC-3 | UFO Sighting 14618 |
| ro-ufo-sighting-14619 | UFO sighting | 1974-04-14 | 04:00:00 UTC-2 | UFO Sighting 14619 |
| ro-astrology-mercury-hour | organization | 1974-04-17 | 12:20:00 UTC-4 | Astrology: Mercury Hour |
| ro-plane-crash-pan-am-flight-812-1974 | air crash | 1974-04-22 | 22:26:00 UTC+8 | Plane Crash: Pan Am Flight 812 (1974) |
| ro-plane-crash-aeroflot-leningrad-1974 | air crash | 1974-04-27 | 18:07:24 UTC+3 | Plane Crash: Aeroflot (Leningrad, 1974) |
| ro-terrorism-1974-dublin-and-monaghan-bombings | terror attack | 1974-05-17 | 17:28:00 UTC+1 | Terrorism: 1974 Dublin and Monaghan bombings |
| ro-ufo-sighting-14623 | UFO sighting | 1974-05-27 | 23:00:00 UTC-3 | UFO Sighting 14623 |
| ro-ufo-sighting-14624 | UFO sighting | 1974-06-20 | 22:00:00 UTC-3 | UFO Sighting 14624 |
| ro-ufo-sighting-14625 | UFO sighting | 1974-06-25 | 01:15:00 UTC-4 | UFO Sighting 14625 |
| ro-ufo-sighting-14627 | UFO sighting | 1974-08-12 | 20:45:00 UTC-3 | UFO Sighting 14627 |
| ro-entertainment-rhoda | TV show | 1974-09-09 | 21:30:00 UTC-4 | Entertainment: Rhoda |
| ro-entertainment-little-house-on-the-prairie | TV show | 1974-09-11 | 20:00:00 UTC-4 | Entertainment: Little House on the Prairie |
| ro-ufo-sighting-14631 | UFO sighting | 1974-11-08 | 01:50:00 UTC-3 | UFO Sighting 14631 |
| ro-ufo-sighting-14632 | UFO sighting | 1974-11-09 | 00:15:00 UTC-3 | UFO Sighting 14632 |
| ro-plane-crash-martinair-flight-138-1974 | air crash | 1974-12-04 | 22:11:00 UTC+5.5 | Plane Crash: Martinair Flight 138 (1974) |
| ro-ufo-sighting-14639 | UFO sighting | 1975-02-18 | 15:20:00 UTC-3 | UFO Sighting 14639 |
| ro-accident-moorgate-train-crash-london-underground | rail accident | 1975-02-28 | 08:46:00 UTC+0 | Accident: Moorgate Train Crash, London Underground |
| ro-plane-crash-eastern-air-lines-flight-66-1975 | air crash | 1975-06-24 | 16:05:00 UTC-4 | Plane Crash: Eastern Air Lines Flight 66 (1975) |
| ro-nature-eruption-tolbachik-1975 | volcano | 1975-07-06 | 09:45:00 UTC+12 | Nature:Eruption:Tolbachik (1975) |
| ro-ufo-sighting-14646 | UFO sighting | 1975-07-31 | 09:00:00 UTC+2 | UFO Sighting 14646 |
| ro-plane-crash-alia-royal-jordanian-airlines-1975 | air crash | 1975-08-03 | 04:25:00 UTC+0 | Plane Crash: Alia Royal Jordanian Airlines (1975) |
| ro-plane-crash-csa-flight-540-1975 | air crash | 1975-08-20 | 01:13:00 UTC+3 | Plane Crash: ČSA Flight 540 (1975) |
| ro-entertainment-saturday-night-live | TV show | 1975-10-11 | 23:30:00 UTC-4 | Entertainment: Saturday Night Live |
| ro-astrology-aquarius-workshops | organization | 1975-10-28 | 13:34:00 UTC-8 | Astrology: Aquarius Workshops |
| ro-ufo-sighting-14651 | UFO sighting | 1975-11-05 | 18:15:00 UTC-7 | UFO Sighting 14651 |
| ro-ufo-sighting-14655 | UFO sighting | 1976-01-06 | 23:30:00 UTC-5 | UFO Sighting 14655 |
| ro-aviation-concorde-first-commercial-flight | aviation | 1976-01-21 | 12:40:00 UTC+1 | Aviation: Concorde First commercial flight |
| ro-entertainment-laverne-and-shirley | entertainment | 1976-01-27 | 20:30:00 UTC-5 | Entertainment: Laverne and Shirley |
| ro-plane-crash-aeroflot-flight-909-1976 | air crash | 1976-03-06 | 00:58:00 UTC+3 | Plane Crash: Aeroflot Flight 909 (1976) |
| ro-entertainment-family | TV show | 1976-03-09 | 22:00:00 UTC-5 | Entertainment: Family |
| ro-ufo-sighting-14657 | UFO sighting | 1976-06-20 | 01:00:00 UTC-5 | UFO Sighting 14657 |
| ro-ufo-sighting-14658 | UFO sighting | 1976-06-23 | 23:50:00 UTC-3 | UFO Sighting 14658 |
| ro-accident-seveso-disaster | accident | 1976-07-10 | 12:37:00 UTC+2 | Accident: Seveso disaster |
| ro-sports-1976-summer-olympics-montreal | sports event | 1976-07-17 | 16:15:00 UTC-4 | Sports: 1976 Summer Olympics, Montréal |
| ro-ufo-sighting-14660 | UFO sighting | 1976-08-06 | 22:00:00 UTC-3 | UFO Sighting 14660 |
| ro-plane-crash-zagreb-mid-air-collision-1976 | air crash | 1976-09-10 | 10:15:00 UTC+1 | Plane Crash: Zagreb mid-air collision (1976) |
| ro-plane-crash-turkish-airlines-flight-452-1976 | air crash | 1976-09-19 | 23:15:00 UTC+3 | Plane Crash: Turkish Airlines Flight 452 (1976) |
| ro-entertainment-charlie-s-angels | TV show | 1976-09-22 | 22:00:00 UTC-4 | Entertainment: Charlie's Angels |
| ro-ufo-sighting-14670 | UFO sighting | 1976-10-22 | 21:30:00 UTC+0 | UFO Sighting 14670 |
| ro-entertainment-the-young-doctors | TV show | 1976-11-08 | 19:30:00 UTC+11 | Entertainment: The Young Doctors |
| ro-ufo-sighting-14673 | UFO sighting | 1976-11-12 | 02:00:00 UTC+1 | UFO Sighting 14673 |
| ro-entertainment-fantasy-island | TV show | 1977-01-14 | 21:00:00 UTC-5 | Entertainment: Fantasy Island |
| ro-entertainment-eight-is-enough | TV show | 1977-03-15 | 20:30:00 UTC-5 | Entertainment: Eight Is Enough |
| ro-entertainment-three-s-company | TV show | 1977-03-15 | 21:30:00 UTC-5 | Entertainment: Three's Company |
| ro-plane-crash-tenerife-airport-disaster-1977 | air crash | 1977-03-27 | 17:07:00 UTC+0 | Plane Crash: Tenerife Airport Disaster (1977) |
| ro-ufo-sighting-14684 | UFO sighting | 1977-04-09 | 09:00:00 UTC-6 | UFO Sighting 14684 |
| ro-ufo-sighting-14688 | UFO sighting | 1977-04-25 | 04:25:00 UTC-4 | UFO Sighting 14688 |
| ro-entertainment-star-wars | entertainment | 1977-05-25 | 10:45:00 UTC-4 | Entertainment: Star Wars |
| ro-space-voyager-2-space-probe | space flight | 1977-08-20 | 10:29:00 UTC-4 | Space: Voyager 2 (space probe) |
| ro-ufo-sighting-14697 | UFO sighting | 1977-08-30 | 00:15:00 UTC+2 | UFO Sighting 14697 |
| ro-space-voyager-1 | space flight | 1977-09-05 | 12:56:00 UTC+0 | Space: Voyager 1 |
| ro-entertainment-soap | TV show | 1977-09-13 | 21:30:00 UTC-4 | Entertainment: Soap |
| ro-ufo-sighting-14701 | UFO sighting | 1977-09-15 | 02:20:00 UTC-3 | UFO Sighting 14701 |
| ro-ufo-sighting-14702 | UFO sighting | 1977-09-20 | 04:00:00 UTC+3 | UFO Sighting 14702 |
| ro-celestial-chiron-discovery | celestial | 1977-11-01 | 10:00:00 UTC-8 | Celestial: Chiron Discovery |
| ro-ufo-sighting-14708 | UFO sighting | 1977-11-18 | 21:00:00 UTC-3 | UFO Sighting 14708 |
| ro-plane-crash-tap-air-portugal-flight-425-1977 | air crash | 1977-11-19 | 21:48:00 UTC+0 | Plane Crash: TAP Air Portugal Flight 425 (1977) |
| ro-plane-crash-malaysian-airline-flight-653-1977 | air crash | 1977-12-04 | 20:30:00 UTC+7.5 | Plane Crash: Malaysian Airline Flight 653 (1977) |
| ro-ufo-sighting-14711 | UFO sighting | 1978-02-04 | 05:00:00 UTC-3 | UFO Sighting 14711 |
| ro-ufo-sighting-14712 | UFO sighting | 1978-02-05 | 06:40:00 UTC+1 | UFO Sighting 14712 |
| ro-entertainment-dallas | entertainment | 1978-04-02 | 22:00:00 UTC-5 | Entertainment: Dallas |
| ro-ufo-sighting-14718 | UFO sighting | 1978-05-17 | 09:00:00 UTC+2 | UFO Sighting 14718 |
| ro-ufo-sighting-14724 | UFO sighting | 1978-06-11 | 23:45:00 UTC-3 | UFO Sighting 14724 |
| ro-ufo-sighting-14736 | UFO sighting | 1978-09-17 | 21:00:00 UTC+2 | UFO Sighting 14736 |
| ro-plane-crash-psa-flight-182-1978 | air crash | 1978-09-25 | 09:01:47 UTC-7 | Plane Crash: PSA Flight 182 (1978) |
| ro-ufo-sighting-14740 | UFO sighting | 1978-10-22 | 20:04:00 UTC+8 | UFO Sighting 14740 |
| ro-entertainment-diff-rent-strokes | entertainment | 1978-11-03 | 20:00:00 UTC-5 | Entertainment: Diff'rent Strokes |
| ro-nature-earthquake-solomon-islands-1978 | earthquake | 1978-11-04 | 22:29:36 UTC+0 | Nature:Earthquake Solomon Islands: 1978 |
| ro-ufo-sighting-14744 | UFO sighting | 1978-12-06 | 20:45:00 UTC-3 | UFO Sighting 14744 |
| ro-ufo-sighting-14745 | UFO sighting | 1978-12-06 | 23:45:00 UTC+1 | UFO Sighting 14745 |
| ro-plane-crash-alitalia-flight-4128-1978 | air crash | 1978-12-23 | 00:39:00 UTC+1 | Plane Crash: Alitalia Flight 4128 (1978) |
| ro-ufo-sighting-14746 | UFO sighting | 1978-12-31 | 23:00:00 UTC-3 | UFO Sighting 14746 |
| ro-jura-sovereignty | political | 1979-01-01 | 00:00:00 UTC+1 | Jura, sovereignty |
| ro-ufo-sighting-14747 | UFO sighting | 1979-01-03 | 23:50:00 UTC+2 | UFO Sighting 14747 |
| ro-disaster-betelgeuse-oil-tanker-explosion | explosion | 1979-01-08 | 00:55:00 UTC+0 | Disaster: Betelgeuse Oil Tanker Explosion |
| ro-entertainment-prisoner | TV show | 1979-02-27 | 20:30:00 UTC+11 | Entertainment: Prisoner |
| ro-ufo-sighting-14756 | UFO sighting | 1979-04-13 | 23:00:00 UTC-3 | UFO Sighting 14756 |
| ro-plane-crash-american-airlines-flight-191-1979 | air crash | 1979-05-25 | 15:04:00 UTC-5 | Plane Crash: American Airlines Flight 191 (1979) |
| ro-entertainment-alien | entertainment | 1979-05-25 | 10:00:00 UTC-4 | Entertainment: Alien |
| ro-ufo-sighting-14762 | UFO sighting | 1979-06-28 | 03:00:00 UTC-3 | UFO Sighting 14762 |
| ro-plane-crash-aeroflot-flight-7880-1979 | air crash | 1979-08-11 | 13:35:38 UTC+3 | Plane Crash: Aeroflot Flight 7880 (1979) |
| ro-ufo-sighting-14771 | UFO sighting | 1979-09-09 | 20:00:00 UTC-3 | UFO Sighting 14771 |
| ro-plane-crash-pia-flight-740-1979 | air crash | 1979-11-26 | 02:04:00 UTC+3 | Plane Crash: PIA Flight 740 (1979) |
| ro-plane-crash-air-new-zealand-flight-901-1979 | air crash | 1979-11-28 | 20:49:50 UTC+0 | Plane Crash: Air New Zealand Flight 901 (1979) |
| ro-ufo-sighting-14776 | UFO sighting | 1979-12-08 | 17:00:00 UTC-3 | UFO Sighting 14776 |
| ro-ufo-sighting-14778 | UFO sighting | 1979-12-30 | 07:40:00 UTC+8 | UFO Sighting 14778 |
| ro-plane-crash-iran-air-flight-291-1980 | air crash | 1980-01-21 | 19:11:00 UTC+3.5 | Plane Crash: Iran Air Flight 291 (1980) |
| ro-ufo-sighting-14782 | UFO sighting | 1980-02-03 | 16:30:00 UTC-3 | UFO Sighting 14782 |
| ro-ufo-sighting-14784 | UFO sighting | 1980-03-24 | 18:34:00 UTC+8 | UFO Sighting 14784 |
| ro-ufo-sighting-14786 | UFO sighting | 1980-04-09 | 03:25:00 UTC+8 | UFO Sighting 14786 |
| ro-plane-crash-dan-air-flight-1008-1980 | air crash | 1980-04-25 | 14:21:15 UTC+1 | Plane Crash: Dan-Air Flight 1008 (1980) |
| ro-ufo-sighting-14787 | UFO sighting | 1980-05-16 | 01:14:00 UTC+8 | UFO Sighting 14787 |
| ro-accident-ustica-affair | accident | 1980-06-27 | 20:59:00 UTC+2 | Accident: Ustica affair |
| ro-plane-crash-aeroflot-flight-4225-1980 | air crash | 1980-07-08 | 00:39:00 UTC+6 | Plane Crash: Aeroflot Flight 4225 (1980) |
| ro-plane-crash-saudia-flight-163-1980 | air crash | 1980-08-19 | 21:14:54 UTC+3 | Plane Crash: Saudia Flight 163 (1980) |
| ro-historic-p-e-t-a | historic | 1980-08-21 | 09:00:00 UTC-4 | Historic: P.E.T.A. |
| ro-astrology-apae | organization | 1980-09-07 | 18:37:00 UTC+1 | Astrology: APAE |
| ro-apple-shares | business | 1980-12-12 | 10:00:00 UTC-5 | Apple, Shares |
| ro-ufo-sighting-14805 | UFO sighting | 1980-12-14 | 17:34:00 UTC+8 | UFO Sighting 14805 |
| ro-ufo-sighting-14806 | UFO sighting | 1980-12-27 | 00:30:00 UTC+0 | UFO Sighting 14806 |
| ro-ufo-sighting-14807 | UFO sighting | 1980-12-29 | 23:45:00 UTC+0 | UFO Sighting 14807 |
| ro-entertainment-dynasty | entertainment | 1981-01-12 | 20:00:00 UTC-5 | Entertainment: Dynasty |
| ro-ufo-sighting-14809 | UFO sighting | 1981-02-19 | 08:20:00 UTC+8 | UFO Sighting 14809 |
| ro-celestial-saturn-cycle | celestial | 1981-03-30 | 18:31:00 UTC-5 | Celestial: Saturn Cycle |
| ro-space-columbia-sts-1 | space flight | 1981-04-12 | 07:00:00 UTC-5 | Space: Columbia STS-1 |
| ro-ufo-sighting-14818 | UFO sighting | 1981-07-24 | 22:37:00 UTC+8 | UFO Sighting 14818 |
| ro-entertainment-mtv | entertainment | 1981-08-01 | 00:01:00 UTC-4 | Entertainment: MTV |
| ro-plane-crash-far-eastern-flight-103-1981 | air crash | 1981-08-22 | 09:55:00 UTC+8 | Plane Crash: Far Eastern Flight 103 (1981) |
| ro-plane-crash-inex-adria-flight-1308-1981 | air crash | 1981-12-01 | 08:53:00 UTC+1 | Plane Crash: Inex-Adria Flight 1308 (1981) |
| ro-entertainment-falcon-crest | TV show | 1981-12-04 | 22:00:00 UTC-5 | Entertainment: Falcon Crest |
| ro-ufo-sighting-14829 | UFO sighting | 1982-01-02 | 23:30:00 UTC-3 | UFO Sighting 14829 |
| ro-entertainment-fame-tv-series | TV show | 1982-01-07 | 20:00:00 UTC-5 | Entertainment: Fame (TV series) |
| ro-entertainment-sons-and-daughters | TV show | 1982-01-18 | 19:00:00 UTC+11 | Entertainment: Sons and Daughters |
| ro-ufo-sighting-14831 | UFO sighting | 1982-02-04 | 03:05:00 UTC+3 | UFO Sighting 14831 |
| ro-ufo-sighting-14832 | UFO sighting | 1982-02-08 | 23:00:00 UTC-3 | UFO Sighting 14832 |
| ro-ufo-sighting-14833 | UFO sighting | 1982-02-09 | 03:12:00 UTC-3 | UFO Sighting 14833 |
| ro-ufo-sighting-14838 | UFO sighting | 1982-03-06 | 20:30:00 UTC-4 | UFO Sighting 14838 |
| ro-plane-crash-caac-flight-3303-1982 | air crash | 1982-04-26 | 16:40:00 UTC+8 | Plane Crash: CAAC Flight 3303 (1982) |
| ro-historic-sinking-of-general-belgrano | shipwreck | 1982-05-02 | 15:57:00 UTC-4 | Historic: Sinking of General Belgrano |
| ro-plane-crash-aeroflot-flight-8641-1982 | air crash | 1982-06-28 | 10:51:50 UTC+4 | Plane Crash: Aeroflot Flight 8641 (1982) |
| ro-plane-crash-pan-am-flight-759-1982 | air crash | 1982-07-09 | 16:08:00 UTC-5 | Plane Crash: Pan Am Flight 759 (1982) |
| ro-ufo-sighting-14857 | UFO sighting | 1982-08-07 | 04:40:00 UTC-3 | UFO Sighting 14857 |
| ro-nature-earthquake-costa-rica-panama-1982 | earthquake | 1982-08-19 | 15:59:03 UTC+0 | Nature:Earthquake Costa Rica/Panama: 1982 |
| ro-astrology-a-f-a-n | organization | 1982-08-31 | 23:51:00 UTC-5 | Astrology: A.F.A.N. |
| ro-ufo-sighting-14861 | UFO sighting | 1982-09-02 | 03:40:00 UTC-3 | UFO Sighting 14861 |
| ro-entertainment-family-ties | entertainment | 1982-09-22 | 21:30:00 UTC-4 | Entertainment: Family Ties |
| ro-entertainment-cheers | TV show | 1982-09-30 | 21:00:00 UTC-4 | Entertainment: Cheers |
| ro-synodic-saturn-pluto-cyc-geo | celestial | 1982-11-08 | 00:38:00 UTC+0 | Synodic: Saturn-Pluto Cyc. Geo |
| ro-ufo-sighting-14869 | UFO sighting | 1982-11-29 | 01:50:00 UTC-3 | UFO Sighting 14869 |
| ro-historic-lethal-injection | historic | 1982-12-06 | 00:09:00 UTC-6 | Historic: Lethal Injection |
| ro-synodic-sat-pluto-helio | celestial | 1982-12-24 | 05:58:00 UTC+0 | Synodic: Sat-Pluto Helio |
| ro-nature-volcano-hawaii | volcano | 1983-01-03 | 02:40:00 UTC-10 | Nature: Volcano Hawaii |
| ro-astrology-sab | organization | 1983-01-18 | 21:09:00 UTC+1 | Astrology: SAB |
| ro-medical-aids-discovery | other | 1983-02-04 | 17:45:00 UTC+1 | Medical: AIDS Discovery |
| ro-entertainment-red-hot-chili-peppers | entertainment | 1983-03-25 | 22:00:00 UTC-8 | Entertainment: Red Hot Chili Peppers |
| ro-space-challenger-space-shuttle | space flight | 1983-04-04 | 13:30:00 UTC-5 | Space: Challenger (Space Shuttle) |
| ro-terrorist-bombing-lebanon | terror attack | 1983-04-18 | 15:05:00 UTC+2 | Terrorist: Bombing Lebanon |
| ro-ufo-sighting-14903 | UFO sighting | 1983-08-19 | 23:20:00 UTC-3 | UFO Sighting 14903 |
| ro-plane-crash-korean-airlines-flight-007-1983 | air crash | 1983-09-01 | 18:06:02 UTC+0 | Plane Crash: Korean Airlines Flight 007 (1983) |
| ro-astrodienst-ag | business | 1983-10-04 | 16:00:00 UTC+1 | Astrodienst AG |
| ro-terrorist-marines-killed | terror attack | 1983-10-23 | 06:22:00 UTC+2 | Terrorist: Marines killed |
| ro-plane-crash-avianca-flight-011-1983 | air crash | 1983-11-27 | 01:06:27 UTC+1 | Plane Crash: Avianca Flight 011 (1983) |
| ro-ufo-sighting-14919 | UFO sighting | 1983-12-14 | 22:00:00 UTC-3 | UFO Sighting 14919 |
| ro-ufo-sighting-14930 | UFO sighting | 1984-01-22 | 23:30:00 UTC-3 | UFO Sighting 14930 |
| ro-nature-mauna-loa-eruption-1984 | volcano | 1984-03-25 | 01:30:00 UTC-10 | Nature:Mauna Loa eruption (1984) |
| ro-ufo-sighting-14945 | UFO sighting | 1984-04-18 | 18:54:00 UTC-3 | UFO Sighting 14945 |
| ro-ufo-sighting-14946 | UFO sighting | 1984-04-18 | 19:30:00 UTC-3 | UFO Sighting 14946 |
| ro-ufo-sighting-14960 | UFO sighting | 1984-07-24 | 22:30:00 UTC-4 | UFO Sighting 14960 |
| ro-sports-1984-summer-olympics-los-angeles | sports event | 1984-07-28 | 19:40:00 UTC-7 | Sports: 1984 Summer Olympics, Los Angeles |
| ro-entertainment-santa-barbara | TV show | 1984-07-30 | 15:00:00 UTC-4 | Entertainment: Santa Barbara |
| ro-space-discovery-space-shuttle | space flight | 1984-09-05 | 06:37:54 UTC-4 | Space: Discovery (Space Shuttle) |
| ro-entertainment-the-cosby-show | TV show | 1984-09-20 | 20:00:00 UTC-4 | Entertainment: The Cosby Show |
| ro-nature-earthquake-central-california-1984 | earthquake | 1984-11-23 | 18:08:27 UTC+0 | Nature:Earthquake:Central California 1984 |
| ro-accident-bhopal-gas-explosion | explosion | 1984-12-03 | 00:35:00 UTC+5.5 | Accident: Bhopal gas explosion |
| ro-plane-crash-aeroflot-flight-3519-1984 | air crash | 1984-12-23 | 14:15:00 UTC+7 | Plane Crash: Aeroflot Flight 3519 (1984) |
| ro-plane-crash-iberia-airlines-flight-610-1985 | air crash | 1985-02-19 | 09:27:04 UTC+1 | Plane Crash: Iberia Airlines Flight 610 (1985) |
| ro-entertainment-eastenders | entertainment | 1985-02-19 | 19:00:00 UTC+0 | Entertainment: EastEnders |
| ro-ufo-sighting-15009 | UFO sighting | 1985-04-27 | 23:00:00 UTC+5.5 | UFO Sighting 15009 |
| ro-plane-crash-air-india-flight-182-1985 | air crash | 1985-06-23 | 07:14:01 UTC+0 | Plane Crash: Air India Flight 182 (1985) |
| ro-ufo-sighting-15013 | UFO sighting | 1985-06-23 | 15:00:00 UTC-3 | UFO Sighting 15013 |
| ro-ufo-sighting-15014 | UFO sighting | 1985-06-23 | 18:00:00 UTC-3 | UFO Sighting 15014 |
| ro-space-giotto-spacecraft | space flight | 1985-07-02 | 11:23:00 UTC+0 | Space: Giotto (spacecraft) |
| ro-plane-crash-aeroflot-flight-7425-1985 | air crash | 1985-07-10 | 23:46:00 UTC+3 | Plane Crash: Aeroflot Flight 7425 (1985) |
| ro-plane-crash-delta-air-lines-flight-191-1985 | air crash | 1985-08-02 | 18:05:52 UTC-5 | Plane Crash: Delta Air Lines Flight 191 (1985) |
| ro-plane-crash-japan-airlines-flight-123-1985 | air crash | 1985-08-12 | 18:56:28 UTC+9 | Plane Crash: Japan Airlines Flight 123 (1985) |
| ro-ufo-sighting-15021 | UFO sighting | 1985-08-18 | 18:44:00 UTC-3 | UFO Sighting 15021 |
| ro-ufo-sighting-15022 | UFO sighting | 1985-08-18 | 19:30:00 UTC-3 | UFO Sighting 15022 |
| ro-ufo-sighting-15023 | UFO sighting | 1985-08-18 | 20:30:00 UTC-3 | UFO Sighting 15023 |
| ro-ufo-sighting-15024 | UFO sighting | 1985-08-19 | 17:55:00 UTC-3 | UFO Sighting 15024 |
| ro-ufo-sighting-15025 | UFO sighting | 1985-08-21 | 21:00:00 UTC-3 | UFO Sighting 15025 |
| ro-ufo-sighting-15026 | UFO sighting | 1985-08-26 | 13:30:00 UTC-3 | UFO Sighting 15026 |
| ro-entertainment-the-golden-girls | TV show | 1985-09-14 | 21:00:00 UTC-4 | Entertainment: The Golden Girls |
| ro-ufo-sighting-15028 | UFO sighting | 1985-09-17 | 07:10:00 UTC-3 | UFO Sighting 15028 |
| ro-plane-crash-arrow-air-flight-1285-1985 | air crash | 1985-12-12 | 06:46:00 UTC-3.5 | Plane Crash: Arrow Air Flight 1285 (1985) |
| ro-helicopter-crash-paris-dakar-rally | air crash | 1986-01-14 | 19:20:00 UTC+0 | Helicopter crash: Paris-Dakar rally |
| ro-space-challenger-disaster | space flight | 1986-01-28 | 11:38:00 UTC-5 | Space: Challenger Disaster |
| ro-space-mir-space-station | space flight | 1986-02-19 | 21:28:23 UTC+0 | Space: Mir (Space Station) |
| ro-oracle-shares | business | 1986-03-12 | 09:30:00 UTC-5 | Oracle, Shares |
| ro-microsoft-shares | business | 1986-03-13 | 09:30:00 UTC-5 | Microsoft, Shares |
| ro-plane-crash-mexicana-flight-940-1986 | air crash | 1986-03-31 | 09:05:08 UTC-6 | Plane Crash: Mexicana Flight 940 (1986) |
| ro-accident-mexicana-airlines-crash-1986 | air crash | 1986-03-31 | 09:04:00 UTC-6 | Accident: Mexicana Airlines Crash 1986 |
| ro-concert-rendez-vous-houston | other | 1986-04-05 | 20:30:00 UTC-6 | Concert: Rendez-vous Houston |
| ro-terrorist-attack-la-belle | terror attack | 1986-04-05 | 01:30:00 UTC+2 | Terrorist attack:La Belle |
| ro-accident-chernobyl-explosion | explosion | 1986-04-26 | 01:23:00 UTC+4 | Accident: Chernobyl Explosion |
| ro-nature-earthquake-mexico-1986 | earthquake | 1986-04-30 | 07:07:19 UTC+0 | Nature:Earthquake Mexico 1986 |
| ro-nature-lake-nyos-event | other | 1986-08-21 | 20:30:00 UTC+1 | Nature:Lake Nyos Event |
| ro-astrology-cedra | organization | 1986-09-17 | 11:20:00 UTC+2 | Astrology: CEDRA |
| ro-accident-schweizerhalle | accident | 1986-11-01 | 00:19:00 UTC+1 | Accident: Schweizerhalle |
| ro-nature-earthquake-peru-ecuador-1986 | earthquake | 1986-11-23 | 01:39:22 UTC+0 | Nature:Earthquake Peru-Ecuador 1986 |
| ro-business-british-airways-shares | air crash | 1987-02-11 | 08:30:00 UTC+0 | Business: British Airways Shares |
| ro-accident-ferry-herald-of-free-enterprise | shipwreck | 1987-03-06 | 19:05:00 UTC+1 | Accident: Ferry Herald of Free Enterprise |
| ro-entertainment-french-and-saunders | TV show | 1987-03-09 | 21:00:00 UTC+0 | Entertainment: French and Saunders |
| ro-celestial-jupiter-cycle | celestial | 1987-03-13 | 01:31:00 UTC-5 | Celestial: Jupiter Cycle |
| ro-entertainment-the-bold-and-the-beautiful | TV show | 1987-03-23 | 13:30:00 UTC-5 | Entertainment: The Bold and the Beautiful |
| ro-entertainment-married-with-children | entertainment | 1987-04-05 | 19:00:00 UTC-4 | Entertainment: Married... With Children |
| ro-plane-crash-lot-flight-5055-1987 | air crash | 1987-05-09 | 11:12:13 UTC+2 | Plane Crash: LOT Flight 5055 (1987) |
| ro-nature-philippines-mindanao-1987 | other | 1987-05-12 | 01:30:27 UTC+0 | Nature:Philippines/Mindanao 1987 |
| ro-crime-knightsbridge-security-deposit-robbery | crime | 1987-07-12 | 15:15:00 UTC+1 | Crime: Knightsbridge Security Deposit robbery |
| ro-plane-crash-northwest-airlines-flight-255-1987 | air crash | 1987-08-16 | 20:45:19 UTC-4 | Plane Crash: Northwest Airlines Flight 255 (1987) |
| ro-entertainment-full-house | TV show | 1987-09-22 | 20:30:00 UTC-4 | Entertainment: Full House |
| ro-nature-earthquake-ethiopia-1987 | earthquake | 1987-10-25 | 16:46:14 UTC+0 | Nature:Earthquake:Ethiopia 1987 |
| ro-terrorist-remembrance-day-bombing | terror attack | 1987-11-08 | 10:43:00 UTC+0 | Terrorist: Remembrance Day bombing |
| ro-accident-london-fire | fire | 1987-11-18 | 19:36:00 UTC+0 | Accident: London fire |
| ro-phenomena-a-nightmare-s-accident | phenomenon | 1987-11-19 | 02:00:00 UTC-8 | Phenomena:A Nightmare's Accident |
| ro-plane-crash | air crash | 1987-11-29 | 02:05:00 UTC+9 | Plane Crash: |
| ro-plane-crash-1987-alianza-lima-disaster | air crash | 1987-12-08 | 20:14:00 UTC-5 | Plane Crash: 1987 Alianza Lima disaster |
| ro-political-inf-treaty | political | 1987-12-08 | 14:02:00 UTC-5 | Political: INF Treaty |
| ro-entertainment-home-and-away | entertainment | 1988-01-17 | 19:30:00 UTC+11 | Entertainment: Home and Away |
| ro-plane-crash-china-southwest-a-flight-4146-1988 | air crash | 1988-01-18 | 22:17:00 UTC+8 | Plane Crash: China Southwest A. Flight 4146 (1988) |
| ro-astrology-afan-inc | organization | 1988-01-29 | 14:12:00 UTC-8 | Astrology: AFAN Inc. |
| ro-celestial-pluto-cycle | celestial | 1988-02-26 | 18:16:00 UTC-5 | Celestial: Pluto Cycle |
| ro-nature-avalanche-klosters-1988 | avalanche | 1988-03-10 | 14:45:00 UTC+1 | Nature: Avalanche, Klosters 1988 |
| ro-entertainment-the-wonder-years | TV show | 1988-03-15 | 20:30:00 UTC-5 | Entertainment: The Wonder Years |
| ro-plane-crash-avianca-flight-410-1988 | air crash | 1988-03-17 | 13:17:46 UTC-5 | Plane Crash: Avianca Flight 410 (1988) |
| ro-animal-molloko | other | 1988-04-29 | 17:38:00 UTC-7 | Animal: Molloko |
| ro-synodic-sat-uranus-helio | celestial | 1988-06-09 | 07:54:00 UTC+1 | Synodic: Sat-Uranus Helio |
| ro-plane-crash-iran-air-flight-655-1988 | air crash | 1988-07-03 | 10:24:00 UTC+3.5 | Plane Crash: Iran Air Flight 655 (1988) |
| ro-accident-piper-alpha-oil-rig-explosion | explosion | 1988-07-06 | 21:58:00 UTC+1 | Accident: Piper Alpha Oil Rig Explosion |
| ro-entertainment-roseanne | entertainment | 1988-10-18 | 20:30:00 UTC-4 | ‎Entertainment: Roseanne |
| ro-synodic-saturn-uranus-geo | celestial | 1988-10-18 | 13:13:00 UTC+1 | Synodic: Saturn-Uranus Geo |
| ro-plane-crash-indian-airlines-flight-113-1988 | air crash | 1988-10-19 | 06:53:00 UTC+5.5 | Plane Crash: Indian Airlines Flight 113 (1988) |
| ro-entertainment-murphy-brown | entertainment | 1988-11-14 | 21:00:00 UTC-5 | Entertainment: Murphy Brown |
| ro-terrorist-lockerbie-bombing | terror attack | 1988-12-21 | 19:02:50 UTC+0 | Terrorist: Lockerbie bombing |
| ro-plane-crash-independent-air-flight-1851-1989 | air crash | 1989-02-08 | 13:08:12 UTC-1 | Plane Crash: Independent Air Flight 1851 (1989) |
| ro-terrorist-clive-barracks-bombing | terror attack | 1989-02-20 | 03:10:00 UTC+0 | Terrorist: Clive Barracks bombing |
| ro-synodic-saturn-nep-geo | celestial | 1989-03-03 | 12:03:00 UTC+0 | Synodic: Saturn-Nep Geo |
| ro-historic-love-parade-german-music-festival | historic | 1989-07-01 | 16:30:00 UTC+2 | Historic: Love Parade (German music festival) |
| ro-entertainment-seinfeld | entertainment | 1989-07-05 | 21:30:00 UTC-4 | Entertainment: Seinfeld |
| ro-nature-earthquake-and-eruption-japan | earthquake | 1989-07-13 | 09:33:00 UTC+0 | Nature:Earthquake and Eruption (Japan) |
| ro-synodic-sat-neptune-helio | celestial | 1989-07-17 | 07:42:00 UTC+1 | Synodic: Sat-Neptune Helio |
| ro-plane-crash-united-airlines-flight-232-1989 | air crash | 1989-07-19 | 16:00:00 UTC-5 | Plane Crash: United Airlines Flight 232 (1989) |
| ro-plane-crash-uta-flight-772-1989 | air crash | 1989-09-19 | 13:59:00 UTC+1 | Plane Crash: UTA Flight 772 (1989) |
| ro-entertainment-baywatch | TV show | 1989-09-22 | 20:00:00 UTC-4 | Entertainment: Baywatch |
| ro-plane-crash-tan-sahsa-flight-414-1989 | air crash | 1989-10-21 | 07:53:00 UTC-6 | Plane Crash: Tan-Sahsa Flight 414 (1989) |
| ro-historic-fall-of-the-berlin-wall | historic | 1989-11-09 | 18:57:00 UTC+1 | Historic: Fall of the Berlin Wall |
| ro-plane-crash-avianca-flight-203-1989 | air crash | 1989-11-27 | 07:16:00 UTC-5 | Plane crash: Avianca Flight 203 (1989) |
| ro-mortality-1989-ecole-polytechnique-massacre | terror attack | 1989-12-06 | 17:10:00 UTC-5 | Mortality: 1989 École Polytechnique massacre; Shooting Spree: Montreal Polytechnique massacre |
| ro-entertainment-the-simpsons | entertainment | 1989-12-17 | 20:30:00 UTC-5 | Entertainment: The Simpsons |
| ro-cisco-systems-shares | business | 1990-02-16 | 09:30:00 UTC-5 | Cisco Systems, Shares |
| ro-entertainment-twin-peaks | TV show | 1990-04-08 | 21:00:00 UTC-4 | Entertainment: Twin Peaks |
| ro-space-hubble-space-telescope-launch | space flight | 1990-04-24 | 08:33:51 UTC-4 | Space: Hubble Space Telescope (Launch) |
| ro-plane-crash-xiamen-airlines-flight-8301-1990 | air crash | 1990-10-02 | 09:04:00 UTC+8 | Plane Crash: Xiamen Airlines Flight 8301 (1990) |
| ro-entertainment-beverly-hills-90210 | TV show | 1990-10-04 | 20:30:00 UTC-4 | Entertainment: Beverly Hills, 90210 |
| ro-military-persian-gulf-war | military | 1991-01-15 | 10:30:00 UTC-5 | Military: Persian Gulf War |
| ro-plane-crash-lauda-air-flight-004-1991 | air crash | 1991-05-26 | 23:17:00 UTC+7 | Plane Crash: Lauda Air Flight 004 (1991) |
| ro-nature-volcano-philippines | volcano | 1991-06-12 | 08:51:00 UTC+8 | Nature: Volcano Philippines |
| ro-plane-crash-nigeria-airways-flight-2120-1991 | air crash | 1991-07-11 | 08:38:00 UTC+3 | Plane Crash: Nigeria Airways Flight 2120 (1991) |
| ro-world-wide-web | other | 1991-08-06 | 16:56:20 UTC+2 | World Wide Web |
| ro-astrology-kepler-college | organization | 1991-09-03 | 13:04:00 UTC-7 | Astrology: Kepler College |
| ro-accident-1992-airbus-a320-crash-strasbourg | air crash | 1992-01-20 | 19:20:00 UTC+1 | Accident: 1992 Airbus A320 crash, Strasbourg |
| ro-historic-bosnian-war-begin | military | 1992-04-03 | 15:30:00 UTC+2 | Historic: Bosnian War, begin |
| ro-accident-furiani-stadium-collapse | accident | 1992-05-05 | 20:20:00 UTC+2 | Accident: Furiani Stadium collapse |
| ro-entertainment-melrose-place | entertainment | 1992-07-08 | 20:30:00 UTC-4 | Entertainment: Melrose Place |
| ro-sports-1992-summer-olympics-barcelona | sports event | 1992-07-25 | 22:21:00 UTC+2 | Sports: 1992 Summer Olympics, Barcelona |
| ro-plane-crash-cgac-flight-7552-1992 | air crash | 1992-07-31 | 15:06:00 UTC+8 | Plane Crash: CGAC Flight 7552 (1992) |
| ro-nature-flood-vaison-la-romaine-1992 | flood | 1992-09-22 | 15:00:00 UTC+2 | Nature: Flood Vaison-la-Romaine (1992) |
| ro-plane-crash-el-al-flight-1862-1992 | air crash | 1992-10-04 | 18:35:00 UTC+1 | Plane Crash: El Al Flight 1862 (1992) |
| ro-nature-peekskill-meteorite | meteor | 1992-10-09 | 20:00:00 UTC-4 | Nature:Peekskill meteorite |
| ro-entertainment-absolutely-fabulous | TV show | 1992-11-12 | 21:00:00 UTC+0 | Entertainment: Absolutely Fabulous |
| ro-historic-demolition-of-the-babri-masjid | historic | 1992-12-06 | 15:45:00 UTC+5.5 | Historic: Demolition of the Babri Masjid |
| ro-nation-belgium | founding | 1993-02-06 | 20:36:00 UTC+1 | Nation: Belgium |
| ro-entertainment-babylon-5 | TV show | 1993-02-22 | 20:00:00 UTC-5 | Entertainment: Babylon 5 |
| ro-terrorist-wtc-1993 | terror attack | 1993-02-26 | 12:17:37 UTC-5 | Terrorist: WTC (1993) |
| ro-terrorist-1993-bombay-bombings | terror attack | 1993-03-12 | 13:30:00 UTC+5.5 | Terrorist: 1993 Bombay bombings |
| ro-synodic-uranus-nep-helio | celestial | 1993-04-20 | 07:10:00 UTC+1 | Synodic: Uranus-Nep Helio |
| ro-historic-fermat-s-theorem | historic | 1993-06-23 | 10:30:00 UTC+1 | Historic: Fermat's theorem |
| ro-entertainment-frasier | TV show | 1993-09-16 | 21:30:00 UTC-4 | Entertainment: Frasier |
| ro-sports-sydney-wins-2000-olympics-bid | sports event | 1993-09-23 | 20:28:00 UTC+2 | Sports: Sydney Wins 2000 Olympics Bid |
| ro-synodic-uranus-nep-geo | celestial | 1993-10-25 | 06:46:00 UTC+0 | Synodic: Uranus-Nep Geo |
| ro-entertainment-the-nanny | TV show | 1993-11-03 | 20:30:00 UTC-5 | Entertainment: The Nanny |
| ro-accident-aircraft-explosion | air crash | 1993-12-10 | 07:00:00 UTC-6 | Accident: Aircraft Explosion |
| ro-sports-1994-winter-olympics-lillehammer | sports event | 1994-02-12 | 17:13:00 UTC+1 | Sports: 1994 Winter Olympics, Lillehammer |
| ro-celestial-mars-cycle | celestial | 1994-04-17 | 15:27:00 UTC-4 | Celestial: Mars Cycle |
| ro-plane-crash-china-airlines-flight-140-1994 | air crash | 1994-04-26 | 20:15:45 UTC+9 | Plane Crash: China Airlines Flight 140 (1994) |
| ro-historic-chunnel | historic | 1994-05-06 | 10:57:00 UTC+1 | Historic: Chunnel |
| ro-plane-crash-china-northwest-a-flight-2303-1994 | air crash | 1994-06-06 | 08:22:42 UTC+8 | Plane Crash: China Northwest A. Flight 2303 (1994) |
| ro-aviation-boeing-777-maiden-flight | aviation | 1994-06-12 | 11:45:00 UTC-7 | Aviation: Boeing 777 Maiden Flight |
| ro-historic-first-frontier-israel-jordan | historic | 1994-08-08 | 11:00:00 UTC+3 | Historic: First frontier Israel-Jordan |
| ro-plane-crash-usair-flight-427-1994 | air crash | 1994-09-08 | 19:03:23 UTC-4 | Plane Crash: USAir Flight 427 (1994); Accident: Plane, USAir |
| ro-entertainment-friends | TV show | 1994-09-22 | 20:30:00 UTC-4 | Entertainment: Friends |
| ro-business-amazon-website | business | 1994-10-31 | 21:00:00 UTC-8 | Business: Amazon Website |
| ro-nature-popocatepetl-eruption | volcano | 1994-12-21 | 06:30:00 UTC-6 | Nature:Popocatèpetl Eruption |
| ro-terrorist-hostages | terror attack | 1994-12-24 | 11:15:00 UTC+1 | Terrorist: Hostages |
| ro-terrorist-air-france-flight-8969-police-assault | terror attack | 1994-12-26 | 17:12:00 UTC+1 | Terrorist: Air France Flight 8969 Police assault |
| ro-civic-event-simpson-trial | crime | 1995-01-24 | 10:35:00 UTC-8 | Civic Event: Simpson trial |
| ro-accident-construction-crane-collapse-toul-fr | accident | 1995-01-26 | 16:18:00 UTC+1 | Accident: Construction Crane Collapse (Toul, FR) |
| ro-terrorist-oklahoma-city-bombing | terror attack | 1995-04-19 | 09:02:00 UTC-5 | Terrorist: Oklahoma City bombing |
| ro-accident-carbon-monoxide | other | 1995-05-21 | 21:00:00 UTC+2 | Accident: Carbon Monoxide |
| ro-business-ebay-website | business | 1995-08-03 | 21:00:00 UTC-7 | Business: eBay Website |
| ro-historic-kraijna-reconquered | historic | 1995-08-04 | 05:03:00 UTC+2 | Historic: Kraijna reconquered |
| ro-business-windows-95 | business | 1995-08-24 | 00:01:00 UTC-7 | Business: Windows '95 |
| ro-entertainment-the-drew-carey-show | entertainment | 1995-09-13 | 20:30:00 UTC-4 | Entertainment: The Drew Carey Show |
| ro-historic-bosnian-war-ceasefire | military | 1995-10-12 | 00:01:00 UTC+1 | Historic: Bosnian War:Ceasefire |
| ro-space-soho-space-probe | space flight | 1995-12-02 | 08:08:00 UTC+0 | Space: SOHO (space probe) |
| ro-historic-bosnia-treaty | political | 1995-12-14 | 11:48:00 UTC+1 | Historic: Bosnia Treaty |
| ro-plane-crash-trans-service-airlift-1995 | air crash | 1995-12-20 | 21:38:00 UTC-5 | Plane Crash: Trans Service Airlift (1995) |
| ro-entertainment-3rd-rock-from-the-sun | entertainment | 1996-01-09 | 20:30:00 UTC-5 | Entertainment: 3rd Rock from the Sun |
| ro-plane-crash-birgenair-flight-301-1996 | air crash | 1996-02-06 | 23:47:14 UTC-4 | Plane Crash: Birgenair Flight 301 (1996) |
| ro-space-near-launch | space flight | 1996-02-17 | 15:43:00 UTC-5 | Space: NEAR launch |
| ro-mostar-reunification | other | 1996-02-20 | 12:00:00 UTC+1 | Mostar, reunification |
| ro-novartis | business | 1996-03-06 | 23:55:00 UTC+1 | Novartis |
| ro-mortality-dunblane-school-massacre | terror attack | 1996-03-13 | 09:32:00 UTC+0 | Mortality: Dunblane school massacre |
| ro-historic-sarajevo-reunification | historic | 1996-03-19 | 06:00:00 UTC+1 | Historic: Sarajevo, reunification |
| ro-kidnapping-monks-of-tibhirine | crime | 1996-03-27 | 01:15:00 UTC+1 | Kidnapping: Monks of Tibhirine |
| ro-shooting-spree-port-arthur-tasmania | shooting | 1996-04-28 | 11:45:00 UTC+10 | Shooting spree: Port Arthur Tasmania |
| ro-accident-mall-explosion | explosion | 1996-06-11 | 12:15:00 UTC-3 | Accident: Mall Explosion |
| ro-terrorist-dhahran-bombs-1996 | terror attack | 1996-06-25 | 21:48:00 UTC+3 | Terrorist:Dhahran bombs 1996 |
| ro-science-cloning | science | 1996-07-05 | 16:30:00 UTC+1 | Science: Cloning |
| ro-plane-crash-twa-flight-800-1996 | air crash | 1996-07-17 | 20:31:00 UTC-4 | Plane Crash: TWA Flight 800 (1996) |
| ro-business-enron | business | 1996-07-19 | 16:24:00 UTC-7 | Business: Enron |
| ro-sports-1996-summer-olympics-atlanta | sports event | 1996-07-20 | 00:02:00 UTC-4 | Sports: 1996 Summer Olympics, Atlanta |
| ro-nation-afghanistan-taliban-rule-1996 | founding | 1996-09-27 | 03:00:00 UTC+4.5 | Nation: Afghanistan Taliban Rule (1996) |
| ro-astrology-act | organization | 1997-04-28 | 16:58:00 UTC-4 | Astrology: ACT |
| ro-business-yahoo | business | 1997-05-15 | 09:30:00 UTC-4 | Business: Yahoo |
| ro-nature-soufriere-de-montserrat | other | 1997-06-25 | 17:02:00 UTC+0 | Nature:Soufrière de Montserrat |
| ro-cities-hong-kong | city | 1997-07-01 | 00:00:00 UTC+8 | Cities: Hong Kong |
| ro-entertainment-oz | entertainment | 1997-07-12 | 23:30:00 UTC-4 | Entertainment: Oz |
| ro-nature-oder-neisse-flood-1997 | flood | 1997-07-23 | 09:10:00 UTC+2 | Nature:Oder-Neisse flood 1997 |
| ro-entertainment-the-view | entertainment | 1997-08-11 | 11:00:00 UTC-4 | Entertainment: The View |
| ro-entertainment-ally-mcbeal | TV show | 1997-09-08 | 21:00:00 UTC-4 | Entertainment: Ally McBeal |
| ro-business-google-website | business | 1997-09-15 | 00:00:00 UTC-7 | Business: Google Website |
| ro-science-swiss-ephemeris | science | 1997-09-30 | 16:00:00 UTC+2 | Science: Swiss Ephemeris |
| ro-space-cassini-huygens-spacecraft | space flight | 1997-10-15 | 04:43:00 UTC-4 | Space: Cassini-Huygens (spacecraft) |
| ro-accident-fire-italy | fire | 1997-10-31 | 11:09:00 UTC+1 | Accident: Fire, Italy |
| ro-entertainment-dawson-s-creek | TV show | 1998-01-20 | 21:00:00 UTC-5 | Entertainment: Dawson's Creek |
| ro-nuclear-test-india | nuclear test | 1998-05-11 | 12:15:00 UTC+5.5 | Nuclear:Test India |
| ro-entertainment-sex-and-the-city | entertainment | 1998-06-06 | 21:45:00 UTC-4 | Entertainment: Sex and the City |
| ro-plane-crash-ostende-airshow-1997 | air crash | 1998-07-26 | 16:58:00 UTC+2 | Plane Crash: Ostende Airshow 1997 |
| ro-terrorist-omagh-bombing-1998 | terror attack | 1998-08-15 | 15:10:00 UTC+1 | Terrorist: Omagh Bombing 1998 |
| ro-entertainment-that-70s-show | entertainment | 1998-08-23 | 20:30:00 UTC-4 | Entertainment: That '70s Show |
| ro-accident-plane-ecuador | air crash | 1998-08-29 | 13:20:00 UTC-5 | Accident: Plane Ecuador |
| ro-accident-plane-swissair | air crash | 1998-09-02 | 20:16:00 UTC-4 | Accident: Plane Swissair |
| ro-entertainment-total-request-live | entertainment | 1998-09-14 | 15:30:00 UTC-4 | Entertainment: Total Request Live |
| ro-entertainment-will-and-grace | TV show | 1998-09-21 | 21:30:00 UTC-4 | Entertainment: Will and Grace |
| ro-entertainment-charmed | entertainment | 1998-10-07 | 21:00:00 UTC-4 | Entertainment: Charmed |
| ro-astrology-isar-memberletter | organization | 1998-11-15 | 19:35:00 UTC+1 | Astrology: ISAR memberletter |
| ro-space-international-space-station-iss | space flight | 1998-11-20 | 06:40:27 UTC+0 | Space: International Space Station (ISS) |
| ro-business-euro-introduction | business | 1999-01-01 | 00:00:01 UTC+1 | Business: Euro introduction |
| ro-entertainment-the-sopranos | entertainment | 1999-01-10 | 21:00:00 UTC-5 | Entertainment: The Sopranos |
| ro-accident-blackout-sao-paulo-1999 | accident | 1999-03-11 | 10:18:00 UTC-3 | Accident: Blackout São Paulo 1999 |
| ro-business-alibaba-website | business | 1999-04-14 | 21:00:00 UTC+8 | Business: Alibaba Website |
| ro-sports-racing-yacht | sports event | 1999-05-05 | 13:00:00 UTC+2 | Sports: Racing Yacht |
| ro-entertainment-passions | TV show | 1999-07-05 | 14:00:00 UTC-4 | Entertainment: Passions |
| ro-entertainment-the-west-wing | TV show | 1999-09-22 | 21:00:00 UTC-4 | Entertainment: The West Wing |
| ro-accident-ladbroke-grove-rail-crash | rail accident | 1999-10-05 | 08:08:00 UTC+1 | Accident: Ladbroke Grove rail crash |
| ro-astrology-u-a-c-inc | organization | 1999-10-15 | 11:46:00 UTC-4 | Astrology: U.A.C. Inc |
| ro-nature-cyclone-martin-1999 | cyclone | 1999-12-27 | 16:00:00 UTC+1 | Nature: Cyclone Martin (1999) |
| ro-entertainment-malcolm-in-the-middle | TV show | 2000-01-09 | 20:30:00 UTC-5 | Entertainment: Malcolm in the Middle |
| ro-business-twitter-website | business | 2000-01-21 | 11:28:17 UTC-5 | Business: Twitter Website |
| ro-plane-crash-alaska-airlines-flight-261-2000 | air crash | 2000-01-31 | 16:21:00 UTC-8 | Plane Crash: Alaska Airlines Flight 261 (2000) |
| ro-infineon-shares | business | 2000-03-13 | 09:00:00 UTC+1 | Infineon, Shares |
| ro-nature-avalanche-austria | avalanche | 2000-03-28 | 14:50:00 UTC+2 | Nature: Avalanche Austria |
| ro-plane-crash-air-philippines-flight-541-2000 | air crash | 2000-04-19 | 06:58:00 UTC+8 | Plane Crash: Air Philippines Flight 541 (2000) |
| ro-astrology-afan-list | organization | 2000-04-27 | 09:00:00 UTC-4 | Astrology: AFAN List |
| ro-accident-enschede-fireworks-disaster | fire | 2000-05-13 | 15:34:00 UTC+2 | Accident: Enschede Fireworks Disaster |
| ro-accident-plane-atlantic-city | air crash | 2000-05-21 | 11:48:00 UTC-4 | Accident: Plane, Atlantic City |
| ro-nature-earthquake-india-40283 | earthquake | 2000-06-08 | 02:22:00 UTC+5.5 | Nature: Earthquake India 40283 |
| ro-nature-kyushu-earthquake-japan-2000-june | earthquake | 2000-06-08 | 09:32:00 UTC+9 | Nature: Kyushu Earthquake:Japan 2000 (june) |
| ro-astrology-turkish-astrological-association | organization | 2000-06-11 | 10:23:00 UTC+3 | Astrology: Turkish Astrological Association |
| ro-synodic-jup-sat-helio | celestial | 2000-06-22 | 15:49:00 UTC+1 | Synodic: Jup-Sat Helio |
| ro-entertainment-big-brother-usa | entertainment | 2000-07-05 | 21:00:00 UTC-4 | Entertainment: Big Brother (USA) |
| ro-nature-istanbul-earthquake-turkey-2000 | earthquake | 2000-07-07 | 03:15:00 UTC+3 | Nature: Istanbul Earthquake:Turkey 2000 |
| ro-nature-tornado-alberta | tornado | 2000-07-14 | 18:30:00 UTC-6 | Nature: Tornado Alberta |
| ro-accident-concorde | air crash | 2000-07-25 | 16:46:00 UTC+2 | Accident: Concorde |
| ro-political-bush-cheney | political | 2000-07-25 | 14:06:00 UTC-5 | Political: Bush-Cheney |
| ro-accident-kursk-submarine | accident | 2000-08-12 | 11:28:00 UTC+4 | Accident: Kursk Submarine |
| ro-plane-crash-gulf-air-flight-072-2000 | air crash | 2000-08-23 | 19:20:00 UTC+3 | Plane Crash: Gulf Air Flight 072 (2000) |
| ro-nature-volcano-japan | volcano | 2000-08-29 | 04:35:00 UTC+9 | Nature: Volcano Japan |
| ro-nature-eruption-popocatepetl-mexico-2000 | volcano | 2000-09-04 | 03:40:00 UTC-5 | Nature: Eruption Popocatepetl:Mexico 2000 |
| ro-sports-2000-summer-olympics-sydney | sports event | 2000-09-15 | 19:00:00 UTC+11 | Sports: 2000 Summer Olympics, Sydney |
| ro-astrology-opa-inc | organization | 2000-10-04 | 13:45:00 UTC-4 | Astrology: OPA Inc |
| ro-historic-storming-of-belgrade-parliament | storm | 2000-10-05 | 15:35:00 UTC+2 | Historic: Storming of Belgrade parliament |
| ro-terrorist-u-s-s-cole | terror attack | 2000-10-12 | 11:18:00 UTC+3 | Terrorist: U.S.S. Cole |
| ro-plane-crash-singapore-airlines-flight-006-2000 | air crash | 2000-10-31 | 23:18:00 UTC+8 | Plane Crash: Singapore Airlines Flight 006 (2000) |
| ro-accident-austrian-train-wreck | rail accident | 2000-11-11 | 09:00:00 UTC+1 | Accident: Austrian Train Wreck |
| ro-accident-cable-car | accident | 2000-11-11 | 09:10:00 UTC+1 | Accident: Cable Car |
| ro-plane-crash-asa-pesada-luanda-2000 | air crash | 2000-11-15 | 13:05:00 UTC+1 | Plane Crash: ASA Pesada (Luanda, 2000) |
| ro-transportation-acela-express | other | 2000-11-15 | 09:45:00 UTC-5 | Transportation: Acela Express |
| ro-entertainment-queer-as-folk-usa | TV show | 2000-12-03 | 22:00:00 UTC-5 | Entertainment: Queer as Folk (USA) |
| ro-social-global-crime-conferenc | organization | 2000-12-12 | 09:00:00 UTC+1 | Social: Global Crime Conferenc |
| ro-historic-chernobyl-closing | historic | 2000-12-15 | 13:16:00 UTC+2 | Historic: Chernobyl closing |
| ro-accident-fire-china | fire | 2000-12-25 | 21:35:00 UTC+8 | Accident: Fire, China |
| ro-accident-fire-holland | fire | 2001-01-01 | 00:15:00 UTC+1 | Accident: Fire, Holland |
| ro-accident-electric-explosion | explosion | 2001-01-03 | 11:45:00 UTC-5 | Accident: Electric Explosion |
| ro-business-wikipedia | business | 2001-01-13 | 00:12:14 UTC+0 | Business: Wikipedia |
| ro-sports-super-bowl-2001 | sports event | 2001-01-28 | 18:25:00 UTC-5 | Sports: Super Bowl 2001 |
| ro-space-near-landing | space flight | 2001-02-12 | 15:04:00 UTC-5 | Space: NEAR landing |
| ro-animal-cassowary-attack | terror attack | 2001-02-15 | 15:00:00 UTC-8 | Animal: Cassowary attack |
| ro-military-baghdad-operation | military | 2001-02-16 | 12:30:00 UTC+3 | Military: Baghdad Operation |
| ro-nature-earthquake-el-salvador-2001-iii | earthquake | 2001-02-17 | 14:25:00 UTC-6 | Nature: Earthquake El Salvador: 2001 (III) |
| ro-accident-freeway | accident | 2001-02-20 | 10:15:00 UTC-8 | Accident: Freeway |
| ro-accident-plane-nat-l-guard | air crash | 2001-03-03 | 11:00:00 UTC-5 | Accident: Plane Nat'l Guard |
| ro-accident-amtrak-iowa | rail accident | 2001-03-17 | 23:40:00 UTC-6 | Accident: Amtrak Iowa |
| ro-space-mir-landing | space flight | 2001-03-23 | 01:30:00 UTC+10 | Space: Mir Landing |
| ro-accident-belgian-train | rail accident | 2001-03-27 | 08:45:00 UTC+2 | Accident: Belgian train |
| ro-accident-plane-aspen | air crash | 2001-03-29 | 19:02:00 UTC-7 | Accident: Plane Aspen |
| ro-social-legalized-gay-marriage | organization | 2001-04-01 | 00:10:00 UTC+2 | Social: Legalized gay marriage |
| ro-space-mars-odyssey | space flight | 2001-04-07 | 11:02:00 UTC-4 | Space: Mars Odyssey |
| ro-sports-kentucky-derby | sports event | 2001-05-05 | 18:07:00 UTC-4 | Sports: Kentucky Derby |
| ro-mortality-nepal-assassination | assassination | 2001-06-01 | 22:40:00 UTC+5.75 | Mortality: Nepal assassination |
| ro-entertainment-six-feet-under | TV show | 2001-06-03 | 22:00:00 UTC-4 | Entertainment: Six Feet Under |
| ro-animal-alligator | other | 2001-06-23 | 21:50:00 UTC-4 | Animal: Alligator |
| ro-space-nasa-observatory-map | space flight | 2001-06-30 | 15:46:46 UTC-4 | Space: NASA Observatory MAP |
| ro-plane-crash-vladivostok-air-flight-352-2001 | air crash | 2001-07-04 | 02:10:00 UTC+9 | Plane crash: Vladivostok Air Flight 352 (2001) |
| ro-accident-train | rail accident | 2001-07-29 | 02:17:00 UTC-5 | Accident: Train |
| ro-accident-explosion-tokyo | explosion | 2001-09-01 | 01:00:00 UTC+9 | Accident: Explosion Tokyo |
| ro-terrorist-wtc-2001 | terror attack | 2001-09-11 | 08:46:00 UTC-4 | Terrorist: WTC  (2001) |
| ro-accident-plane-mexico | air crash | 2001-09-12 | 17:00:00 UTC-5 | Accident: Plane Mexico |
| ro-accident-amtrak-utah | rail accident | 2001-09-13 | 17:30:00 UTC-6 | Accident: Amtrak Utah |
| ro-military-war-authorization | military | 2001-09-16 | 23:18:00 UTC-4 | Military: War Authorization |
| ro-astrology-aerial | organization | 2001-09-18 | 08:51:00 UTC-4 | Astrology: AERIAL |
| ro-accident-toulouse-azf-factory-explosion | explosion | 2001-09-21 | 10:17:00 UTC+2 | Accident: Toulouse AZF factory explosion |
| ro-accident-toulouse-france | accident | 2001-09-21 | 10:21:00 UTC+2 | Accident: Toulouse France |
| ro-terrorist-zug-massacre | terror attack | 2001-09-27 | 10:32:00 UTC+2 | Terrorist: Zug massacre |
| ro-military-afghan-attack | terror attack | 2001-10-07 | 18:57:00 UTC+4.5 | Military: Afghan attack |
| ro-plane-crash-sas-flight-686-2001 | air crash | 2001-10-08 | 08:10:00 UTC+2 | Plane Crash: SAS Flight 686 (2001) |
| ro-terrorist-anthrax-envelope | terror attack | 2001-10-15 | 10:15:00 UTC-4 | Terrorist: Anthrax envelope |
| ro-plane-crash-american-airlines-flight-587-2001 | air crash | 2001-11-12 | 09:16:15 UTC-5 | Plane Crash: American Airlines Flight 587 (2001) |
| ro-nation-afghanistan | founding | 2001-12-22 | 13:12:00 UTC+4.5 | Nation: Afghanistan |
| ro-sports-super-bowl-2002-36 | sports event | 2002-02-03 | 17:40:00 UTC-6 | Sports: Super Bowl 2002 #36 |
| ro-sports-2002-winter-olympics-salt-lake-city | sports event | 2002-02-08 | 21:10:00 UTC-7 | Sports: 2002 Winter Olympics, Salt Lake City |
| ro-science-envisat-start | science | 2002-03-01 | 22:08:00 UTC-3 | Science:Envisat, start |
| ro-mortality-2002-nanterre-massacre | terror attack | 2002-03-27 | 01:11:00 UTC+1 | Mortality: 2002 Nanterre massacre |
| ro-plane-crash-pirelli-tower-crash-milan-2002 | air crash | 2002-04-18 | 17:44:00 UTC+2 | Plane Crash: Pirelli Tower Crash Milan (2002) |
| ro-mortality-erfurt-shooting | shooting | 2002-04-26 | 11:00:00 UTC+2 | Mortality: Erfurt shooting |
| ro-business-rapidshare-website | business | 2002-05-27 | 18:23:36 UTC+0 | Business: Rapidshare Website |
| ro-entertainment-8-simple-rules | TV show | 2002-09-17 | 20:00:00 UTC-4 | Entertainment: 8 Simple Rules |
| ro-terrorist-bali-explosion | terror attack | 2002-10-12 | 23:10:00 UTC+8 | Terrorist: Bali Explosion |
| ro-aviation-germanwings-airline-first-flight | aviation | 2002-10-27 | 06:30:00 UTC+1 | Aviation: Germanwings Airline First Flight |
| ro-business-linkedin-website | business | 2002-11-02 | 07:38:11 UTC-8 | Business: LinkedIn Website |
| ro-astrodatabank-news | other | 2003-01-02 | 14:02:00 UTC-5 | AstroDatabank News |
| ro-space-columbia-disaster-sts-107 | space flight | 2003-02-01 | 08:59:32 UTC-5 | Space: Columbia Disaster (STS 107) |
| ro-accident-fire-in-ri-nightclub | fire | 2003-02-20 | 23:00:00 UTC-5 | Accident: Fire in RI Nightclub |
| ro-military-iraq-war-2003 | military | 2003-03-20 | 05:33:00 UTC+3 | Military: Iraq War 2003 |
| ro-space-mars-spirit-launched | space flight | 2003-06-10 | 13:59:00 UTC-4 | Space: Mars "Spirit" Launched |
| ro-space-opportunity-mars-exploration-rover | space flight | 2003-07-07 | 11:18:15 UTC-4 | Space: Opportunity (Mars Exploration Rover) |
| ro-entertainment-the-o-c | TV show | 2003-08-05 | 21:00:00 UTC-4 | Entertainment: The O.C. |
| ro-communications-power-failure | other | 2003-08-14 | 16:06:00 UTC-4 | Communications: Power Failure |
| ro-celestial-mars-2003 | celestial | 2003-08-27 | 09:51:00 UTC+0 | Celestial: Mars 2003 |
| ro-entertainment-two-and-a-half-men | entertainment | 2003-09-22 | 21:30:00 UTC-4 | Entertainment: Two and a Half Men |
| ro-entertainment-arrested-development | TV show | 2003-11-02 | 21:30:00 UTC-5 | Entertainment: Arrested Development |
| ro-celestial-sedna-discovery | celestial | 2003-11-19 | 10:50:00 UTC-8 | Celestial: Sedna Discovery |
| ro-plane-crash-flash-airlines-flight-604-2004 | air crash | 2004-01-03 | 04:45:06 UTC+2 | Plane Crash: Flash Airlines Flight 604 (2004) |
| ro-historic-queen-mary-2-launch | space flight | 2004-01-08 | 16:40:00 UTC+0 | Historic: Queen Mary 2 Launch |
| ro-astrology-aya | organization | 2004-01-11 | 12:15:00 UTC-7 | Astrology: AYA |
| ro-entertainment-the-l-word | TV show | 2004-01-18 | 22:00:00 UTC-5 | Entertainment: The L Word |
| ro-sports-super-bowl-2004-38 | sports event | 2004-02-01 | 18:25:00 UTC-6 | Sports: Super Bowl 2004 #38 |
| ro-space-rosetta-spacecraft | space flight | 2004-03-02 | 07:17:00 UTC+0 | Space: Rosetta (spacecraft) |
| ro-terrorist-madrid-train-bombs | terror attack | 2004-03-11 | 07:39:00 UTC+1 | Terrorist: Madrid Train Bombs |
| ro-historic-spaceshipone | space flight | 2004-06-21 | 07:51:00 UTC-7 | Historic: SpaceShipOne |
| ro-space-cassini-huygens-reaches-saturn | space flight | 2004-06-30 | 19:36:00 UTC-7 | Space: Cassini-Huygens Reaches Saturn |
| ro-sports-2004-summer-olympics-athens | sports event | 2004-08-13 | 23:46:00 UTC+3 | Sports: 2004 Summer Olympics, Athens |
| ro-business-google-first-trade | business | 2004-08-19 | 11:55:00 UTC-4 | Business: Google First Trade |
| ro-business-google-market-start | business | 2004-08-19 | 09:30:00 UTC-4 | Business: Google Market Start |
| ro-plane-crash-two-in-russia | air crash | 2004-08-24 | 22:56:00 UTC+4 | Plane Crash: Two in Russia |
| ro-terrorist-russian-school | terror attack | 2004-09-01 | 09:00:00 UTC+4 | Terrorist: Russian School |
| ro-entertainment-lost | TV show | 2004-09-22 | 20:00:00 UTC-4 | Entertainment: Lost |
| ro-political-bush-kerry-debates | political | 2004-09-30 | 21:00:00 UTC-4 | Political: Bush-Kerry Debates |
| ro-entertainment-boston-legal | entertainment | 2004-10-03 | 22:00:00 UTC-4 | Entertainment: Boston Legal |
| ro-entertainment-desperate-housewives | entertainment | 2004-10-03 | 21:00:00 UTC-4 | Entertainment: Desperate Housewives |
| ro-terrorist-car-bombs-baghdad | terror attack | 2004-10-03 | 08:45:00 UTC+3 | Terrorist: Car Bombs Baghdad |
| ro-accident-gas-explosions-in-france | explosion | 2004-12-26 | 17:00:00 UTC+1 | Accident: gas explosions in France |
| ro-accident-buenos-aires-fire | fire | 2004-12-30 | 23:00:00 UTC-3 | Accident: Buenos Aires Fire |
| ro-celestial-eris-discovery | celestial | 2005-01-05 | 11:20:00 UTC-8 | Celestial: Eris Discovery |
| ro-business-youtube-website | business | 2005-02-14 | 21:13:12 UTC-8 | Business: YouTube Website |
| ro-terrorist-suicide-bomb-blast | terror attack | 2005-02-28 | 08:35:00 UTC+3 | Terrorist: Suicide Bomb Blast |
| ro-entertainment-the-office-usa | TV show | 2005-03-24 | 21:30:00 UTC-5 | Entertainment: The Office (USA) |
| ro-entertainment-grey-s-anatomy | TV show | 2005-03-27 | 22:00:00 UTC-5 | Entertainment: Grey's Anatomy |
| ro-business-youtube-first-video | business | 2005-04-23 | 20:27:00 UTC-7 | Business: YouTube (first video) |
| ro-transportation-train-crash | rail accident | 2005-04-25 | 09:20:00 UTC+9 | Transportation: Train Crash |
| ro-aviation-airbus-a380-maiden-flight | aviation | 2005-04-27 | 10:29:00 UTC+2 | Aviation: Airbus A380 Maiden Flight |
| ro-nature-banning-earthquake-s-california-2005 | earthquake | 2005-06-16 | 13:54:00 UTC-7 | Nature: Banning Earthquake:S-California 2005 |
| ro-nature-earthquake-series-california-2005-iv | earthquake | 2005-06-16 | 22:41:00 UTC-7 | Nature: Earthquake series:California 2005 (IV) |
| ro-nature-yucaipa-earthquake-s-california-2005 | earthquake | 2005-06-16 | 13:53:00 UTC-7 | Nature: Yucaipa Earthquake:S-California 2005 |
| ro-nature-earthquake-calif-49781 | earthquake | 2005-06-16 | 04:11:00 UTC-7 | Nature: Earthquake Calif 49781 |
| ro-nature-earthquake-series-california-2005-i | earthquake | 2005-06-16 | 22:22:00 UTC-7 | Nature: Earthquake series:California 2005 (I) |
| ro-terrorist-london-tube-bombing | terror attack | 2005-07-07 | 08:51:00 UTC+1 | Terrorist: London Tube Bombing |
| ro-terrorist-iraq-mosque-bombed | terror attack | 2005-07-16 | 20:00:00 UTC+4 | Terrorist: Iraq Mosque Bombed |
| ro-terrorist-egyptian-car-bombs | terror attack | 2005-07-23 | 01:00:00 UTC+3 | Terrorist: Egyptian car bombs |
| ro-space-discovery-return-to-flight-2005 | space flight | 2005-07-26 | 10:39:00 UTC-4 | Space: Discovery "Return to Flight" 2005 |
| ro-nature-hurricane-katrina | cyclone | 2005-08-29 | 06:10:00 UTC-5 | Nature: Hurricane Katrina |
| ro-entertainment-bones | TV show | 2005-09-13 | 20:00:00 UTC-4 | Entertainment: Bones |
| ro-entertainment-supernatural | TV show | 2005-09-13 | 21:00:00 UTC-4 | Entertainment: Supernatural |
| ro-terrorist-bali-explosion-05 | terror attack | 2005-10-01 | 19:30:00 UTC+8 | Terrorist: Bali Explosion '05 |
| ro-social-brighton-and-hove-astrology-circle | organization | 2005-10-15 | 20:00:00 UTC+1 | Social: Brighton and Hove Astrology Circle |
| ro-terror-al-hadithah-massacre | terror attack | 2005-11-19 | 07:15:00 UTC+3 | Terror: Al-Hadithah massacre |
| ro-plane-crash-west-tisbury-ma | air crash | 2005-11-27 | 12:10:00 UTC-5 | Plane Crash: West Tisbury, MA |
| ro-space-new-horizons-space-probe | space flight | 2006-01-19 | 14:00:00 UTC-5 | Space: New Horizons (space probe) |
| ro-entertainment-high-school-musical | entertainment | 2006-01-20 | 20:00:00 UTC-5 | Entertainment: High School Musical |
| ro-sports-2006-winter-olympics-turin | sports event | 2006-02-10 | 22:05:00 UTC+1 | Sports: 2006 Winter Olympics, Turin |
| ro-entertainment-big-love | TV show | 2006-03-12 | 22:00:00 UTC-5 | Entertainment: Big Love |
| ro-celestial-aries-ingress-2006 | celestial | 2006-03-20 | 13:26:00 UTC-5 | Celestial: Aries Ingress 2006 |
| ro-business-twitter-s-first-tweet | business | 2006-03-21 | 12:50:00 UTC-8 | Business: Twitter's first tweet |
| ro-historic-three-gorges-dam | historic | 2006-05-20 | 14:00:00 UTC+8 | Historic: Three Gorges Dam |
| ro-celestial-cancer-ingress-2006 | celestial | 2006-06-21 | 08:25:00 UTC-4 | Celestial: Cancer Ingress 2006 |
| ro-kidnapping-gilad-shalit | crime | 2006-06-25 | 05:30:00 UTC+3 | Kidnapping: Gilad Shalit |
| ro-space-discovery-2006 | space flight | 2006-07-04 | 14:38:00 UTC-4 | Space: Discovery 2006 |
| ro-accident-forsmark-failure | accident | 2006-07-25 | 13:21:00 UTC+2 | Accident: Forsmark failure |
| ro-historic-iau-resolution-dwarf-planets | air crash | 2006-08-24 | 15:34:00 UTC+2 | Historic: IAU Resolution: dwarf planets |
| ro-piratenpartei | political | 2006-09-10 | 10:30:00 UTC+2 | Piratenpartei |
| ro-entertainment-brothers-sisters | TV show | 2006-09-24 | 22:00:00 UTC-4 | Entertainment: Brothers + Sisters |
| ro-entertainment-heroes | TV show | 2006-09-25 | 21:00:00 UTC-4 | Entertainment: Heroes |
| ro-entertainment-dexter | TV show | 2006-10-01 | 22:00:00 UTC-4 | Entertainment: Dexter |
| ro-business-wikileaks | business | 2006-10-04 | 05:54:19 UTC+0 | Business: Wikileaks |
| ro-entertainment-30-rock | TV show | 2006-10-11 | 20:00:00 UTC-4 | Entertainment: 30 Rock |
| ro-business-apple-iphone | business | 2007-01-09 | 09:43:30 UTC-8 | Business: Apple iPhone |
| ro-business-astrology-ss-website | business | 2007-01-28 | 13:58:00 UTC-5 | Business: Astrology SS Website |
| ro-nature-tornado-alabama | tornado | 2007-03-01 | 13:10:00 UTC-6 | Nature: Tornado Alabama |
| ro-accident-bus-crash | accident | 2007-03-02 | 05:30:00 UTC-5 | Accident: Bus Crash |
| ro-celestial-aries-ingress-2007 | celestial | 2007-03-21 | 03:07:00 UTC+3 | Celestial: Aries Ingress 2007 |
| ro-shooting-spree-virginia-tech | shooting | 2007-04-16 | 07:15:00 UTC-4 | Shooting Spree: Virginia Tech |
| ro-nature-tornado-greensburg-ks | tornado | 2007-05-04 | 21:30:00 UTC-5 | Nature: Tornado Greensburg KS |
| ro-entertainment-mad-men | entertainment | 2007-07-19 | 22:00:00 UTC-4 | Entertainment: Mad Men |
| ro-accident-bridge-collapse-mn | accident | 2007-08-01 | 18:05:00 UTC-5 | Accident: Bridge Collapse MN |
| ro-accident-mine-cave-in-utah | other | 2007-08-06 | 03:50:00 UTC-6 | Accident: Mine Cave-In Utah |
| ro-space-endeavour-sts-118-2007 | space flight | 2007-08-08 | 18:36:42 UTC-4 | Space: Endeavour STS-118 (2007) |
| ro-entertainment-high-school-musical-2 | entertainment | 2007-08-17 | 20:00:00 UTC-4 | Entertainment: High School Musical 2 |
| ro-entertainment-gossip-girl | TV show | 2007-09-19 | 21:00:00 UTC-4 | Entertainment: Gossip Girl |
| ro-entertainment-the-big-bang-theory | entertainment | 2007-09-24 | 20:30:00 UTC-4 | Entertainment: The Big Bang Theory |
| ro-space-dawn-spacecraft | space flight | 2007-09-27 | 07:34:00 UTC-4 | Space: Dawn (spacecraft) |
| ro-celestial-winter-solstice2007 | celestial | 2007-12-22 | 01:08:00 UTC-5 | Celestial: Winter Solstice2007 |
| ro-entertainment-breaking-bad | TV show | 2008-01-20 | 22:00:00 UTC-5 | Entertainment: Breaking Bad |
| ro-prognosefokus | historic | 2008-05-18 | 11:07:00 UTC+2 | Prognosefokus |
| ro-law-fisa-08-amendment-senate | law | 2008-07-09 | 14:47:00 UTC-4 | Law: FISA '08 Amendment Senate |
| ro-sports-2008-summer-olympics-beijing | sports event | 2008-08-08 | 20:00:00 UTC+8 | Sports: 2008 Summer Olympics, Beijing |
| ro-business-whatsapp-inc | business | 2008-09-04 | 05:39:12 UTC-7 | Business: WhatsApp Inc. |
| ro-shooting-spree-kauhajoki-school | shooting | 2008-09-23 | 10:40:00 UTC+3 | Shooting Spree: Kauhajoki school |
| ro-terrorist-attacks-mumbai | terror attack | 2008-11-26 | 21:20:00 UTC+5.5 | Terrorist Attacks Mumbai |
| ro-plane-crash-ny-la-guardia | air crash | 2009-01-15 | 15:31:00 UTC-5 | Plane Crash: NY La Guardia |
| ro-nature-cyclone-klaus-2009 | cyclone | 2009-01-24 | 05:00:00 UTC+1 | Nature: Cyclone Klaus (2009) |
| ro-entertainment-rupaul-s-drag-race | entertainment | 2009-02-02 | 22:00:00 UTC-5 | Entertainment: RuPaul's Drag Race |
| ro-plane-crash-clarence-ctr-ny | air crash | 2009-02-12 | 22:20:00 UTC-5 | Plane Crash: Clarence Ctr NY |
| ro-law-am-recovery-reinvestment | law | 2009-02-17 | 13:23:00 UTC-7 | Law: Am.Recovery/Reinvestment |
| ro-plane-crash-turkish-airlines-flight-1951-2009 | air crash | 2009-02-25 | 10:31:00 UTC+1 | Plane Crash: Turkish Airlines Flight 1951 (2009) |
| ro-entertainment-parks-and-recreation | TV show | 2009-04-09 | 20:30:00 UTC-4 | Entertainment: Parks and Recreation |
| ro-entertainment-glee | TV show | 2009-05-19 | 21:00:00 UTC-4 | Entertainment: Glee |
| ro-plane-departure-air-france-flight-447-2009 | air crash | 2009-05-31 | 19:03:00 UTC-3 | Plane Departure: Air France Flight 447 (2009) |
| ro-plane-crash-yemenia-air-flight-626-2009 | air crash | 2009-06-30 | 01:51:00 UTC+3 | Plane Crash: Yemenia Air Flight 626 (2009) |
| ro-entertainment-archer | entertainment | 2009-09-17 | 22:30:00 UTC-4 | Entertainment: Archer |
| ro-entertainment-cougar-town | TV show | 2009-09-23 | 21:30:00 UTC-4 | Entertainment: Cougar Town |
| ro-entertainment-modern-family | TV show | 2009-09-23 | 21:00:00 UTC-4 | Entertainment: Modern Family |
| ro-military-ft-hood-massacre | terror attack | 2009-11-05 | 13:30:00 UTC-6 | Military: Ft. Hood Massacre |
| ro-aviation-airbus-a400m | air crash | 2009-12-11 | 10:16:00 UTC+1 | Aviation: Airbus A400M |
| ro-aviation-boeing-787-maiden-flight | aviation | 2009-12-15 | 10:27:00 UTC-8 | Aviation: Boeing 787 Maiden Flight |
| ro-historic-burj-khalifa | historic | 2010-01-04 | 19:55:00 UTC+4 | Historic: Burj Khalifa |
| ro-business-apple-ipad | business | 2010-01-27 | 13:10:00 UTC-8 | Business: Apple iPad |
| ro-sports-2010-winter-olympics-vancouver | sports event | 2010-02-12 | 20:31:00 UTC-8 | Sports: 2010 Winter Olympics, Vancouver |
| ro-nature-volcano-iceland-2010 | volcano | 2010-03-21 | 00:05:00 UTC+0 | Nature: Volcano Iceland (2010) |
| ro-law-health-insurance-reform | law | 2010-03-23 | 11:56:00 UTC-4 | Law: Health Insurance Reform |
| ro-accident-bp-oil-rig-explosion | explosion | 2010-04-20 | 22:00:00 UTC-5 | Accident: BP Oil Rig Explosion |
| ro-plane-crash-afriqiyah-airways-flight-771-2010 | air crash | 2010-05-12 | 06:01:00 UTC+2 | Plane Crash: Afriqiyah Airways Flight 771 (2010) |
| ro-nature-flood-draguignan-2010 | flood | 2010-06-15 | 10:00:00 UTC+2 | Nature: Flood Draguignan (2010) |
| ro-historic-instagram | historic | 2010-07-16 | 10:26:00 UTC-7 | Historic: Instagram |
| ro-accident-copiapo-mining-collapse | accident | 2010-08-05 | 14:00:00 UTC-4 | Accident: Copiapo mining collapse |
| ro-entertainment-the-talk | entertainment | 2010-10-18 | 14:00:00 UTC-4 | Entertainment: The Talk |
| ro-law-repeal-don-t-ask | law | 2010-12-22 | 09:35:00 UTC-5 | Law: Repeal Don't Ask |
| ro-shooting-spree-tucson-az | shooting | 2011-01-08 | 10:10:00 UTC-7 | Shooting Spree: Tucson AZ |
| ro-entertainment-bob-s-burgers | entertainment | 2011-01-09 | 20:30:00 UTC-5 | Entertainment: Bob's Burgers |
| ro-political-egyptian-protest | political | 2011-01-25 | 12:00:00 UTC+2 | Political: Egyptian Protest |
| ro-political-un-decl-re-libya | political | 2011-03-17 | 19:20:00 UTC-4 | Political: UN Decl Re Libya |
| ro-entertainment-game-of-thrones | TV show | 2011-04-17 | 20:30:00 UTC-4 | Entertainment: Game of Thrones |
| ro-space-endeavour-space-shuttle | space flight | 2011-05-16 | 08:56:00 UTC-4 | Space: Endeavour (Space Shuttle) |
| ro-nature-tornado-reading-ks | tornado | 2011-05-21 | 21:15:00 UTC-5 | Nature: Tornado Reading, KS |
| ro-nature-tornado-joplin-mo | tornado | 2011-05-22 | 18:00:00 UTC-5 | Nature: Tornado Joplin, MO |
| ro-entertainment-suits | TV show | 2011-06-23 | 22:00:00 UTC-4 | Entertainment: Suits |
| ro-law-ny-same-sex-marriage-act | law | 2011-06-24 | 23:55:00 UTC-4 | Law: NY Same-Sex Marriage Act |
| ro-space-atlantis-sts-135-final-mission | space flight | 2011-07-08 | 11:29:00 UTC-4 | Space: Atlantis STS-135 (Final mission) |
| ro-shooting-spree-utya-island | shooting | 2011-07-22 | 17:22:00 UTC+2 | Shooting Spree: Utøya Island |
| ro-terrorist-attack-oslo-bombing | terror attack | 2011-07-22 | 15:26:00 UTC+2 | Terrorist Attack: Oslo bombing |
| ro-accident-tanzanian-ferry-mv-spice-isander-i-capsi | shipwreck | 2011-09-10 | 01:00:00 UTC+3 | Accident: Tanzanian ferry MV Spice Isander I capsi |
| ro-space-curiosity-mars-science-laboratory | space flight | 2011-11-26 | 10:02:00 UTC-5 | Space: Curiosity (Mars Science Laboratory) |
| ro-accident-costa-concordia-capsize | shipwreck | 2012-01-13 | 20:45:05 UTC+1 | Accident: Costa Concordia capsize |
| ro-accident-bus-crash-switzerland | accident | 2012-03-13 | 21:15:00 UTC+1 | Accident: Bus Crash Switzerland |
| ro-shooting-spree-oakland | shooting | 2012-04-02 | 10:30:00 UTC-7 | Shooting spree: Oakland |
| ro-business-facebook-first-trade | business | 2012-05-18 | 11:30:00 UTC-4 | Business: Facebook, First Trade |
| ro-historic-the-shard | historic | 2012-07-05 | 15:00:00 UTC+1 | Historic: The Shard |
| ro-sports-2012-summer-olympics-london | sports event | 2012-07-28 | 00:21:00 UTC+1 | Sports: 2012 Summer Olympics, London |
| ro-shooting-spree-annecy-chevaline | shooting | 2012-09-05 | 15:45:00 UTC+2 | Shooting Spree: Annecy Chevaline |
| ro-shooting-spree-sandy-hook-newtown-conn | shooting | 2012-12-14 | 09:35:00 UTC-5 | Shooting Spree: Sandy Hook (Newtown) Conn. |
| ro-entertainment-house-of-cards-american-tv-series | TV show | 2013-02-01 | 00:00:00 UTC-5 | Entertainment: House of Cards (American TV series) |
| ro-terrorist-boston-marathon-bombings | terror attack | 2013-04-15 | 14:50:00 UTC-4 | Terrorist: Boston Marathon Bombings |
| ro-accidents-west-fertilizer-company-explosion-waco | explosion | 2013-04-17 | 07:50:38 UTC-5 | Accidents: West Fertilizer Company explosion (Waco |
| ro-accident-savar-building-collapse | accident | 2013-04-24 | 08:45:00 UTC+6 | Accident: Savar building collapse |
| ro-aviation-airbus-a350-maiden-flight | aviation | 2013-06-14 | 10:00:00 UTC+2 | Aviation: Airbus A350 Maiden Flight |
| ro-railroad-derailment-lac-megantic-quebec-canada | rail accident | 2013-07-06 | 01:14:00 UTC-4 | Railroad derailment Lac-Mégantic, Québec (Canada) |
| ro-entertainment-orange-is-the-new-black | entertainment | 2013-07-11 | 00:01:00 UTC-7 | Entertainment: Orange Is the New Black |
| ro-railroad-derailment-bretigny-sur-orge-france | rail accident | 2013-07-12 | 17:14:00 UTC+2 | Railroad derailment, Brétigny-sur-Orge (France) |
| ro-entertainment-the-real | entertainment | 2013-07-15 | 12:00:00 UTC-4 | Entertainment: The Real |
| ro-train-derailment-santiago-de-compostela | rail accident | 2013-07-24 | 20:41:00 UTC+2 | Train derailment, Santiago de Compostela |
| ro-accident-2013-monteforte-irpino-bus-crash | accident | 2013-07-28 | 20:30:00 UTC+2 | Accident: 2013 Monteforte Irpino bus crash |
| ro-space-cygnus-spacecraft-first-launch | space flight | 2013-09-18 | 10:58:00 UTC-4 | Space: Cygnus (spacecraft, first launch) |
| ro-terrorist-attack-westgate-shopping-mail-nairobi | terror attack | 2013-09-21 | 12:35:00 UTC+3 | Terrorist Attack Westgate Shopping Mail Nairobi |
| ro-accident-riga-shopping-centre-roof-collapse | accident | 2013-11-21 | 17:41:00 UTC+2 | Accident: Riga shopping centre roof collapse |
| ro-entertainment-transparent | TV show | 2014-02-06 | 00:01:00 UTC-5 | Entertainment: Transparent |
| ro-sports-2014-winter-olympics-sochi | sports event | 2014-02-07 | 22:27:00 UTC+4 | Sports: 2014 Winter Olympics, Sochi |
| ro-plane-crash-malaysia-airlines-flight-370 | air crash | 2014-03-08 | 00:41:00 UTC+8 | Plane Crash: Malaysia Airlines Flight 370 |
| ro-accident-great-fire-of-valparaiso | fire | 2014-04-12 | 16:40:00 UTC-3 | Accident: great fire of Valparaiso |
| ro-accident-korean-ferry-sewol-capsized | shipwreck | 2014-04-16 | 08:49:40 UTC+9 | Accident: Korean ferry Sewol capsized |
| ro-mortality-2014-odessa-clashes | accident | 2014-05-02 | 19:44:00 UTC+3 | Mortality: 2014 Odessa clashes |
| ro-accident-soma-mine-disaster | accident | 2014-05-13 | 15:10:00 UTC+3 | Accident: Soma mine disaster |
| ro-jewish-museum-of-belgium-shooting | shooting | 2014-05-24 | 15:50:00 UTC+2 | Jewish Museum of Belgium shooting |
| ro-historic-e-elt-groundbreaking | historic | 2014-06-19 | 13:45:00 UTC-4 | Historic: E-ELT Groundbreaking |
| ro-accident-moscow-metro-derailment | rail accident | 2014-07-15 | 08:45:00 UTC+4 | Accident: Moscow metro derailment |
| ro-plane-crash-2014-malaysia-airlines-flight-mh17 | air crash | 2014-07-17 | 16:20:03 UTC+3 | Plane Crash: 2014 Malaysia Airlines Flight MH17 |
| ro-plane-crash-transasia-airways-flight-222-2014 | air crash | 2014-07-23 | 19:06:00 UTC+8 | Plane Crash: TransAsia Airways Flight 222 (2014) |
| ro-plane-crash-air-algerie-flight-5017-2014 | air crash | 2014-07-24 | 01:47:15 UTC+0 | Plane Crash: Air Algérie Flight 5017 (2014) |
| ro-accident-kaohsiung-gas-explosions | explosion | 2014-07-31 | 23:57:00 UTC+8 | Accident: Kaohsiung gas explosions |
| ro-shooting-of-michael-brown-ferguson | shooting | 2014-08-09 | 12:01:00 UTC-5 | Shooting of Michael Brown, Ferguson |
| ro-plane-crash-sepahan-air-flight-5915-2014 | air crash | 2014-08-10 | 09:18:00 UTC+4.5 | Plane crash: Sepahan Air Flight 5915 (2014) |
| ro-sports-invictus-games | sports event | 2014-09-10 | 20:00:00 UTC+1 | Sports: Invictus Games |
| ro-entertainment-gotham | TV show | 2014-09-22 | 20:00:00 UTC-4 | Entertainment: Gotham |
| ro-entertainment-black-ish | TV show | 2014-09-24 | 21:31:00 UTC-4 | Entertainment: Black-ish |
| ro-shooting-spree-ottawa-parliament-hill | shooting | 2014-10-22 | 09:53:00 UTC-4 | Shooting Spree: Ottawa Parliament Hill |
| ro-accident-cygnus-explosion-spacecraft | space flight | 2014-10-29 | 18:22:38 UTC-4 | Accident: Cygnus explosion (spacecraft)) |
| ro-accident-spaceship-two-explosion | space flight | 2014-10-31 | 17:12:00 UTC+0 | Accident: Spaceship Two Explosion |
| ro-space-orion-spacecraft | space flight | 2014-12-05 | 07:05:00 UTC-5 | Space: Orion (spacecraft) |
| ro-terrorist-sydney-hostage-crisis-2014 | terror attack | 2014-12-15 | 09:44:00 UTC+11 | Terrorist: Sydney Hostage Crisis 2014 |
| ro-terrorist-peshawar-school-shooting-spree | terror attack | 2014-12-16 | 10:30:00 UTC+5 | Terrorist: Peshawar School Shooting Spree |
| ro-accident-ferry-norman-atlantic-fire | shipwreck | 2014-12-28 | 06:00:00 UTC+2 | Accident: Ferry Norman Atlantic fire |
| ro-plane-crash-airasia-flight-8501-2014 | air crash | 2014-12-28 | 06:24:00 UTC+7 | Plane Crash: AirAsia Flight 8501 (2014) |
| ro-terrorist-shooting-at-charlie-hebdo-journal-2015 | terror attack | 2015-01-07 | 11:31:00 UTC+1 | Terrorist: Shooting at Charlie Hebdo Journal (2015 |
| ro-terrorist-dammartin-printing-house-shooting | terror attack | 2015-01-09 | 16:56:00 UTC+1 | Terrorist: Dammartin printing house shooting |
| ro-terrorist-paris-supermarket-shooting | terror attack | 2015-01-09 | 13:00:00 UTC+1 | Terrorist: Paris Supermarket Shooting |
| ro-inauguration-paris-philharmonie | inauguration | 2015-01-14 | 21:00:00 UTC+1 | Inauguration: Paris Philharmonie |
| ro-plane-crash-hellenic-air-force-f-16 | air crash | 2015-01-26 | 15:16:00 UTC+1 | Plane crash: Hellenic Air Force F-16 |
| ro-plane-crash-transasia-airways-flight-235 | air crash | 2015-02-04 | 10:55:00 UTC+8 | Plane crash: TransAsia Airways Flight 235 |
| ro-helicopter-crash-villa-castelli-collision | air crash | 2015-03-09 | 17:15:00 UTC-3 | Helicopter crash: Villa Castelli collision |
| ro-historic-seat-of-the-european-central-bank | historic | 2015-03-18 | 12:04:00 UTC+1 | Historic: Seat of the European Central Bank |
| ro-plane-crash-germanwings-flight-4u9525-2015 | air crash | 2015-03-24 | 10:40:47 UTC+1 | Plane Crash: Germanwings Flight 4U9525 (2015) |
| ro-space-progress-spacecraft-launch | space flight | 2015-04-28 | 07:09:00 UTC+6 | Space: Progress spacecraft (launch) |
| ro-entertainment-grace-and-frankie | TV show | 2015-05-08 | 00:00:00 UTC-4 | Entertainment: Grace and Frankie |
| ro-2015-philadelphia-train-derailment | rail accident | 2015-05-12 | 21:23:00 UTC-4 | 2015 Philadelphia train derailment |
| ro-les-republicains | political | 2015-05-30 | 21:10:00 UTC+2 | Les Républicains |
| ro-accident-sinking-of-kim-nirvana-ferry | shipwreck | 2015-07-02 | 12:50:00 UTC+8 | Accident: Sinking of Kim Nirvana ferry |
| ro-accident-2015-tianjin-explosion | explosion | 2015-08-12 | 23:36:00 UTC+8 | Accident: 2015 Tianjin explosion |
| ro-terrorist-2015-thalys-attack | terror attack | 2015-08-21 | 17:50:00 UTC+2 | Terrorist: 2015 Thalys attack |
| ro-accident-shoreham-airshow-crash | air crash | 2015-08-22 | 13:22:00 UTC+1 | Accident: Shoreham Airshow Crash |
| ro-shooting-spree-2015-murders-of-alison-and-adam | shooting | 2015-08-26 | 06:46:00 UTC-4 | Shooting Spree: 2015 Murders of Alison and Adam |
| ro-science-collision-of-black-holes | science | 2015-09-14 | 09:50:00 UTC+0 | Science: Collision of Black Holes |
| ro-accident-mecca-hajj-stampede-2015 | accident | 2015-09-24 | 09:00:00 UTC+3 | Accident: Mecca Hajj stampede (2015) |
| ro-accident-collision-puisseguin | accident | 2015-10-23 | 07:30:00 UTC+2 | Accident: Collision Puisseguin |
| ro-plane-crash-kogalymavia-flight-9268-bombing | terror attack | 2015-10-31 | 06:13:00 UTC+2 | Plane Crash: Kogalymavia flight 9268 bombing |
| ro-terrorist-attacks-paris-november-2015 | terror attack | 2015-11-13 | 21:17:00 UTC+1 | Terrorist: Attacks Paris November 2015 |
| ro-2015-eckwersheim-tgv-derailment | rail accident | 2015-11-14 | 15:15:00 UTC+1 | 2015 Eckwersheim TGV derailment |
| ro-accident-bad-aibling-rail-collision | rail accident | 2016-02-09 | 06:48:00 UTC+1 | Accident: Bad Aibling rail collision |
| ro-entertainment-fuller-house | TV show | 2016-02-26 | 03:00:00 UTC-5 | Entertainment: Fuller House |
| ro-space-exomars | space flight | 2016-03-14 | 09:31:00 UTC+0 | Space: ExoMars |
| ro-plane-crash-flydubai-flight-981 | air crash | 2016-03-19 | 03:42:00 UTC+3 | Plane Crash: Flydubai Flight 981 |
| ro-plane-crash-egyptair-flight-804 | air crash | 2016-05-19 | 02:33:00 UTC+3 | Plane Crash: EgyptAir Flight 804 |
| ro-historic-gotthard-base-tunnel | historic | 2016-06-01 | 12:18:00 UTC+2 | Historic: Gotthard Base Tunnel |
| ro-terrorist-2016-orlando-nightclub-shooting | terror attack | 2016-06-12 | 02:02:00 UTC-4 | Terrorist: 2016 Orlando Nightclub Shooting |
| ro-terrorist-2016-nice-truck-attack | terror attack | 2016-07-14 | 22:30:00 UTC+2 | Terrorist: 2016 Nice truck attack |
| ro-sports-2016-summer-olympics-rio-de-janeiro | sports event | 2016-08-05 | 23:27:00 UTC-3 | Sports: 2016 Summer Olympics, Rio de Janeiro |
| ro-nuclear-test-north-korea-2016 | nuclear test | 2016-09-09 | 00:30:01 UTC+0 | Nuclear:Test North Korea 2016 |
| ro-entertainment-this-is-us | TV show | 2016-09-20 | 22:00:00 UTC-4 | Entertainment: This Is Us |
| ro-entertainment-the-crown | TV show | 2016-11-01 | 00:00:00 UTC+0 | Entertainment: The Crown |
| ro-plane-crash-colombia-2016 | air crash | 2016-11-28 | 22:00:00 UTC-5 | Plane Crash: Colombia (2016) |
| ro-plane-crash-2016-tupolev-154 | air crash | 2016-12-25 | 05:27:00 UTC+3 | Plane crash: 2016 Tupolev 154 |
| ro-terrorist-2017-westminster-attack | terror attack | 2017-03-22 | 14:38:00 UTC+0 | Terrorist: 2017 Westminster Attack |
| ro-nature-eruption-etna-2017 | volcano | 2017-04-19 | 18:05:00 UTC+0 | Nature:Eruption:Etna 2017 |
| ro-terrorism-2017-shooting-of-paris-police-officers | terror attack | 2017-04-20 | 21:00:00 UTC+2 | Terrorism: 2017 shooting of Paris police officers |
| ro-entertainment-the-handmaid-s-tale-tv-series | entertainment | 2017-04-26 | 00:00:00 UTC-4 | Entertainment: The Handmaid's Tale (TV series) |
| ro-historic-currencies-le-farinet | historic | 2017-05-13 | 13:13:00 UTC+2 | Historic: Currencies: Le Farinet |
| ro-terrorist-2017-manchester-arena-bombing | terror attack | 2017-05-22 | 22:33:00 UTC+1 | Terrorist: 2017 Manchester Arena bombing |
| ro-terrorist-june-2017-london-attacks | terror attack | 2017-06-03 | 22:05:00 UTC+1 | Terrorist: June 2017 London attacks |
| ro-disaster-grenfell-tower-fire | fire | 2017-06-14 | 00:56:00 UTC+1 | Disaster: Grenfell Tower fire |
| ro-entertainment-ozark | TV show | 2017-07-21 | 03:00:00 UTC-4 | Entertainment: Ozark |
| ro-disaster-charlottesville-car-attack | terror attack | 2017-08-12 | 13:42:00 UTC-4 | Disaster: Charlottesville car attack |
| ro-terrorist-2017-barcelona-attacks | terror attack | 2017-08-17 | 16:56:00 UTC+2 | Terrorist: 2017 Barcelona attacks |
| ro-nuclear-earthquake-north-korea-2017 | nuclear test | 2017-09-03 | 03:30:01 UTC+0 | Nuclear:Earthquake North Korea:2017 |
| ro-nature-hurricane-irma | cyclone | 2017-09-06 | 02:00:00 UTC-4 | Nature: Hurricane Irma |
| ro-terrorist-2017-las-vegas-strip-mass-shooting | terror attack | 2017-10-01 | 22:05:00 UTC-7 | Terrorist: 2017 Las Vegas Strip mass shooting |
| ro-terrorist-2017-mogadishu-bombings | terror attack | 2017-10-14 | 15:25:00 UTC+3 | Terrorist: 2017 Mogadishu bombings |
| ro-terrorist-sutherland-springs-church-shooting | terror attack | 2017-11-05 | 11:20:00 UTC-6 | Terrorist: Sutherland Springs church shooting |
| ro-terrorist-2017-sinai-attack | terror attack | 2017-11-24 | 12:30:00 UTC+2 | Terrorist: 2017 Sinai Attack |
| ro-sports-2018-winter-olympics-pyeongchang | sports event | 2018-02-09 | 21:43:00 UTC+9 | Sports: 2018 Winter Olympics, Pyeongchang |
| ro-sports-2018-commonwealth-games-gold-coast | sports event | 2018-04-04 | 22:25:00 UTC+10 | Sports: 2018 Commonwealth Games, Gold Coast |
| ro-terrorist-2018-toronto-van-attack | terror attack | 2018-04-23 | 13:30:00 UTC-4 | Terrorist: 2018 Toronto van attack |
| ro-plane-crash-cubana-de-aviacion-flight-972 | air crash | 2018-05-18 | 12:08:00 UTC-4 | Plane Crash: Cubana de Aviacion, Flight 972 |
| ro-plane-crash-aeromexico-connect-flight-2431 | air crash | 2018-07-31 | 16:00:00 UTC-5 | Plane Crash: Aeromexico Connect Flight 2431 |
| ro-plane-crash-swiss-ju-air-vintage | air crash | 2018-08-04 | 16:56:00 UTC+2 | Plane Crash: Swiss Ju-Air Vintage |
| ro-space-parker-solar-probe | space flight | 2018-08-12 | 03:31:00 UTC-4 | Space: Parker Solar Probe |
| ro-accident-ponte-morandi-bridge-collapse-genoa | accident | 2018-08-14 | 11:36:00 UTC+2 | Accident: Ponte Morandi bridge collapse, Genoa |
| ro-plane-crash-lion-air-flight-610 | air crash | 2018-10-29 | 06:33:00 UTC+7 | Plane Crash: Lion Air Flight 610 |
| ro-accident-paris-trevise-gas-explosion | explosion | 2019-01-12 | 08:50:00 UTC+1 | Accident: Paris Trévise gas explosion |
| ro-disaster-brumadinho-dam-failure | flood | 2019-01-25 | 12:28:00 UTC-2 | Disaster: Brumadinho Dam failure |
| ro-plane-crash-ethiopian-airlines-flight-302 | air crash | 2019-03-10 | 08:44:00 UTC+3 | Plane Crash: Ethiopian Airlines Flight 302 |
| ro-terrorist-2019-christchurch-mosque-shootings | terror attack | 2019-03-15 | 13:40:00 UTC+13 | Terrorist: 2019 Christchurch mosque shootings |
| ro-historic-2019-notre-dame-de-paris-fire | fire | 2019-04-15 | 18:50:00 UTC+2 | Historic: 2019 Notre-Dame de Paris fire |
| ro-terrorist-2019-sri-lanka-easter-bombings | terror attack | 2019-04-21 | 08:45:00 UTC+5.5 | Terrorist: 2019 Sri Lanka Easter bombings |
| ro-entertainment-euphoria | TV show | 2019-06-16 | 22:00:00 UTC-4 | Entertainment: Euphoria |
| ro-mortality-2019-el-paso-shooting | shooting | 2019-08-03 | 10:38:00 UTC-6 | Mortality: 2019 El Paso shooting |
| ro-mortality-2019-dayton-shooting | shooting | 2019-08-04 | 01:05:00 UTC-4 | Mortality: 2019 Dayton shooting |
| ro-terrorism-paris-police-headquarters-stabbing | terror attack | 2019-10-03 | 12:53:00 UTC+2 | Terrorism: Paris police headquarters stabbing |
| ro-helicopter-crash-menaka-collision | air crash | 2019-11-25 | 18:38:00 UTC+0 | Helicopter crash: Ménaka collision |
| ro-terrorism-2019-london-bridge-stabbing | terror attack | 2019-11-29 | 13:58:00 UTC+0 | Terrorism: 2019 London Bridge stabbing |
| ro-plane-crash-bek-air-flight-2100-kazakhstan | air crash | 2019-12-27 | 07:22:00 UTC+6 | Plane Crash: Bek Air Flight 2100 Kazakhstan |
| ro-historic-covid-19-pandemic | historic | 2019-12-30 | 17:43:00 UTC+8 | Historic: COVID-19 pandemic |
| ro-plane-crash-uia-flight-752-tehran-2020 | air crash | 2020-01-08 | 06:14:00 UTC+3.5 | Plane Crash: UIA Flight 752 (Tehran, 2020) |
| ro-accident-2020-tarragona-explosion | explosion | 2020-01-14 | 18:40:00 UTC+1 | Accident: 2020 Tarragona explosion |
| ro-helicopter-crash-calabasas-california | air crash | 2020-01-26 | 09:45:00 UTC-8 | Helicopter Crash: Calabasas, California |
| ro-historic-brexit | historic | 2020-01-31 | 23:00:00 UTC+0 | Historic: Brexit |
| ro-entertainment-tiger-king | TV show | 2020-03-20 | 00:01:00 UTC-4 | Entertainment: Tiger King |
| ro-mortality-2020-nova-scotia-killings | accident | 2020-04-18 | 22:25:00 UTC-3 | Mortality: 2020 Nova Scotia killings |
| ro-plane-crash-pakistan-international-airlines | air crash | 2020-05-22 | 14:45:00 UTC+5 | Plane Crash: Pakistan International Airlines |
| ro-mortality-death-of-george-floyd | accident | 2020-05-25 | 20:37:00 UTC-5 | Mortality: Death of George Floyd |
| ro-space-crew-dragon-2 | space flight | 2020-05-30 | 15:22:00 UTC-4 | Space: Crew Dragon 2 |
| ro-historic-nantes-cathedral-fire-2020 | fire | 2020-07-18 | 07:40:00 UTC+2 | Historic: Nantes Cathedral fire 2020 |
| ro-space-mars-2020-rover-mission | space flight | 2020-07-30 | 07:50:00 UTC-4 | Space: Mars 2020 (Rover Mission) |
| ro-accident-2020-beirut-explosions | explosion | 2020-08-04 | 18:08:00 UTC+3 | Accident: 2020 Beirut explosions |
| ro-historic-abraham-accords-peace-agreement | historic | 2020-09-15 | 13:32:00 UTC-4 | Historic: Abraham Accords Peace Agreement |
| ro-accident-arecibo-telescope-collapse | accident | 2020-12-01 | 07:53:50 UTC-4 | Accident: Arecibo telescope collapse |
| ro-medical-first-covid-19-vaccination-in-uk | other | 2020-12-08 | 06:31:00 UTC+0 | Medical: First COVID-19 vaccination in UK |
| ro-historic-2021-siege-of-u-s-capitol | historic | 2021-01-06 | 14:11:00 UTC-5 | Historic: 2021 Siege of U.S. Capitol |
| ro-plane-crash-sriwijaya-air-flight-182 | air crash | 2021-01-09 | 14:40:00 UTC+7 | Plane Crash: Sriwijaya Air Flight 182 |
| ro-nature-2021-india-uttarakhand-glacier-burst | flood | 2021-02-07 | 10:45:00 UTC+5.5 | Nature: 2021 India Uttarakhand glacier burst |
| ro-accident-2021-mount-meron-crush | accident | 2021-04-30 | 00:50:00 UTC+3 | Accident: 2021 Mount Meron Crush |
| ro-accident-surfside-condominium-building-collapse | accident | 2021-06-24 | 01:23:00 UTC-4 | Accident: Surfside condominium building collapse |
| ro-sports-2020-summer-olympics-tokyo | sports event | 2021-07-23 | 23:15:00 UTC+9 | Sports: 2020 Summer Olympics, Tokyo |
| ro-space-inspiration4 | space flight | 2021-09-15 | 20:02:00 UTC-4 | Space: Inspiration4 |
| ro-historic-aukus | historic | 2021-09-16 | 07:00:00 UTC+10 | Historic: AUKUS |
| ro-space-james-webb-space-telescope | space flight | 2021-12-25 | 09:20:00 UTC-3 | Space: James Webb Space Telescope |
| ro-accident-2022-airbus-318-engine-fire-paris | air crash | 2022-01-21 | 20:45:00 UTC+1 | Accident: 2022 Airbus 318 engine fire, Paris |
| ro-sports-2022-winter-olympics-beijing | sports event | 2022-02-04 | 21:52:00 UTC+8 | Sports: 2022 Winter Olympics, Beijing |
| ro-mortality-2022-perpignan-explosion | explosion | 2022-02-14 | 01:30:00 UTC+1 | Mortality: 2022 Perpignan explosion |
| ro-military-2022-russian-invasion-of-ukraine | military | 2022-02-24 | 04:55:00 UTC+2 | Military: 2022 Russian invasion of Ukraine |
| ro-plane-crash-2022-china-eastern-airlines-flight-57 | air crash | 2022-03-21 | 14:22:00 UTC+8 | Plane Crash: 2022 China Eastern Airlines Flight 57 |
| ro-mortality-kramatorsk-railway-bombing | terror attack | 2022-04-08 | 10:24:00 UTC+3 | Mortality: Kramatorsk railway bombing |
| ro-shooting-spree-2022-robb-elementary-school | shooting | 2022-05-24 | 11:30:00 UTC-5 | Shooting Spree: 2022 Robb Elementary School |
| ro-terrorist-2022-oslo-shooting | terror attack | 2022-06-25 | 01:13:00 UTC+2 | Terrorist: 2022 Oslo shooting |
| ro-mortality-krementchuk-missile-attack | terror attack | 2022-06-27 | 15:50:00 UTC+3 | Mortality: Krementchuk missile attack |
| ro-sports-2022-commonwealth-games-birmingham | sports event | 2022-07-28 | 22:00:00 UTC+1 | Sports: 2022 Commonwealth Games, Birmingham |
| ro-2022-crimean-bridge-explosion | explosion | 2022-10-08 | 06:07:00 UTC+3 | 2022 Crimean Bridge explosion |
| ro-accident-seoul-halloween-crowd-crush | accident | 2022-10-29 | 22:20:00 UTC+9 | Accident: Seoul Halloween crowd crush |
| ro-shooting-spree-2022-colorado-springs-nightclub | shooting | 2022-11-19 | 23:55:00 UTC-7 | Shooting Spree: 2022 Colorado Springs nightclub |
