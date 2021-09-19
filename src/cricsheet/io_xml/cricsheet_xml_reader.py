import os
import xmltodict
from cricsheet.io_xml.models import Scoresheet, Match, Team, Competition
from cricsheet.io_xml.models import Player, Umpire, Innings, Delivery, Wicket
from cricsheet.io_xml.parsers.scoresheet_info import ScoresheetInfoParser
from cricsheet.io_xml.parsers.match import MatchParser
from cricsheet.io_xml.parsers.innings import InningsParser
from cricsheet.io_xml.parsers.delivery import DeliveryParser
from cricsheet.io_xml.parsers.wicket import WicketParser

ENSURE_LIST = lambda x: [x] if not isinstance(x, list) else x


class CricsheetXMLReader(object):
    def __init__(self):
        pass

    def get_objects_from_directory(self, directory):
        objects = list()
        i = 0
        for index in os.listdir(directory):
            for filename in os.listdir("/".join([directory, index])):
                match_id = filename.split(".")[0]
                i += 1
                print(f"Parsing match #{i}, with id: {match_id}")
                with open("/".join([directory, index, filename]), "r") as stream:
                    raw = xmltodict.parse(stream.read())["cricsheet"]

                scoresheet_info_parser = ScoresheetInfoParser(match_id)
                objects.append(Scoresheet(**scoresheet_info_parser.parse(raw["meta"])))
                match_parser = MatchParser(match_id)
                objects.append(Match(**match_parser.parse(raw["info"])))

                for innings in ENSURE_LIST(raw["innings"]["inning"]):
                    innings_number = innings["inningsNumber"]
                    innings_parser = InningsParser(match_id, innings_number)
                    objects.append(Innings(**innings_parser.parse(innings)))

                    for delivery in ENSURE_LIST(innings["deliveries"]["delivery"]):
                        over_number, ball_number = delivery["over"], delivery["ball"]
                        delivery_parser = DeliveryParser(
                            match_id, innings_number, over_number, ball_number
                        )
                        objects.append(Delivery(**delivery_parser.parse(delivery)))

                        if "wickets" in delivery:
                            for wicket in ENSURE_LIST(delivery["wickets"]["wicket"]):
                                wicket_parser = WicketParser(
                                    match_id, innings_number, over_number, ball_number
                                )
                                objects.append(Wicket(**wicket_parser.parse(wicket)))
        return objects
