# from bs4 import BeautifulSoup as bs
# from weasyprint import HTML
# from twocaptcha import TwoCaptcha
#
#
# def create_pdf(cnpj, emissao, tipo, img_src):
#     with open("../static/teste.html", "r", encoding="utf-8") as file:
#         data = file.read()
#
#     soup = bs(data, "html.parser")
#
#     p1 = soup.find("p", attrs={"class": "cnpj"})
#     p3 = soup.find("p", attrs={"class": "emissao"})
#     p4 = soup.find("p", attrs={"class": "tipo"})
#
#     for i in p1.find_all(string=True):
#         if "{{cnpj}}" in i:
#             i.replace_with(i.replace("{{cnpj}}", cnpj))
#
#     for i in p3.find_all(string=True):
#         if "{{emissao}}" in i:
#             i.replace_with(i.replace("{{emissao}}", emissao))
#
#     for i in p4.find_all(string=True):
#         if "{{tipo}}" in i:
#             i.replace_with(i.replace("{{tipo}}", tipo))
#
#     soup.find("img", attrs={"class": "status-image"})["src"] = img_src
#
#     return HTML(string=str(soup)).write_pdf()
#
