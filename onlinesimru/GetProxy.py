from onlinesimru.api import Api


class GetProxy(Api):
    def tariffs(self):
        return self._get(f"/proxy/tariffs", {"country": "all"})

    def get(
        self,
        cl: str = "days",
        type: str = "private",
        connect: str = "https",
        count: int = 1,
        operator: str = None,
        country: int = 7,
        city: str = "any",
        port_count: int = 1,
        session: bool = True,
    ):
        return self._get(
            f"/proxy/getProxy",
            {
                "class": cl,
                "type": type,
                "connect": connect,
                "count": count,
                "operator": operator,
                "country": country,
                "city": city,
                "port_count": port_count,
                "session": session,
            },
        )["item"]

    def state(self, orderby: str = "ASC"):
        return self._get(f"/proxy/getState", {"orderby": orderby})["list"]

    def stateOne(self, tzid: int):
        return self._get(f"/proxy/getState", {"tzid": tzid})["list"][0]

    def changeIp(self, tzid: int):
        return self._get(f"/proxy/changeIp", {"tzid": tzid})

    def changeType(self, tzid: int):
        return self._get(f"/proxy/changeType", {"tzid": tzid})["connect_type"]

    def setComment(self, tzid: int, comment: str = ""):
        return self._get(f"/proxy/setComment", {"tzid": tzid, "comment": comment})
