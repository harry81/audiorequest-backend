from naver_api.naver_search import Naver
from joonggonara.models import Joonggonara


naver = Naver()


def fetch_joonggonara(clubid=10050146):
    fetches = naver.search(clubid=clubid)
    for ele in fetches:
        jn = Joonggonara(**ele)
        jn.save()

    return fetches
