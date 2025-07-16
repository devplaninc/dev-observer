from bs4 import BeautifulSoup, Comment


def clean_html_for_llm(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "aside", "form", "noscript"]):
        tag.decompose()

    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    # junk_keywords = ["sidebar", "popup", "ad", "sponsor", "subscribe", "cookie"]
    # for el in soup.find_all(True):  # True = all tags
    #     if el.attrs and any(attr in el.attrs for attr in ["class", "id"]):
    #         class_id_values = " ".join(el.get("class", []) + [el.get("id", "")])
    #         if any(word in class_id_values.lower() for word in junk_keywords):
    #             el.decompose()
    #
    # attrs_to_clear = ["class", "style"]
    # for tag in soup.find_all(True):
    #     if tag.attrs:
    #         for attr in attrs_to_clear:
    #             tag.attrs.pop(attr, None)

    clean = soup

    # Minimize whitespace
    return clean.prettify()
