from app.parser import parse_page

def test_parse_page_basic():
    html = """
    <tr class='hl-tr'>
        <td></td>
        <td><a class='torTopic'>Test Movie / 2024</a></td>
        <td></td>
        <td>
            <p></p>
            <p>1,234</p>
        </td>
    </tr>
    """
    result = parse_page(html)
    assert result == [("Test Movie", 1234)]

def test_parse_page_empty():
    html = "<html></html>"
    result = parse_page(html)
    assert result == []

def test_parse_page_broken_row():
    html = """
    <tr class='hl-tr'>
        <td>broken</td>
    </tr>
    """
    result = parse_page(html)
    assert result == []
