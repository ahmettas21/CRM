import csv
import io
import bs4

def parse_aqua_file(file_content, filename):
    """
    Parses Aqua Ticket export files.
    Returns a list of dictionaries where keys are column headers.
    Hanldes both true CSVs and HTML-Tables disguised as .xls.
    """
    data = []
    
    if filename.endswith(".xls") or filename.endswith(".html"):
        # Parse as HTML Table
        soup = bs4.BeautifulSoup(file_content, "html.parser")
        table = soup.find("table")
        if not table:
            raise ValueError("No HTML table found in the provided .xls file.")
        
        rows = table.find_all("tr")
        if not rows:
            return []
        
        # Define the headers based on the first row with <th> or <td>
        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        
        # Exclude summary rows at the bottom (they usually have negative PNR)
        for row in rows[1:]:
            cells = row.find_all("td")
            if not cells:
                continue
            
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Ensure length matches headers
            if len(row_data) != len(headers):
                # pad or cut
                row_data = row_data[:len(headers)] + [""] * (len(headers) - len(row_data))
                
            row_dict = dict(zip(headers, row_data))
            
            # Check for summary row (negative PNR or summary text)
            pnr_val = row_dict.get("Pnr.No", "")
            if pnr_val.startswith("-") or pnr_val == "Genel Toplam":
                continue
                
            data.append(row_dict)
            
    elif filename.endswith(".csv"):
        if isinstance(file_content, bytes):
            try:
                content_str = file_content.decode("utf-8-sig")
            except UnicodeDecodeError:
                try:
                    content_str = file_content.decode("latin-1")
                except Exception:
                    content_str = file_content.decode("utf-8", errors="ignore")
        else:
            content_str = file_content
            
        reader = csv.DictReader(io.StringIO(content_str), delimiter=";")
        if not reader.fieldnames or len(reader.fieldnames) < 5:
            # Maybe comma separated
            reader = csv.DictReader(io.StringIO(content_str), delimiter=",")
            
        for row_dict in reader:
             row_dict = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row_dict.items() if k}
             
             pnr_val = row_dict.get("Pnr.No", "")
             if str(pnr_val).startswith("-") or pnr_val == "Genel Toplam":
                 continue
             data.append(row_dict)
    else:
        raise ValueError("Unsupported file format. Please upload .xls (HTML) or .csv")
        
    return data
