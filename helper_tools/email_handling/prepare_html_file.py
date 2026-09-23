

import bs4


async def prepare_html_file(
        link:str|None, user_email:str, file_path:str, reason:str,
        user_name:str|None=None
) -> str:

    """
    prepares the html file for email sending\n

    attributes:\n
    1.link ; either for password reset or account activation\n
    2. user_email\n
    3. file_path ; either for password reset or account activation\n
    """
    
    with open(file_path, "r") as file:
        html_content = file.read()

    soup = bs4.BeautifulSoup(html_content, "lxml")
    
    if reason == "reset_password" and link:
        reset_password_anchor = soup.find("a", id="reset-password-anchor")
        if reset_password_anchor:
            reset_password_anchor.string = link

        reset_password_anchor_href = soup.find("a", id="reset-password-anchor-href")
        if reset_password_anchor_href and link:
            reset_password_anchor_href.attrs["href"] = link

    elif reason == "activate_account":
        anchour = soup.find("a")
        user_email_div = soup.find("div", id="user-email-div")

        if anchour and user_email_div and link:
            anchour.attrs["href"] = link
            user_email_div.string = user_email

    elif reason == "send_refferal_link":
        referal_link = soup.find("a", id="referal_link")
        referal_link_with_txt = soup.find("a", id="referal_link_with_txt")
        
        if referal_link and link:
            referal_link.attrs["href"] = link
            
        if referal_link_with_txt and link:
            referal_link_with_txt.attrs["href"] = link
            referal_link_with_txt.string = link
    
    elif reason == "notification_email":
        
        #fails for tags burried deep in the file
        #username = soup.find("strong", id="username")
        #if username and user_name:
        #    username.string = user_name

        html_str = str(soup)
        if user_name:
            html_str = html_str.replace("{{ username }}", user_name)
            html_str = html_str.replace("{{ username}}", user_name)
            html_str = html_str.replace("{{username }}", user_name)
            html_str = html_str.replace("{{username}}", user_name)

        soup_updated = bs4.BeautifulSoup(html_str, "lxml")
        

        anchor = soup_updated.find("a")
        if anchor and link:
            anchor.attrs["href"] = link

        return str(soup_updated)
    else:

        return ""

    #with open("assets/_activate_account.html", "w") as file:
    #    file.write(str(soup))

    #return "assets/_activate_account.html"

    return str(soup)