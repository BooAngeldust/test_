import urllib.request
import json

from src.libs.text import ParseToUrl


class Request:
    response_link = ""

    @staticmethod
    def __Request(request_link : str) -> dict:
        try:
            # Make request
            urllib.request.urlopen(request_link)

            # Collect response
            raw_response = urllib.request.urlopen(Request.response_link)
            response = json.loads(raw_response.read())
            
        except:
            raise Exception("Cannot fetch data, try again later.")


        return response

    @staticmethod
    def MapInfo(map_name : str, player : str) -> dict:
        if player == None or '':
            request_link = f""
        else:
            player = ParseToUrl(player)
            request_link = f""

        return Request.__Request(request_link)

    @staticmethod
    def PlayerInfo(player : str) -> dict:
        player = ParseToUrl(player)
        request_link = f""

        return Request.__Request(request_link)
        
    @staticmethod
    def PointsInfo(player : str) -> dict:
        player = ParseToUrl(player)
        request_link = f""

        return Request.__Request(request_link)

    @staticmethod
    def UnfinishedInfo(player : str, diff : str) -> dict:
        player = ParseToUrl(player)
        request_link = f""

        return Request.__Request(request_link)




