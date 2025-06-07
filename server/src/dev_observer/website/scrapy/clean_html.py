from bs4 import BeautifulSoup, Comment


def clean_html_for_llm(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove junk tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    # Remove elements with junky class/id names (ads, popups, sidebars)
    junk_keywords = ["sidebar", "popup", "ad", "sponsor", "subscribe", "footer", "header", "cookie"]
    for el in soup.find_all(True):  # True = all tags
        if el.attrs and any(attr in el.attrs for attr in ["class", "id"]):
            class_id_values = " ".join(el.get("class", []) + [el.get("id", "")])
            if any(word in class_id_values.lower() for word in junk_keywords):
                el.decompose()

    # Strip all attributes from remaining tags
    for tag in soup.find_all(True):
        tag.attrs = {}

    # Optionally restrict to body content only
    if soup.body:
        clean = soup.body
    else:
        clean = soup

    # Minimize whitespace
    return clean.prettify()
