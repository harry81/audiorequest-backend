from naver_api.naver_search import Naver
from joonggonara.models import Joonggonara


naver = Naver()


def fetch_joonggonara():
    fetches = naver.search(clubid=10050146)
    for ele in fetches:
        jn = Joonggonara(**ele)
        jn.save()

    return fetches
