# ClimaTempo Scrapper
A simple climatempo web scrapper that gets climatology information about cities over the year.


### Usage:
    $ climat_scrapper: pip install -e .
    $ climat_scrapper: climat_scrapper [city_limit]

City limit defaults to 100 and can be overwriten:

    $ climat_scrapper: climat_scrapper 50


### Tabular Sample:
        Cidade Estado        Mês Minima (°C) Máxima (°C)  Precipitação (mm)
    Rio Branco   Acre    Janeiro         21°         31°                289
    Rio Branco   Acre  Fevereiro         21°         31°                285
    Rio Branco   Acre      Março         21°         31°                230
    Rio Branco   Acre      Abril         21°         31°                190
    Rio Branco   Acre       Maio         19°         31°                 93
    Rio Branco   Acre      Junho         18°         30°                 32
    Rio Branco   Acre      Julho         17°         31°                 44
    Rio Branco   Acre     Agosto         17°         33°                 38
    Rio Branco   Acre   Setembro         19°         33°                 90
    Rio Branco   Acre    Outubro         21°         33°                171
    Rio Branco   Acre   Novembro         21°         32°                221
    Rio Branco   Acre   Dezembro         21°         31°                265

