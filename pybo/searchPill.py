from urllib.parse import urlencode, unquote, quote_plus
import requests
from bs4 import BeautifulSoup



def search():
    serviceKey = "8/bnxiQS+6+cZaLNhKmIRXawXVN8vYxJh23R3gZDCnHi0fzQuzUuY2XeXsibxBc6rt4h9iuZfXkP4/65n1eyrA=="

    pillName = []
    howToConsume = []
    efficacy = []
    preservation = []
    intake = []
    url = "http://apis.data.go.kr/1471000/HtfsTrgetInfoService01/getHtfsInfoList01"
    returnType = "xml"
    numOfRows="3"
    pageNo="5"
    ver="1.0"

    # prdlst_nm = pillname
    predlst_nm = ''
    bssh_nm=''

    queryParams = '?' + urlencode({ quote_plus('ServiceKey') : serviceKey, quote_plus('returnType') : returnType, quote_plus('numOfRows') : numOfRows, quote_plus('pageNo') : pageNo, quote_plus('prdlst_nm') : prdlst_nm, quote_plus('bssh_nm') : bssh_nm, quote_plus('ver') : ver })
    res = requests.get(url + queryParams)
    xml = res.text
    soup = BeautifulSoup(xml, 'html.parser')
    for tag in soup.find_all('PRDLST_NM'):
        pillName.append(tag.text)
    for tag in soup.find_all('NTK_MTHD'):
        howToConsume.append(tag.text)
    for tag in soup.find.all('PRIMARY_FNCLTY'):
        efficacy.append(tag.text)
    for tag in soup.find.all('CSTDY_MTHD'):
        preservation.append(tag.text)
    for tag in soup.find.all('IFTKN_ATNT_MATR_CN'):
        intake.append(tag.text)
    res = dict(zip(pillName, howToConsume, efficacy, preservation, intake))
    return res

