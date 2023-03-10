def parse_patent(html_code, number_patent):
    """Функция собирает всю необходимую информацию о патенте с html-кода.

    Args:
        html_code (lxml): html-код страницы патента
        number_patent (str): номер патента, который сейчас парсится

    Returns:
        list: [
                number - Номер патента,
                date - дата подачи заявки,
                quotes - список цитированных в отчёте документов,
                authors - авторы,
                patent_owner - патентообладатель,
                mpk - МПК,
                spk - СПК,
                country - страна,
                type_of_document - тип документа,
                title - название патента,
                abstract - реферат,
                patent_claims - формула патента,
                patent_description - описание патента,
                sources_of_information - источники информации,
                ]

    """

    if html_code.text == "Документ с данным номером отсутствует":
        data = [""] * 14
        data[0] = number_patent
        return (data, True)

    try:
        keys_data_1 = (
            html_code.find("table", id="bib").find("tr").findAll("td")[0].findAll("p")
        )
        keys_data_2 = (
            html_code.find("table", id="bib").find("tr").findAll("td")[1].findAll("p")
        )

        list_date = [i for i in keys_data_1 if "(21)(22)" in i.text]
        if list_date:
            date = list_date[0].find("b").text.split(", ")[-1]  # Дата подачи заявки
        else:
            date = []

        list_quotes = [i for i in keys_data_1 if "(56)" in i.text]
        if list_quotes:
            quotes = (
                list_quotes[0].find("b").text.split(". ")
            )  # Список документов, цитированных в отчете о поиске
        else:
            quotes = []

        list_authors = [i for i in keys_data_2 if "(72)" in i.text]
        if list_authors:
            authors = list_authors[0].find("b").text[1:].split(",")  # Автор(ы)
        else:
            authors = []

        list_patent_owner = [i for i in keys_data_2 if "(73)" in i.text]
        if list_patent_owner:
            patent_owner = keys_data_2[1].find("b").text[1:]  # Патентообладатель(и)
        else:
            patent_owner = []

        keys_data_3 = html_code.find("table", class_="tp").findAll("tr")
        mpk = [
            " ".join(i.text[1:-1].split())
            for i in keys_data_3[3].find("div").find("ul").findAll("li")
        ]  # МПК
        try:
            spk = [
                " ".join(i.text[1:-1].split())
                for i in keys_data_3[5].find("div").find("ul").findAll("li")
            ]  # СПК
        except AttributeError:
            spk = [keys_data_3[5].text]

        keys_data_4 = html_code.find("table", class_="tp").findAll(
            "div", class_="topfield2"
        )
        country = keys_data_4[0].text  # Страна
        number = keys_data_4[1].text[1:-1].replace(" ", "")  # Номер патента
        type_of_document = keys_data_4[2].text  # Тип документа

        title = " ".join(
            html_code.find("p", id="B542").text.split()[1:]
        )  # Название патента
        abstract = (
            html_code.find("div", id="Abs").findAll("p")[1].text[:-1]
        )  # Реферат патента

        ind_abstract = [
            ind for ind, i in enumerate(html_code.findAll("p")) if "(57)" in i.text
        ][
            0
        ]  # Индекс реферата

        trash = set(
            [
                "",
                " ",
                "  ",
                "\n",
                "\n,",
                "\n, ",
                "\n\n",
                "\n\n,",
                "\n\n, ",
                "\n\n\n",
                "\n\n\n,",
                "\n\n\n ",
                "\n\n\n, ",
                "\n\n\n\n",
            ]
        )  # Возможный мусор
        all_text = [
            i.text
            for i in html_code.findAll("p")[ind_abstract + 2 :]
            if not (i.text in trash)
        ]  # Весь патент

        ind_source_of_inf = [
            ind for ind, i in enumerate(all_text) if "Источники информации" in i
        ]  # Индекс "Источники информации"
        ind_patent_claims = [
            ind for ind, i in enumerate(all_text) if "Формула изобретения" in i
        ][
            0
        ]  # Индекс "Формула патента"

        if ind_source_of_inf:
            patent_description = all_text[: ind_source_of_inf[0]]  # Описание патента
            source_of_information = all_text[
                ind_source_of_inf[0] + 1 : ind_patent_claims
            ]  # Источники информации
        else:
            patent_description = all_text[:ind_patent_claims]
            source_of_information = []  # Источники информации

        ind_notification = [
            ind for ind, i in enumerate(all_text) if "ИЗВЕЩЕНИЯ" in i
        ]  # Индекс "ИЗВЕЩЕНИЯ
        if ind_notification:
            patent_claims = all_text[
                ind_patent_claims + 1 : ind_notification[0]
            ]  # Формула патента
        else:
            patent_claims = all_text[ind_patent_claims + 1 :]  # Формула патента

        return (
            [
                number,
                date,
                quotes,
                authors,
                patent_owner,
                mpk,
                spk,
                country,
                type_of_document,
                title,
                abstract,
                " ".join(patent_claims),
                " ".join(patent_description),
                source_of_information,
            ],
            True,
        )
    except:
        data = [""] * 14
        data[0] = number_patent
        return (data, False)
